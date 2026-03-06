from datetime import datetime, timedelta
import calendar
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QGridLayout, QComboBox, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class CalendarWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.api = main_window.api
        self.lookups = main_window.lookups
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # --- TOP BAR ---
        bar = QFrame()
        bar.setObjectName("Card")
        bar.setFixedHeight(60)
        bar.setStyleSheet("""
            QFrame#Card { 
                background-color: white; 
                border: 1px solid #E0E0E0; 
                border-radius: 8px; 
            }
        """)
        
        bl = QHBoxLayout(bar)
        
        btn_prev = QPushButton("<")
        btn_prev.setFixedSize(40, 30)
        btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_prev.clicked.connect(lambda: self.change_date(-1))
        
        btn_today = QPushButton("Today")
        btn_today.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_today.clicked.connect(self.go_to_today)
        btn_today.setStyleSheet("background: #F0F0F0; border: 1px solid #CCC; border-radius: 4px; font-weight: bold;")
        
        self.lbl_cal_title = QLabel()
        self.lbl_cal_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #383838;")
        self.lbl_cal_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_next = QPushButton(">")
        btn_next.setFixedSize(40, 30)
        btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_next.clicked.connect(lambda: self.change_date(1))
        
        self.view_mode = QComboBox()
        self.view_mode.addItems(["Day", "Week", "Month", "Year"])
        self.view_mode.setCurrentText("Month")
        self.view_mode.currentTextChanged.connect(self.refresh_calendar)
        self.view_mode.setFixedWidth(100)
        
        bl.addWidget(btn_prev)
        bl.addWidget(btn_today)
        bl.addStretch()
        bl.addWidget(self.lbl_cal_title)
        bl.addStretch()
        bl.addWidget(self.view_mode)
        bl.addWidget(btn_next)
        
        layout.addWidget(bar)
        
        # --- CALENDAR AREA ---
        self.cal_area = QWidget()
        self.cal_layout = QVBoxLayout(self.cal_area)
        self.cal_layout.setContentsMargins(0,0,0,0)
        
        layout.addWidget(self.cal_area)
        
        self.cal_date = datetime.now()
        
        self.refresh_calendar()

    def go_to_today(self):
        self.cal_date = datetime.now()
        self.refresh_calendar()

    def change_date(self, delta):
        mode = self.view_mode.currentText()
        if mode == "Day": self.cal_date += timedelta(days=delta)
        elif mode == "Week": self.cal_date += timedelta(weeks=delta)
        elif mode == "Month":
            m = self.cal_date.month + delta
            y = self.cal_date.year
            if m > 12: 
                m = 1; y += 1
            elif m < 1: 
                m = 12; y -= 1
            self.cal_date = self.cal_date.replace(year=y, month=m, day=1)
        elif mode == "Year": 
            self.cal_date = self.cal_date.replace(year=self.cal_date.year + delta)
            
        self.refresh_calendar()

    def refresh_calendar(self):
        while self.cal_layout.count():
            item = self.cal_layout.takeAt(0)
            if item.widget(): 
                item.widget().deleteLater()
        
        mode = self.view_mode.currentText()
        
        if mode == "Day": self.render_day_view()
        elif mode == "Week": self.render_week_view()
        elif mode == "Month": self.render_month_view()
        elif mode == "Year": self.render_year_view()

    # === VIEWS ===

    def render_day_view(self):
        self.lbl_cal_title.setText(self.cal_date.strftime("%A, %d %B %Y").upper())
        day_str = self.cal_date.strftime("%Y-%m-%d")
        month_str = self.cal_date.strftime("%Y-%m")
        
        all_tasks = self.api.get_tasks_by_month(month_str)
        tasks = [t for t in all_tasks if t['todo_date'] == day_str]
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        container = QWidget()
        vl = QVBoxLayout(container)
        vl.setSpacing(10)
        
        if not tasks:
            vl.addWidget(QLabel("No tasks for this day. Enjoy! 🎉", alignment=Qt.AlignmentFlag.AlignCenter))
        else:
            for t in tasks:
                bg = t.get('task_color', '#AFAE9D')
                card = QFrame()
                card.setStyleSheet(f"background: {bg}; border-radius: 8px; color: white;")
                card.setFixedHeight(60)
                
                row = QHBoxLayout(card)
                row.setContentsMargins(15, 0, 15, 0)
                
                time_val = t['deadline_time'] if t['deadline_time'] != "00:00" else "All Day"
                time_lbl = QLabel(time_val)
                time_lbl.setStyleSheet("font-weight: bold; font-size: 16px; background: transparent;")
                
                title_lbl = QLabel(t['title'])
                title_lbl.setStyleSheet("font-size: 14px; font-weight: bold; background: transparent;")
                
                row.addWidget(time_lbl)
                row.addSpacing(15)
                row.addWidget(title_lbl)
                row.addStretch()
                
                vl.addWidget(card)
                
        vl.addStretch()
        scroll.setWidget(container)
        self.cal_layout.addWidget(scroll)

    def render_week_view(self):
        start_of_week = self.cal_date - timedelta(days=self.cal_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        self.lbl_cal_title.setText(f"{start_of_week.strftime('%d %b')} - {end_of_week.strftime('%d %b %Y')}")
        
        tasks = self.api.get_tasks_by_month(start_of_week.strftime("%Y-%m"))
        if start_of_week.month != end_of_week.month:
            tasks += self.api.get_tasks_by_month(end_of_week.strftime("%Y-%m"))
            
        tasks_map = {}
        for t in tasks: 
            tasks_map.setdefault(t['todo_date'], []).append(t)
            
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(10)
        grid.setContentsMargins(0,0,0,0)
        
        days_name = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        
        for i in range(7):
            curr = start_of_week + timedelta(days=i)
            curr_str = curr.strftime("%Y-%m-%d")
            is_today = (curr.date() == datetime.now().date())
            
            # Header
            head = QLabel(f"{days_name[i]}\n{curr.day}")
            head.setAlignment(Qt.AlignmentFlag.AlignCenter)
            head.setFixedHeight(50)
            
            style = "font-weight: bold; border-radius: 4px;"
            if is_today: style += " background: #D45D5D; color: white;"
            else: style += " background: #E0E0E0; color: #555;"
            head.setStyleSheet(style)
            
            grid.addWidget(head, 0, i)
            
            # Column
            col_frame = QFrame()
            col_frame.setStyleSheet("background: white; border: 1px solid #E0E0E0; border-radius: 4px;")
            cl = QVBoxLayout(col_frame)
            cl.setSpacing(5)
            cl.setContentsMargins(5, 5, 5, 5)
            
            if curr_str in tasks_map:
                for t in tasks_map[curr_str]:
                    lbl = QLabel(t['title'])
                    lbl.setWordWrap(True)
                    lbl.setStyleSheet(f"background: {t.get('task_color', '#AFAE9D')}; color: white; border-radius: 3px; padding: 4px; font-size: 11px;")
                    cl.addWidget(lbl)
            
            cl.addStretch()
            grid.addWidget(col_frame, 1, i)
            
        for i in range(7): 
            grid.setColumnStretch(i, 1)
            
        self.cal_layout.addWidget(grid_widget)

    def render_month_view(self):
        self.lbl_cal_title.setText(self.cal_date.strftime("%B %Y").upper())
        
        year, month = self.cal_date.year, self.cal_date.month
        month_tasks = self.api.get_tasks_by_month(self.cal_date.strftime("%Y-%m"))
        
        tasks_map = {}
        for t in month_tasks:
            try: 
                day = int(t['todo_date'].split('-')[-1])
                tasks_map.setdefault(day, []).append(t)
            except: pass
            
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(0)
        grid.setContentsMargins(0,0,0,0)
        
        # Headers
        days_header = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        for i, d in enumerate(days_header):
            lbl = QLabel(d)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-weight: bold; color: #666; padding: 10px; background: #FAFAF9; border-bottom: 1px solid #DDD;")
            grid.addWidget(lbl, 0, i)
            
        cal_matrix = calendar.monthcalendar(year, month)
        today = datetime.now()
        
        for r, week in enumerate(cal_matrix):
            for c, day in enumerate(week):
                cell = QFrame()
                style = "background: white; border-right: 1px solid #EEE; border-bottom: 1px solid #EEE;"
                if c == 0: style += " border-left: 1px solid #EEE;"
                
                cell.setStyleSheet(style)
                cell.setMinimumHeight(120) 
                
                if day == 0:
                    cell.setStyleSheet("background: #FCFCFC; border-right: 1px solid #EEE; border-bottom: 1px solid #EEE;")
                    grid.addWidget(cell, r+1, c)
                    continue
                
                vl = QVBoxLayout(cell)
                vl.setContentsMargins(5, 5, 5, 5)
                vl.setSpacing(2)
                
                # Day Number
                num = QLabel(str(day))
                num.setAlignment(Qt.AlignmentFlag.AlignRight)
                num_style = "font-weight: bold; color: #555; font-size: 12px;"
                
                if today.day == day and today.month == month and today.year == year:
                    num_style += " background: #D45D5D; color: white; border-radius: 10px; padding: 2px 6px;"
                    num.setFixedSize(30, 24)
                    num.setAlignment(Qt.AlignmentFlag.AlignCenter)
                
                num.setStyleSheet(num_style)
                
                top_row = QHBoxLayout()
                top_row.addStretch()
                top_row.addWidget(num)
                vl.addLayout(top_row)
                
                # Tasks
                if day in tasks_map:
                    for i, t in enumerate(tasks_map[day]):
                        if i < 3: 
                            lbl = QLabel(t['title'])
                            lbl.setStyleSheet(f"background: {t.get('task_color', '#AFAE9D')}; color: white; border-radius: 2px; padding: 2px 4px; font-size: 10px;")
                            lbl.setFixedHeight(18)
                            vl.addWidget(lbl)
                        else:
                            vl.addWidget(QLabel(f"+ {len(tasks_map[day])-3} more", styleSheet="color: #888; font-size: 9px;"))
                            break
                            
                vl.addStretch()
                grid.addWidget(cell, r+1, c)
                
        for i in range(7): grid.setColumnStretch(i, 1)
        
        scroll.setWidget(container)
        self.cal_layout.addWidget(scroll)

    def render_year_view(self):
        year = self.cal_date.year
        self.lbl_cal_title.setText(str(year))
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(20)
        
        months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        
        for i, m_name in enumerate(months):
            card = QFrame()
            card.setFixedSize(180, 120)
            card.setStyleSheet("""
                QFrame { 
                    background: white; 
                    border: 1px solid #E0E0E0; 
                    border-radius: 12px; 
                }
                QFrame:hover { border: 1px solid #6C5CE7; }
            """)
            
            vl = QVBoxLayout(card)
            vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            lbl_m = QLabel(m_name)
            lbl_m.setStyleSheet("font-weight: bold; font-size: 20px; color: #383838; background: transparent; border: none;")
            
            lbl_sub = QLabel("View Tasks")
            lbl_sub.setStyleSheet("color: #888; font-size: 12px; background: transparent; border: none;")
            
            vl.addWidget(lbl_m)
            vl.addWidget(lbl_sub)
            
            btn = QPushButton(card)
            btn.setGeometry(0,0,180,120)
            btn.setStyleSheet("background: transparent; border: none;")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda ch, m=i+1: self.open_month(m))
            
            grid.addWidget(card, i // 4, i % 4)
            
        scroll.setWidget(container)
        self.cal_layout.addWidget(scroll)

    def open_month(self, month):
        self.cal_date = self.cal_date.replace(month=month, day=1)
        self.view_mode.setCurrentText("Month")
        self.refresh_calendar()

        