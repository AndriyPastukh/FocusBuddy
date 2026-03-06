from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QGridLayout, QScrollArea, QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, timedelta

# Matplotlib integration
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class OverviewWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.api = main_window.api
        
        # Data cache
        self.all_sessions = [] 
        self.all_tasks = []
        
        # Scroll Area Setup
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { width: 12px; background: #F0F0F0; border-radius: 6px; }
            QScrollBar::handle:vertical { background: #C0C0C0; border-radius: 6px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        
        self.content = QWidget()
        self.content.setStyleSheet("background-color: transparent;")
        
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(20, 20, 30, 50)
        self.layout.setSpacing(30)
        
        # Header & Filter
        header_layout = QHBoxLayout()
        
        lbl_title = QLabel("ANALYTICS DASHBOARD")
        lbl_title.setFont(QFont("Oswald", 20, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #383838;")
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Last 7 Days", "This Month", "Today", "Yesterday", "All Time"])
        self.filter_combo.setFixedWidth(180)
        self.filter_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.filter_combo.setStyleSheet("""
            QComboBox {
                padding: 8px; border: 2px solid #E0E0E0; border-radius: 8px;
                font-weight: bold; color: #555; background: white; font-size: 14px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox:hover { border: 2px solid #B0B0B0; }
        """)
        self.filter_combo.currentIndexChanged.connect(self.recalc_stats)
        
        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Period:", styleSheet="color:#666; font-weight:bold; font-size: 14px;"))
        header_layout.addWidget(self.filter_combo)
        
        self.layout.addLayout(header_layout)
        
        # KPI Section
        self.kpi_layout = QHBoxLayout()
        self.kpi_layout.setSpacing(20)
        
        self.kpi_xp = self.create_kpi_card("EARNED XP", "0", "#6C5CE7")
        self.kpi_hours = self.create_kpi_card("FOCUS HOURS", "0.0", "#E0C068")
        self.kpi_sessions = self.create_kpi_card("SESSIONS", "0", "#00B894")
        self.kpi_tasks_done = self.create_kpi_card("TASKS DONE", "0", "#FF7675")
        
        self.kpi_layout.addWidget(self.kpi_xp)
        self.kpi_layout.addWidget(self.kpi_hours)
        self.kpi_layout.addWidget(self.kpi_sessions)
        self.kpi_layout.addWidget(self.kpi_tasks_done)
        self.layout.addLayout(self.kpi_layout)
        
        # Charts Grid
        grid_charts = QGridLayout()
        grid_charts.setSpacing(25)
        
        # Row 1
        self.chart_activity = MplCanvas(self, width=5, height=4, dpi=100)
        grid_charts.addWidget(self.create_chart_card("FOCUS TIME (MINUTES)", self.chart_activity), 0, 0)
        
        self.chart_tasks = MplCanvas(self, width=5, height=4, dpi=100)
        grid_charts.addWidget(self.create_chart_card("COMPLETED TASKS", self.chart_tasks), 0, 1)

        # Row 2
        self.chart_habits = MplCanvas(self, width=5, height=4, dpi=100)
        grid_charts.addWidget(self.create_chart_card("HABIT CONSISTENCY (THIS MONTH)", self.chart_habits), 1, 0)

        self.pie_prio = MplCanvas(self, width=5, height=4, dpi=100)
        grid_charts.addWidget(self.create_chart_card("TASKS BY PRIORITY", self.pie_prio), 1, 1)
        
        # Row 3
        self.pie_cat = MplCanvas(self, width=5, height=4, dpi=100)
        grid_charts.addWidget(self.create_chart_card("FOCUS BY CATEGORY", self.pie_cat), 2, 0)
        
        self.pie_stat = MplCanvas(self, width=5, height=4, dpi=100)
        grid_charts.addWidget(self.create_chart_card("TASKS BY STATUS", self.pie_stat), 2, 1)
        
        grid_charts.setColumnStretch(0, 1)
        grid_charts.setColumnStretch(1, 1)
        
        self.layout.addLayout(grid_charts)
        self.layout.addStretch()
        
        self.scroll.setWidget(self.content)
        
        main_l = QVBoxLayout(self)
        main_l.setContentsMargins(0,0,0,0)
        main_l.addWidget(self.scroll)

    def refresh_overview(self):
        """Fetch all data and update stats."""
        self.all_sessions = self.api.get_sessions() 
        self.all_tasks = self.api.get_tasks("all")
        
        self.recalc_stats() 

        # Static charts (current state)
        self.update_pie_chart(self.pie_prio, self.api.get_chart_data("priority"))
        self.update_pie_chart(self.pie_cat, self.api.get_chart_data("category"))
        self.update_pie_chart(self.pie_stat, self.api.get_chart_data("status"))
        
        # Habits trend
        month_str = datetime.now().strftime("%Y-%m")
        habit_stats = self.api.get_habit_score_stats(month_str)
        self.update_habit_chart(habit_stats)

    def recalc_stats(self):
        filter_mode = self.filter_combo.currentText()
        today = datetime.now().date()
        
        # 1. Generate date skeleton (to fill missing days with 0)
        date_range = []
        if filter_mode == "Today":
            date_range = [today]
        elif filter_mode == "Yesterday":
            date_range = [today - timedelta(days=1)]
        elif filter_mode == "Last 7 Days":
            date_range = [today - timedelta(days=i) for i in range(6, -1, -1)]
        elif filter_mode == "This Month":
            first_day = today.replace(day=1)
            delta = (today - first_day).days + 1
            date_range = [first_day + timedelta(days=i) for i in range(delta)]
        else: 
            # All Time - no skeleton needed
            date_range = []

        # Initialize maps with 0
        focus_map = {d.strftime("%m-%d"): 0 for d in date_range}
        tasks_map = {d.strftime("%m-%d"): 0 for d in date_range}
        
        # KPI Variables
        filtered_xp = 0
        filtered_mins = 0
        filtered_sessions = 0
        filtered_tasks_done = 0

        # 2. Process Sessions
        for s in self.all_sessions:
            try:
                s_date_str = s['start_time'].split(' ')[0]
                s_date_obj = datetime.strptime(s_date_str, "%Y-%m-%d").date()
                
                # Check date range
                include = False
                if filter_mode == "All Time": include = True
                elif s_date_obj in date_range: include = True
                
                if include:
                    dur = int(s['duration'])
                    filtered_xp += int(s['xp_earned'])
                    filtered_mins += dur
                    filtered_sessions += 1
                    
                    k = s_date_obj.strftime("%m-%d")
                    focus_map[k] = focus_map.get(k, 0) + dur
            except: continue

        # 3. Process Tasks
        for t in self.all_tasks:
            try:
                if str(t.get('is_completed')) == "1":
                    t_date_str = t.get('todo_date', '') 
                    if not t_date_str: continue
                    t_date_obj = datetime.strptime(t_date_str, "%Y-%m-%d").date()
                    
                    include = False
                    if filter_mode == "All Time": include = True
                    elif t_date_obj in date_range: include = True
                    
                    if include:
                        filtered_tasks_done += 1
                        k = t_date_obj.strftime("%m-%d")
                        tasks_map[k] = tasks_map.get(k, 0) + 1
            except: continue

        # 4. Update KPI
        self.kpi_xp.findChild(QLabel, "val").setText(str(filtered_xp))
        self.kpi_hours.findChild(QLabel, "val").setText(str(round(filtered_mins/60, 1)))
        self.kpi_sessions.findChild(QLabel, "val").setText(str(filtered_sessions))
        self.kpi_tasks_done.findChild(QLabel, "val").setText(str(filtered_tasks_done))
        
        # 5. Update Charts
        self.update_bar_chart(self.chart_activity, focus_map, "Minutes", "#6C5CE7")
        self.update_bar_chart(self.chart_tasks, tasks_map, "Tasks", "#FF7675")

    def update_bar_chart(self, canvas, data_map, label, color):
        canvas.axes.cla()
        
        # Sort chronologically
        dates = sorted(data_map.keys())
        values = [data_map[d] for d in dates]
        
        if not dates:
            canvas.axes.text(0.5, 0.5, "No Data", ha='center', color="#888")
        else:
            bars = canvas.axes.bar(dates, values, color=color, alpha=0.75, width=0.5, zorder=3)
            canvas.axes.grid(axis='y', linestyle='--', alpha=0.3, zorder=0)
            
            # Annotations
            for rect in bars:
                height = rect.get_height()
                canvas.axes.annotate(f'{height}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom', fontsize=8, color='#555')

        canvas.axes.set_title(label, fontsize=10, color='#666', pad=10)
        
        # Rotation if many dates
        rotation = 45 if len(dates) > 7 else 0
        canvas.axes.tick_params(axis='x', rotation=rotation, labelsize=8)
        
        canvas.axes.spines['top'].set_visible(False)
        canvas.axes.spines['right'].set_visible(False)
        canvas.draw()

    def update_habit_chart(self, stats):
        self.chart_habits.axes.cla()
        
        dates = []
        scores = []
        
        if stats:
            for s in stats:
                try:
                    day = s['date'][8:] 
                    dates.append(day)
                    scores.append(int(s['total_score']))
                except: pass
        
        if not dates:
            self.chart_habits.axes.text(0.5, 0.5, "No Habit Data", ha='center', color="#888")
        else:
            self.chart_habits.axes.plot(dates, scores, marker='o', color='#00B894', linewidth=2, markersize=5)
            self.chart_habits.axes.fill_between(dates, scores, color='#00B894', alpha=0.1)
            self.chart_habits.axes.grid(True, linestyle='--', alpha=0.3)
            
        self.chart_habits.axes.set_title("Habit Score Trend", fontsize=10, color='#666')
        self.chart_habits.axes.tick_params(labelsize=8)
        self.chart_habits.axes.spines['top'].set_visible(False)
        self.chart_habits.axes.spines['right'].set_visible(False)
        self.chart_habits.draw()

    def update_pie_chart(self, canvas, data):
        canvas.axes.cla()
        labels = []; sizes = []
        for d in data:
            try: labels.append(d['name']); sizes.append(int(d['count']))
            except: pass
        
        colors = ['#88A0A8', '#E0C068', '#D45D5D', '#800080', '#7FB06F', '#6C5CE7'] 
        
        if not sizes or sum(sizes) == 0:
            canvas.axes.text(0.5, 0.5, "No Data", ha='center', color="#AAA")
        else:
            wedges, texts, autotexts = canvas.axes.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%', startangle=90, textprops={'fontsize': 8})
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_weight('bold')
        
        canvas.draw()

    # --- UI HELPERS ---
    def create_kpi_card(self, title, val, color):
        frame = QFrame()
        frame.setObjectName("Card")
        frame.setFixedHeight(120)
        frame.setStyleSheet(f"""
            QFrame#Card {{ 
                background-color: white; 
                border-radius: 12px; 
                border-left: 6px solid {color};
                border-top: 1px solid #E0E0E0; border-right: 1px solid #E0E0E0; border-bottom: 1px solid #E0E0E0;
            }}
        """)
        l = QVBoxLayout(frame)
        l.setContentsMargins(20, 15, 20, 15)
        
        lbl_t = QLabel(title)
        lbl_t.setFont(QFont("Oswald", 11, QFont.Weight.DemiBold))
        lbl_t.setStyleSheet("color: #888; letter-spacing: 0.5px;")
        
        lbl_v = QLabel(val)
        lbl_v.setObjectName("val") 
        lbl_v.setFont(QFont("Oswald", 28, QFont.Weight.Bold))
        lbl_v.setStyleSheet("color: #383838;")
        
        l.addWidget(lbl_t)
        l.addWidget(lbl_v)
        return frame

    def create_chart_card(self, title, chart_widget):
        frame = QFrame()
        frame.setObjectName("Card")
        frame.setMinimumHeight(500) 
        frame.setStyleSheet("""
            QFrame#Card {
                background-color: white; 
                border-radius: 12px; 
                border: 1px solid #E0E0E0;
            }
        """)
        
        l = QVBoxLayout(frame)
        l.setContentsMargins(15, 20, 15, 15)
        
        lbl = QLabel(title)
        lbl.setFont(QFont("Oswald", 12, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #555; margin-bottom: 10px;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        l.addWidget(lbl)
        l.addWidget(chart_widget, 1)
        return frame

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        fig.subplots_adjust(left=0.08, bottom=0.15, right=0.95, top=0.90)
        super(MplCanvas, self).__init__(fig)