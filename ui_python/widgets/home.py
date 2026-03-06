from datetime import datetime
from calendar import monthrange 
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QGridLayout, QScrollArea, QPushButton, QCheckBox, QTabWidget, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QIcon

# Matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class HomeWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.api = main_window.api
        
        # Scroll Area Setup
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        content = QWidget()
        self.layout = QVBoxLayout(content)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # === 1. HEADER ===
        welcome_layout = QHBoxLayout()
        v_w = QVBoxLayout()
        
        self.lbl_welcome = QLabel("Welcome back, FocusBuddy!")
        self.lbl_welcome.setFont(QFont("Oswald", 22, QFont.Weight.Bold))
        self.lbl_welcome.setStyleSheet("color: #383838;")
        
        self.lbl_date = QLabel(datetime.now().strftime("%A, %d %B %Y").upper())
        self.lbl_date.setFont(QFont("Segoe UI", 11))
        self.lbl_date.setStyleSheet("color: #888; font-weight: bold; letter-spacing: 1px;")
        
        v_w.addWidget(self.lbl_welcome)
        v_w.addWidget(self.lbl_date)
        welcome_layout.addLayout(v_w)
        welcome_layout.addStretch()
        
        # Shortcuts
        if hasattr(self.main_window, 'planner_widget'):
            btn_add = self.create_shortcut_btn("+ TASK", "#383838", self.main_window.planner_widget.add_task_dialog)
            welcome_layout.addWidget(btn_add)
            
        btn_focus = self.create_shortcut_btn("⚡ FOCUS", "#6C5CE7", lambda: self.main_window.tabs.setCurrentIndex(2))
        welcome_layout.addWidget(btn_focus)
        
        self.layout.addLayout(welcome_layout)
        
        # === 2. KPI CARDS ===
        self.kpi_layout = QHBoxLayout()
        self.kpi_xp = self.create_kpi_card("TOTAL XP", "0", "#6C5CE7")
        self.kpi_hours = self.create_kpi_card("FOCUS HOURS", "0.0", "#E0C068")
        self.kpi_tasks = self.create_kpi_card("TASKS DONE", "0", "#7FB06F")
        self.kpi_layout.addWidget(self.kpi_xp)
        self.kpi_layout.addWidget(self.kpi_hours)
        self.kpi_layout.addWidget(self.kpi_tasks)
        self.layout.addLayout(self.kpi_layout)
        
        # === 3. MAIN GRID ===
        grid = QGridLayout()
        grid.setSpacing(20)
        
        # --- LEFT COLUMN (CHARTS) ---
        
        # 1. Habit Trend
        self.habit_canvas = MplCanvas(width=4, height=3, dpi=90)
        self.habit_frame = self.create_chart_card("HABIT TREND (THIS MONTH)", self.habit_canvas)
        grid.addWidget(self.habit_frame, 0, 0)
        
        # 2. Bar Chart
        self.bar_canvas = MplCanvas(width=4, height=3, dpi=90)
        self.bar_frame = self.create_chart_card("WEEKLY ACTIVITY", self.bar_canvas)
        grid.addWidget(self.bar_frame, 1, 0)
        
        # --- RIGHT COLUMN (HABITS & TASKS) ---
        
        # 3. Habits Checklist
        self.habits_frame = QFrame()
        self.habits_frame.setObjectName("Card")
        self.habits_frame.setStyleSheet("#Card { background-color: white; border-radius: 12px; border: 1px solid #E0E0E0; }")
        self.habits_layout = QVBoxLayout(self.habits_frame)
        self.habits_layout.setContentsMargins(20, 20, 20, 20)
        
        h_lbl = QLabel("TODAY'S HABITS")
        h_lbl.setFont(QFont("Oswald", 12, QFont.Weight.Bold))
        h_lbl.setStyleSheet("color: #666; letter-spacing: 1px; margin-bottom: 5px;")
        self.habits_layout.addWidget(h_lbl)
        
        self.habits_container = QVBoxLayout()
        self.habits_layout.addLayout(self.habits_container)
        self.habits_layout.addStretch()
        
        grid.addWidget(self.habits_frame, 0, 1)
        
        # 4. Tasks Tabs
        self.tasks_frame = QFrame()
        self.tasks_frame.setObjectName("Card")
        self.tasks_frame.setStyleSheet("#Card { background-color: white; border-radius: 12px; border: 1px solid #E0E0E0; }")
        
        t_layout = QVBoxLayout(self.tasks_frame)
        t_layout.setContentsMargins(10, 10, 10, 10)
        
        self.task_tabs = QTabWidget()
        self.task_tabs.setStyleSheet("""
            QTabWidget::pane { border: none; }
            QTabBar::tab {
                background: #F4F4F4; color: #888; padding: 6px 12px;
                margin-right: 5px; border-radius: 4px; font-weight: bold; font-size: 11px;
            }
            QTabBar::tab:selected { background: #383838; color: white; }
        """)
        
        self.list_overdue = self.create_task_list()
        self.list_today = self.create_task_list()
        self.list_tomorrow = self.create_task_list()
        
        self.task_tabs.addTab(self.list_overdue, "🔥 OVERDUE")
        self.task_tabs.addTab(self.list_today, "📅 TODAY")
        self.task_tabs.addTab(self.list_tomorrow, "🚀 TOMORROW")
        self.task_tabs.setCurrentIndex(1)
        
        t_layout.addWidget(self.task_tabs)
        grid.addWidget(self.tasks_frame, 1, 1)
        
        # Ratios
        grid.setColumnStretch(0, 3) 
        grid.setColumnStretch(1, 2) 
        
        self.layout.addLayout(grid)
        self.layout.addStretch()
        
        scroll.setWidget(content)
        main_l = QVBoxLayout(self)
        main_l.setContentsMargins(0,0,0,0)
        main_l.addWidget(scroll)

    # --- UI HELPERS ---
    def create_task_list(self):
        lst = QListWidget()
        lst.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        lst.setStyleSheet("""
            QListWidget { border: none; background: transparent; }
            QListWidget::item { padding: 5px; border-bottom: 1px solid #F0F0F0; }
            QListWidget::item:hover { background: #FAFAF9; }
        """)
        return lst

    # --- LOGIC ---
    
    def refresh_with_payload(self, data):
        # A. Update KPI
        dashboard = data.get('dashboard', {})
        self.kpi_tasks.findChild(QLabel, "val").setText(str(dashboard.get('done_total', 0)))
        
        user_list = data.get('user', [])
        if user_list:
            user = user_list[0]
            self.lbl_welcome.setText(f"Welcome back, {user.get('username', 'Hero')}!")
            self.kpi_xp.findChild(QLabel, "val").setText(str(user.get('xp', 0)))
            try:
                mins = int(user.get('total_minutes', 0))
                self.kpi_hours.findChild(QLabel, "val").setText(str(round(mins/60, 1)))
            except: pass

        # B. Charts
        self.update_bar_chart(data.get('weekly_stats', []))
        
        current_month = datetime.now().strftime("%Y-%m")
        habit_stats = self.api.get_habit_score_stats(current_month)
        self.update_habit_trend_chart(habit_stats)
        
        # C. Habits & Tasks
        self.render_quick_habits(data.get('habits', []))
        self.render_home_tasks(
            data.get('overdue', []), 
            data.get('today', []), 
            data.get('tomorrow', [])
        )

    def refresh_home(self):
        payload = self.api.get_home_payload()
        if payload:
            self.refresh_with_payload(payload)

    def update_habit_trend_chart(self, data):
        self.habit_canvas.axes.cla()
        
        # 1. Get total days in month
        now = datetime.now()
        days_in_month = monthrange(now.year, now.month)[1]
        
        # 2. Parse data
        data_map = {}
        if data:
            for s in data:
                try:
                    day = int(s['date'].split('-')[-1])
                    data_map[day] = int(s['total_score'])
                except: pass
        
        # 3. Generate full data list (fill gaps with 0)
        dates = []
        scores = []
        for day in range(1, days_in_month + 1):
            dates.append(str(day))
            scores.append(data_map.get(day, 0))
        
        # 4. Draw
        if not scores or sum(scores) == 0:
             self.habit_canvas.axes.text(0.5, 0.5, "No Habit Activity", ha='center', color="#AAA")
        else:
            self.habit_canvas.axes.plot(dates, scores, marker='o', color='#FF7675', linewidth=2.5, markersize=4)
            self.habit_canvas.axes.fill_between(dates, scores, color='#FF7675', alpha=0.1)
            
        self.habit_canvas.axes.grid(True, linestyle='--', alpha=0.3)
        self.habit_canvas.axes.spines['top'].set_visible(False)
        self.habit_canvas.axes.spines['right'].set_visible(False)
        
        # Limit x-ticks if crowded
        if len(dates) > 15:
            self.habit_canvas.axes.set_xticks(range(0, len(dates), 3))
            self.habit_canvas.axes.set_xticklabels(dates[::3])
            
        self.habit_canvas.axes.tick_params(axis='both', labelsize=8)
        self.habit_canvas.draw()

    def render_quick_habits(self, habits):
        while self.habits_container.count():
            item = self.habits_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        if not habits:
            lbl = QLabel("No habits created yet.")
            lbl.setStyleSheet("color: #AAA; font-style: italic;")
            self.habits_container.addWidget(lbl)
            return

        day_num = datetime.now().day
        
        for h in habits:
            cb = QCheckBox(h['title'])
            cb.setFont(QFont("Segoe UI", 11))
            cb.setStyleSheet("QCheckBox { padding: 6px; } QCheckBox::indicator { width: 16px; height: 16px; }")
            cb.setCursor(Qt.CursorShape.PointingHandCursor)
            
            is_done = day_num in h['days']
            cb.setChecked(is_done)
            cb.clicked.connect(lambda checked, hid=h['id']: self.toggle_quick_habit(hid))
            self.habits_container.addWidget(cb)

    def render_home_tasks(self, overdue, today, tomorrow):
        def fill_list(list_widget, task_data, is_overdue=False):
            list_widget.clear()
            
            if not task_data or not isinstance(task_data, list):
                item = QListWidgetItem("No tasks. Relax! ☕")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setForeground(QColor("#AAA"))
                list_widget.addItem(item)
                return

            for t in task_data:
                if not isinstance(t, dict): continue

                w = QWidget()
                l = QHBoxLayout(w)
                l.setContentsMargins(5, 2, 5, 2)
                
                btn_done = QPushButton("☐")
                btn_done.setFixedSize(24, 24)
                btn_done.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_done.setStyleSheet("border: none; font-size: 18px; color: #888; text-align: left;")
                btn_done.clicked.connect(lambda ch, tid=t.get('id'): self.quick_complete_task(tid))
                
                lbl_text = QLabel(t.get('title', 'Untitled'))
                lbl_text.setStyleSheet("font-size: 13px; color: #333;")
                if is_overdue:
                    lbl_text.setStyleSheet("font-size: 13px; color: #D45D5D; font-weight: bold;")
                
                color = t.get('c_color') or t.get('color') or '#ccc'
                lbl_cat = QLabel("●")
                lbl_cat.setStyleSheet(f"color: {color}; font-size: 12px;")
                
                l.addWidget(btn_done)
                l.addWidget(lbl_text)
                l.addStretch()
                l.addWidget(lbl_cat)
                
                from PyQt6.QtCore import QSize
                item = QListWidgetItem(list_widget)
                item.setSizeHint(QSize(0, 40))
                list_widget.setItemWidget(item, w)

        fill_list(self.list_overdue, overdue, is_overdue=True)
        fill_list(self.list_today, today)
        fill_list(self.list_tomorrow, tomorrow)
        
        self.task_tabs.setTabText(0, f"🔥 {len(overdue) if isinstance(overdue, list) else 0}")
        self.task_tabs.setTabText(1, f"📅 {len(today) if isinstance(today, list) else 0}")
        self.task_tabs.setTabText(2, f"🚀 {len(tomorrow) if isinstance(tomorrow, list) else 0}")

    def toggle_quick_habit(self, habit_id):
        today_str = datetime.now().strftime("%Y-%m-%d")
        self.api.toggle_habit_date(habit_id, today_str)
        self.main_window.refresh_all()

    def quick_complete_task(self, task_id):
        self.api.complete_task(task_id)
        self.main_window.refresh_all()

    def update_bar_chart(self, data):
        self.bar_canvas.axes.cla()
        dates = []; mins = []
        for d in data:
            try: dates.append(d['date'][5:]); mins.append(int(d['focus_minutes']))
            except: pass
        
        if not dates:
            self.bar_canvas.axes.text(0.5, 0.5, "No Activity", ha='center')
        else:
            self.bar_canvas.axes.plot(dates, mins, marker='o', color='#6C5CE7', linewidth=2, markersize=6)
            self.bar_canvas.axes.fill_between(dates, mins, color='#6C5CE7', alpha=0.1)
        
        self.bar_canvas.axes.set_title("Activity (Last 7 Days)", fontsize=9, color='#666')
        self.bar_canvas.axes.tick_params(axis='both', labelsize=7)
        self.bar_canvas.axes.spines['top'].set_visible(False)
        self.bar_canvas.axes.spines['right'].set_visible(False)
        self.bar_canvas.draw()

    # --- HELPERS ---
    def create_kpi_card(self, title, val, color):
        frame = QFrame()
        frame.setObjectName("Card")
        frame.setStyleSheet(f"""
            QFrame#Card {{ 
                background-color: white; border-radius: 12px; 
                border-left: 5px solid {color}; border: 1px solid #E0E0E0;
            }}
        """)
        l = QVBoxLayout(frame)
        lbl_t = QLabel(title)
        lbl_t.setFont(QFont("Oswald", 9, QFont.Weight.Bold))
        lbl_t.setStyleSheet("color: #888;")
        lbl_v = QLabel(val)
        lbl_v.setObjectName("val")
        lbl_v.setFont(QFont("Oswald", 22, QFont.Weight.Bold))
        lbl_v.setStyleSheet("color: #383838;")
        l.addWidget(lbl_t); l.addWidget(lbl_v)
        return frame

    def create_chart_card(self, title, canvas):
        frame = QFrame()
        frame.setObjectName("Card")
        frame.setStyleSheet("background-color: white; border-radius: 12px; border: 1px solid #E0E0E0;")
        l = QVBoxLayout(frame)
        lbl = QLabel(title)
        lbl.setFont(QFont("Oswald", 10, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #666; margin-bottom: 5px;")
        l.addWidget(lbl); l.addWidget(canvas)
        return frame

    def create_shortcut_btn(self, text, bg_color, callback):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedSize(100, 40)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color}; color: white; 
                border-radius: 20px; font-weight: bold; font-size: 11px;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
        """)
        btn.clicked.connect(callback)
        return btn

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        fig.subplots_adjust(left=0.1, bottom=0.1, right=0.95, top=0.9)
        super(MplCanvas, self).__init__(fig)