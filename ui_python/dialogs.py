from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QDateEdit, QTimeEdit, QComboBox, QMessageBox,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem, 
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QColor, QFont 

TRACKERY_STYLE = """
    QDialog { background-color: white; }
    QLabel { font-size: 12px; color: #333; font-weight: bold; }
    QLineEdit, QDateEdit, QTimeEdit, QComboBox { 
        padding: 8px; border: 1px solid #CCC; border-radius: 4px; font-size: 13px;
    }
    QPushButton#PrimaryBtn {
        background-color: #383838; color: white; border: none; padding: 10px; 
        border-radius: 4px; font-weight: bold; font-size: 12px;
    }
    QPushButton#PrimaryBtn:hover { background-color: #555; }
    
    QPushButton#DangerBtn {
        background-color: white; color: #D45D5D; border: 1px solid #D45D5D; 
        padding: 5px; border-radius: 4px; font-weight: bold;
    }
    QPushButton#DangerBtn:hover { background-color: #D45D5D; color: white; }
"""

# === TASK DIALOG (MODIFIED) ===
class AddTaskDialog(QDialog):
    def __init__(self, categories, priorities, is_edit=False):
        super().__init__()
        self.setWindowTitle("TASK DETAILS")
        self.setStyleSheet(TRACKERY_STYLE)
        self.setFixedSize(400, 550) 
        self.delete_requested = False 
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20) 
        layout.setSpacing(15)
        
        self.title = QLineEdit()
        self.title.setPlaceholderText("What needs to be done?")
        
        self.todo_date = QDateEdit()
        self.todo_date.setCalendarPopup(True)
        self.todo_date.setDate(QDate.currentDate())
        self.todo_date.setDisplayFormat("yyyy-MM-dd")
        
        self.deadline_date = QDateEdit()
        self.deadline_date.setCalendarPopup(True)
        self.deadline_date.setDate(QDate.currentDate())
        self.deadline_date.setDisplayFormat("yyyy-MM-dd")
        
        self.deadline_time = QTimeEdit()
        self.deadline_time.setTime(QTime(23, 59))
        self.deadline_time.setDisplayFormat("HH:mm")

        self.cat = QComboBox()
        for c in categories: self.cat.addItem(c['name'], c['id'])
        
        self.prio = QComboBox()
        for p in priorities: self.prio.addItem(p['name'], p['id'])
        
        self.color = QComboBox()
        colors = [("Gray", "#AFAE9D"), ("Red", "#FFB3B3"), ("Green", "#C7E5C7"), ("Blue", "#C7DDE5")]
        for n, c in colors: self.color.addItem(n, c)

        layout.addWidget(QLabel("TASK TITLE"))
        layout.addWidget(self.title)
        layout.addWidget(QLabel("DO DATE"))
        layout.addWidget(self.todo_date)
        
        h_dead = QHBoxLayout()
        v_d = QVBoxLayout(); v_d.addWidget(QLabel("DEADLINE DATE")); v_d.addWidget(self.deadline_date)
        v_t = QVBoxLayout(); v_t.addWidget(QLabel("TIME")); v_t.addWidget(self.deadline_time)
        h_dead.addLayout(v_d); h_dead.addLayout(v_t)
        layout.addLayout(h_dead)
        
        layout.addWidget(QLabel("CATEGORY"))
        layout.addWidget(self.cat)
        layout.addWidget(QLabel("PRIORITY"))
        layout.addWidget(self.prio)
        
        layout.addStretch()
        
        btns_layout = QHBoxLayout()
        
        if is_edit:
            btn_del = QPushButton("DELETE")
            btn_del.setObjectName("DangerBtn")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.clicked.connect(self.on_delete_clicked)
            btns_layout.addWidget(btn_del)
        
        btn_save = QPushButton("SAVE TASK")
        btn_save.setObjectName("PrimaryBtn")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.clicked.connect(self.accept)
        
        btns_layout.addWidget(btn_save)
        layout.addLayout(btns_layout)

    def on_delete_clicked(self):
        reply = QMessageBox.question(
            self, 'Confirm Delete', 
            "Are you sure you want to delete this task?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.delete_requested = True
            self.reject() 



    def set_data(self, title, todo, d_date, d_time, c_id, p_id, clr):
        self.title.setText(title)
        self.todo_date.setDate(datetime.strptime(todo, "%Y-%m-%d").date())
        self.deadline_date.setDate(datetime.strptime(d_date, "%Y-%m-%d").date())
        self.deadline_time.setTime(datetime.strptime(d_time, "%H:%M").time())
        
        idx_c = self.cat.findData(c_id)
        if idx_c != -1: self.cat.setCurrentIndex(idx_c)
        
        idx_p = self.prio.findData(p_id)
        if idx_p != -1: self.prio.setCurrentIndex(idx_p)
        
        idx_clr = self.color.findData(clr)
        if idx_clr != -1: self.color.setCurrentIndex(idx_clr)

    def get_data(self):
        return (
            self.title.text(),
            self.todo_date.date().toString("yyyy-MM-dd"),
            self.deadline_date.date().toString("yyyy-MM-dd"),
            self.deadline_time.time().toString("HH:mm"),
            self.cat.currentData(),
            self.prio.currentData(),
            self.color.currentData()
        )

# === HABIT DIALOGS ===
class AddHabitDialog(QDialog):
    def __init__(self, difficulties):
        super().__init__()
        self.setWindowTitle("NEW HABIT")
        self.setStyleSheet(TRACKERY_STYLE)
        self.setFixedSize(350, 250)
        
        l = QVBoxLayout(self)
        l.setContentsMargins(20, 20, 20, 20)
        
        self.title = QLineEdit()
        self.title.setPlaceholderText("Habit Title (e.g. Read 20 mins)")
        
        self.diff = QComboBox()
        for d in difficulties:
            self.diff.addItem(f"{d['name']} (+{d['score']} XP)", d['id'])
            
        l.addWidget(QLabel("HABIT TITLE"))
        l.addWidget(self.title)
        l.addWidget(QLabel("DIFFICULTY"))
        l.addWidget(self.diff)
        l.addStretch()
        
        btn = QPushButton("CREATE")
        btn.setObjectName("PrimaryBtn")
        btn.clicked.connect(self.accept)
        l.addWidget(btn)
        
    def get_data(self):
        return self.title.text(), self.diff.currentData()

class EditHabitDialog(QDialog):
    def __init__(self, difficulties, current_title, current_diff_id):
        super().__init__()
        self.setWindowTitle("EDIT HABIT")
        self.setStyleSheet(TRACKERY_STYLE)
        self.setFixedSize(350, 250)
        self.delete_requested = False
        
        l = QVBoxLayout(self)
        l.setContentsMargins(20, 20, 20, 20)
        
        self.title = QLineEdit()
        self.title.setText(current_title)
        
        self.diff = QComboBox()
        for d in difficulties:
            self.diff.addItem(f"{d['name']} (+{d['score']} XP)", d['id'])
            
        idx = self.diff.findData(current_diff_id)
        if idx != -1: self.diff.setCurrentIndex(idx)
        
        l.addWidget(QLabel("HABIT TITLE"))
        l.addWidget(self.title)
        l.addWidget(QLabel("DIFFICULTY"))
        l.addWidget(self.diff)
        l.addStretch()
        
        h_btns = QHBoxLayout()
        btn_del = QPushButton("DELETE")
        btn_del.setObjectName("DangerBtn")
        btn_del.clicked.connect(self.on_delete)
        
        btn_save = QPushButton("SAVE")
        btn_save.setObjectName("PrimaryBtn")
        btn_save.clicked.connect(self.accept)
        
        h_btns.addWidget(btn_del)
        h_btns.addWidget(btn_save)
        l.addLayout(h_btns)

    def on_delete(self):
        if QMessageBox.question(self, "Delete", "Delete this habit and logs?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.delete_requested = True
            self.reject()

    def get_data(self):
        return self.title.text(), self.diff.currentData()

# === GOALS DIALOGS ===

class AddGoalDialog(QDialog):
    def __init__(self, categories):
        super().__init__()
        self.setWindowTitle("NEW GOAL")
        self.setStyleSheet(TRACKERY_STYLE)
        self.setFixedSize(400, 500) 
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.title = QLineEdit(); self.title.setPlaceholderText("Main Goal (e.g. Learn English)")
        
        self.deadline = QDateEdit()
        self.deadline.setDate(datetime.now().date() + timedelta(days=365)) 
        self.deadline.setCalendarPopup(True)
        self.deadline.setDisplayFormat("yyyy-MM-dd")

        self.daily = QLineEdit(); self.daily.setPlaceholderText("Daily Habit (e.g. 15 min words)")
        self.weekly = QLineEdit(); self.weekly.setPlaceholderText("Weekly Habit (e.g. Speaking Club)")
        self.monthly = QLineEdit(); self.monthly.setPlaceholderText("Monthly Habit (e.g. Mock Test)")
        
        self.cat = QComboBox()
        for c in categories: self.cat.addItem(c['name'], c['id'])
        
        layout.addWidget(QLabel("GLOBAL GOAL TITLE"))
        layout.addWidget(self.title)
        
        layout.addWidget(QLabel("TARGET DEADLINE"))
        layout.addWidget(self.deadline)

        layout.addWidget(QLabel("CATEGORY"))
        layout.addWidget(self.cat)
        
        layout.addWidget(QLabel("DECOMPOSITION (HABITS)"))
        layout.addWidget(self.daily)
        layout.addWidget(self.weekly)
        layout.addWidget(self.monthly)
        
        layout.addSpacing(20)
        btn = QPushButton("SET GOAL"); btn.setObjectName("PrimaryBtn")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

    def get_data(self):
        return (
            self.title.text(), 
            self.deadline.date().toString("yyyy-MM-dd"),
            self.daily.text(), 
            self.weekly.text(), 
            self.monthly.text(), 
            self.cat.currentData()
        )

class EditGoalDialog(QDialog):
    def __init__(self, categories, goal_data):
        super().__init__()
        self.setWindowTitle("EDIT GOAL")
        self.setStyleSheet(TRACKERY_STYLE)
        self.setFixedSize(400, 550)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        self.title = QLineEdit(); self.title.setText(goal_data['title'])
        
        self.deadline = QDateEdit()
        try:
            self.deadline.setDate(datetime.strptime(goal_data.get('deadline', ''), "%Y-%m-%d").date())
        except:
            self.deadline.setDate(datetime.now().date())
        self.deadline.setCalendarPopup(True)
        self.deadline.setDisplayFormat("yyyy-MM-dd")

        self.daily = QLineEdit(); self.daily.setText(goal_data['habit_daily'])
        self.weekly = QLineEdit(); self.weekly.setText(goal_data['habit_weekly'])
        self.monthly = QLineEdit(); self.monthly.setText(goal_data['habit_monthly'])
        
        self.cat = QComboBox()
        for c in categories: 
            self.cat.addItem(c['name'], c['id'])
        
        idx = self.cat.findData(int(goal_data['category_id']))
        if idx != -1: self.cat.setCurrentIndex(idx)
        
        layout.addWidget(QLabel("GLOBAL GOAL TITLE"))
        layout.addWidget(self.title)
        layout.addWidget(QLabel("TARGET DEADLINE"))
        layout.addWidget(self.deadline)
        layout.addWidget(QLabel("CATEGORY"))
        layout.addWidget(self.cat)
        layout.addWidget(QLabel("DECOMPOSITION"))
        layout.addWidget(self.daily)
        layout.addWidget(self.weekly)
        layout.addWidget(self.monthly)
        
        layout.addSpacing(15)
        
        h_btns = QHBoxLayout()
        btn_del = QPushButton("DELETE GOAL")
        btn_del.setObjectName("DangerBtn")
        btn_del.clicked.connect(self.delete_clicked)
        
        btn_save = QPushButton("SAVE CHANGES"); btn_save.setObjectName("PrimaryBtn")
        btn_save.clicked.connect(self.accept)
        
        h_btns.addWidget(btn_del)
        h_btns.addWidget(btn_save)
        layout.addLayout(h_btns)
        
        self.delete_requested = False

    def delete_clicked(self):
        if QMessageBox.question(self, "Delete", "Delete this goal?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.delete_requested = True
            self.reject()

    def get_data(self):
        return (
            self.title.text(), 
            self.deadline.date().toString("yyyy-MM-dd"),
            self.daily.text(), 
            self.weekly.text(), 
            self.monthly.text(), 
            self.cat.currentData()
        )

# === NEW: TASK SELECTOR & HISTORY ===

class TaskSelectDialog(QDialog):
    def __init__(self, tasks):
        super().__init__()
        self.setWindowTitle("SELECT TASK FOR FOCUS")
        self.setFixedSize(450, 550) 
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        lbl = QLabel("Choose a task to work on:")
        lbl.setFont(QFont("Oswald", 12, QFont.Weight.Bold)) 
        layout.addWidget(lbl)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #E0E0E0; 
                border-radius: 4px; 
                font-size: 14px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #F0F0F0;
            }
            QListWidget::item:selected {
                background-color: #E8DFF5;
                color: #383838;
            }
        """)
        
        self.selected_task_data = None
        
        for t in tasks:
            if str(t['is_completed']) == "0":
                cat_name = t.get('category', 'Task')
                item_text = f"{t['title']} \n[{cat_name}]"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, t)
                self.list_widget.addItem(item)
        
        layout.addWidget(self.list_widget)
        
        btn_select = QPushButton("SELECT THIS TASK")
        btn_select.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_select.setStyleSheet("""
            QPushButton {
                background-color: #6C5CE7; color: white; padding: 12px; 
                border-radius: 6px; font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #5A4AD1; }
        """)
        btn_select.clicked.connect(self.select_task)
        layout.addWidget(btn_select)

    def select_task(self):
        cur = self.list_widget.currentItem()
        if cur:
            self.selected_task_data = cur.data(Qt.ItemDataRole.UserRole)
            self.accept()
    
    def get_data(self):
        return self.selected_task_data

class HistoryDialog(QDialog):
    def __init__(self, sessions):
        super().__init__()
        self.setWindowTitle("FOCUS HISTORY")
        self.setFixedSize(850, 600) 
        self.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        lbl = QLabel("SESSION LOGS")
        lbl.setFont(QFont("Oswald", 14, QFont.Weight.Bold))
        layout.addWidget(lbl)
        
        table = QTableWidget()
        table.setColumnCount(7)
        table.setHorizontalHeaderLabels(["ID", "DATE", "START", "END", "MIN", "XP", "TASK"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch) # Task column stretches
        table.setColumnWidth(0, 40) # ID
        table.setColumnWidth(1, 90) # Date
        table.setColumnWidth(2, 60) # Start
        table.setColumnWidth(3, 60) # End
        table.setColumnWidth(4, 50) # Min
        table.setColumnWidth(5, 50) # XP

        table.setStyleSheet("""
            QHeaderView::section { 
                background-color: #FAFAF9; 
                padding: 6px; 
                border: none; 
                border-bottom: 2px solid #E0E0E0;
                font-weight: bold; 
                color: #555;
            }
            QTableWidget { 
                border: 1px solid #E0E0E0; 
                gridline-color: #F0F0F0;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)
        
        table.setRowCount(len(sessions))
        for i, s in enumerate(sessions):
            full_start = s['start_time']
            try:
                date_part = full_start.split(' ')[0]
                time_start = full_start.split(' ')[1][:5]
            except:
                date_part = full_start
                time_start = "-"

            try:
                time_end = s['end_time'].split(' ')[1][:5]
            except:
                time_end = "-"
            
            table.setItem(i, 0, QTableWidgetItem(str(s['id'])))
            table.setItem(i, 1, QTableWidgetItem(date_part))
            table.setItem(i, 2, QTableWidgetItem(time_start))
            table.setItem(i, 3, QTableWidgetItem(time_end))
            table.setItem(i, 4, QTableWidgetItem(str(s['duration'])))
            
            # XP item
            xp_item = QTableWidgetItem(f"+{s['xp_earned']}")
            xp_item.setForeground(QColor("#7FB06F"))
            xp_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            table.setItem(i, 5, xp_item)
            
            table.setItem(i, 6, QTableWidgetItem(s['task_title']))
            
        layout.addWidget(table)
        
        btn_close = QPushButton("CLOSE")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #F0F0F0; color: #555; padding: 10px; 
                border: 1px solid #CCC; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #E0E0E0; }
        """)
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)