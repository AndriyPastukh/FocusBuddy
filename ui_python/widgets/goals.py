from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

from dialogs import AddGoalDialog, EditGoalDialog 

class GoalsWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.api = main_window.api
        self.lookups = main_window.lookups
        
        # Timer cache for countdowns
        self.active_timers = []
        
        # Countdown Timer (1s)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdowns)
        self.timer.start(1000)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        h_layout = QHBoxLayout()
        lbl = QLabel("YEARLY GOALS STRATEGY")
        lbl.setFont(QFont("Oswald", 14, QFont.Weight.Bold))
        h_layout.addWidget(lbl)
        h_layout.addStretch()
        
        btn_add = QPushButton("+ NEW GOAL")
        btn_add.setObjectName("PrimaryBtn")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self.add_goal_dialog)
        h_layout.addWidget(btn_add)
        
        layout.addLayout(h_layout)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll)

        # Initial Load
        self.load_goals()

    def load_goals(self):
        self.active_timers.clear()
        
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        goals = self.api.get_goals()
        
        row, col = 0, 0
        for g in goals:
            card = self.create_goal_card(g)
            self.cards_layout.addWidget(card, row, col)
            
            col += 1
            if col > 1: # 2 columns
                col = 0
                row += 1
        
        self.update_countdowns()

    def create_goal_card(self, g):
        card = QFrame()
        card.setObjectName("Card")
        card.setFixedSize(480, 300) 
        card.setStyleSheet("""
            QFrame#Card { 
                background-color: white; 
                border-radius: 15px; 
                border: 1px solid #E0E0E0;
            }
        """)
        
        is_done = (str(g['is_completed']) == "1")
        
        l = QVBoxLayout(card)
        l.setSpacing(5)
        l.setContentsMargins(20, 20, 20, 20)
        
        # --- 1. Header ---
        h_top = QHBoxLayout()
        
        cat_lbl = QLabel(g['category'].upper())
        cat_lbl.setStyleSheet(f"background-color: {g.get('c_color', '#eee')}; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 10px;")
        h_top.addWidget(cat_lbl)
        
        if g.get('deadline'):
            dead_lbl = QLabel(f"DEADLINE: {g['deadline']}")
            dead_lbl.setStyleSheet("color: #888; font-weight: bold; font-size: 10px; margin-left: 10px;")
            h_top.addWidget(dead_lbl)
            
        h_top.addStretch()

        btn_check = QPushButton("DONE" if is_done else "ACTIVE")
        btn_check.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_check.setCheckable(True)
        btn_check.setChecked(is_done)
        btn_check.setFixedSize(80, 24)
        if is_done:
            btn_check.setStyleSheet("background-color: #7FB06F; color: white; border: none; font-weight: bold; border-radius: 12px;")
        else:
            btn_check.setStyleSheet("background-color: #E0E0E0; color: #555; border: none; border-radius: 12px;")
            
        btn_check.clicked.connect(lambda ch, gid=g['id']: self.toggle_goal_action(gid))
        h_top.addWidget(btn_check)
        l.addLayout(h_top)
        
        # --- 2. Title ---
        title = QPushButton(g['title'])
        title.setCursor(Qt.CursorShape.PointingHandCursor)
        title.setStyleSheet("text-align: left; font-weight: bold; font-size: 18px; border: none; background: transparent;")
        if is_done:
            title.setStyleSheet("text-align: left; font-weight: bold; font-size: 18px; border: none; background: transparent; color: #aaa; text-decoration: line-through;")
        
        title.clicked.connect(lambda ch, goal=g: self.edit_goal_dialog(goal))
        l.addWidget(title)

        # --- 3. Countdown Timer ---
        if g.get('deadline') and not is_done:
            try:
                d_str = g['deadline']
                dt_deadline = datetime.strptime(d_str, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
                
                lbl_timer = QLabel("Loading...")
                lbl_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl_timer.setFont(QFont("Oswald", 28, QFont.Weight.Bold)) 
                
                self.active_timers.append((dt_deadline, lbl_timer))
                l.addWidget(lbl_timer)
            except: pass
        elif is_done:
            lbl_done = QLabel("GOAL ACHIEVED 🎉")
            lbl_done.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_done.setFont(QFont("Oswald", 24, QFont.Weight.Bold))
            lbl_done.setStyleSheet("color: #7FB06F; margin-top: 5px; margin-bottom: 5px;")
            l.addWidget(lbl_done)
        else:
             l.addSpacing(40) 
        
        # --- 4. Habits List ---
        l.addSpacing(10)
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine); line.setStyleSheet("color: #EEE"); l.addWidget(line)
        l.addSpacing(5)
        
        self.add_habit_row(l, "DAILY:", g['habit_daily'])
        self.add_habit_row(l, "WEEKLY:", g['habit_weekly'])
        self.add_habit_row(l, "MONTHLY:", g['habit_monthly'])
        
        l.addStretch()
        return card

    def update_countdowns(self):
        now = datetime.now()
        
        for deadline, label in self.active_timers:
            delta = deadline - now
            
            if delta.total_seconds() <= 0:
                label.setText("EXPIRED")
                label.setStyleSheet("color: #D45D5D;") 
            else:
                days = delta.days
                seconds = int(delta.total_seconds())
                hours = (seconds // 3600) % 24
                minutes = (seconds // 60) % 60
                secs = seconds % 60
                
                time_str = f"{days}D {hours:02}H {minutes:02}M {secs:02}S"
                label.setText(time_str)
                
                if days < 3: label.setStyleSheet("color: #D45D5D;")
                elif days < 30: label.setStyleSheet("color: #E0C068;")
                else: label.setStyleSheet("color: #383838;")

    def add_habit_row(self, layout, label, text):
        if not text: return
        r = QHBoxLayout()
        r.setSpacing(10)
        lbl = QLabel(label)
        lbl.setFixedWidth(60)
        lbl.setStyleSheet("color: #888; font-size: 10px; font-weight: bold;")
        val = QLabel(text)
        val.setStyleSheet("font-size: 12px; color: #444;")
        r.addWidget(lbl)
        r.addWidget(val)
        layout.addLayout(r)

    def add_goal_dialog(self):
        dlg = AddGoalDialog(self.lookups.categories)
        if dlg.exec():
            title, dead, d, w, m, cat = dlg.get_data()
            if title:
                self.api.add_goal(title, dead, d, w, m, cat)
                self.load_goals()
                self.main_window.refresh_all()

    def edit_goal_dialog(self, goal_data):
        dlg = EditGoalDialog(self.lookups.categories, goal_data)
        if dlg.exec():
            title, dead, d, w, m, cat = dlg.get_data()
            if title:
                self.api.edit_goal(goal_data['id'], title, dead, d, w, m, cat)
                self.load_goals()
                self.main_window.refresh_all()
        elif dlg.delete_requested:
            self.api.del_goal(goal_data['id'])
            self.load_goals()
            self.main_window.refresh_all()

    def toggle_goal_action(self, gid):
        self.api.toggle_goal(gid)
        self.load_goals()
        self.main_window.refresh_all()