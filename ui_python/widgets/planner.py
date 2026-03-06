from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QFrame,
    QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from dialogs import AddTaskDialog

class PlannerWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.api = main_window.api
        self.lookups = main_window.lookups
        self.current_filter = "active"  
        
        # --- UI LAYOUT ---
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 1. Sidebar (Filters)
        side = QFrame()
        side.setObjectName("Sidebar")
        side.setFixedWidth(240)
        side.setStyleSheet("""
            QFrame#Sidebar { background-color: white; border-right: 1px solid #E0E0E0; }
            QLabel { color: #888; font-weight: bold; font-size: 11px; margin-top: 15px; margin-bottom: 5px; padding-left: 15px; }
            QPushButton { 
                text-align: left; padding: 10px 15px; border: none; background-color: transparent; 
                color: #383838; font-size: 13px; border-radius: 5px; margin: 0 10px; 
            }
            QPushButton:hover { background-color: #F5F5F0; color: #000; }
        """)
        
        sl = QVBoxLayout(side)
        sl.setContentsMargins(0, 20, 0, 20)
        sl.setSpacing(5)
        
        # === SECTION: MAIN ===
        sl.addWidget(QLabel("MAIN"))
        
        self.btn_active = QPushButton("⚡ Active Tasks")
        self.btn_active.clicked.connect(lambda: self.switch_filter("active"))
        sl.addWidget(self.btn_active)

        self.btn_important = QPushButton("🔥 Important")
        self.btn_important.clicked.connect(lambda: self.switch_filter("important"))
        sl.addWidget(self.btn_important)

        # === SECTION: TIME ===
        sl.addWidget(QLabel("TIME"))

        self.btn_today = QPushButton("📅 Today")
        self.btn_today.clicked.connect(lambda: self.switch_filter("today"))
        sl.addWidget(self.btn_today)
        
        self.btn_overdue = QPushButton("❌ Overdue")
        self.btn_overdue.clicked.connect(lambda: self.switch_filter("overdue"))
        self.btn_overdue.setStyleSheet("color: #D45D5D; text-align: left; padding: 10px 15px; border: none; margin: 0 10px;")
        sl.addWidget(self.btn_overdue)

        # === SECTION: ARCHIVE ===
        sl.addWidget(QLabel("ARCHIVE"))

        self.btn_all = QPushButton("📂 All Tasks (History)")
        self.btn_all.clicked.connect(lambda: self.switch_filter("all"))
        sl.addWidget(self.btn_all)
        
        sl.addStretch()
        
        btn_add = QPushButton("+ NEW TASK")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self.add_task_dialog)
        btn_add.setStyleSheet("""
            QPushButton { 
                background-color: #383838; color: white; text-align: center; 
                padding: 12px; margin: 15px; border-radius: 4px; font-weight: bold; 
            }
            QPushButton:hover { background-color: #555; }
        """)
        sl.addWidget(btn_add)
        
        layout.addWidget(side)
        
        # 2. Main Content (Grid)
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        self.grid = QTableWidget()
        self.grid.setColumnCount(8) 
        self.grid.setHorizontalHeaderLabels(["ID", "STATUS", "TASK", "DEADLINE", "LEFT", "CATEGORY", "PRIORITY", "EDIT"])
        
        self.grid.setShowGrid(False)
        self.grid.setAlternatingRowColors(True)
        self.grid.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.grid.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.grid.setFrameShape(QFrame.Shape.NoFrame)
        self.grid.verticalHeader().setVisible(False)
        self.grid.verticalHeader().setDefaultSectionSize(45)
        
        self.grid.setStyleSheet("""
            QTableWidget { 
                background-color: white; alternate-background-color: #FAFAF9; 
                selection-background-color: #E8DFF5; selection-color: #383838; font-size: 13px; color: #383838; 
            }
            QHeaderView::section { 
                background-color: #CFCBC2; color: #383838; padding: 8px; font-weight: bold; 
                font-size: 12px; border: none; border-bottom: 2px solid #BDB7AB; 
            }
            QComboBox { border: 1px solid #EEE; border-radius: 4px; padding: 2px; color: #555; }
            QComboBox::drop-down { border: 0px; }
        """)

        header = self.grid.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Task Title stretch
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        
        self.grid.setColumnWidth(0, 0)   # ID 
        self.grid.setColumnWidth(1, 140) # Status
        self.grid.setColumnWidth(3, 110) # Deadline
        self.grid.setColumnWidth(4, 90)  # Left
        self.grid.setColumnWidth(5, 120) # Category
        self.grid.setColumnWidth(6, 110) # Priority
        self.grid.setColumnWidth(7, 50)  # Edit

        content_layout.addWidget(self.grid)
        layout.addWidget(content_area)

    # --- LOGIC ---

    def switch_filter(self, filter_type):
        self.current_filter = filter_type
        for btn in [self.btn_active, self.btn_important, self.btn_today, self.btn_all]:
             btn.setStyleSheet("text-align: left; padding: 10px 15px; border: none; background-color: transparent; color: #383838; margin: 0 10px;")
        
        if filter_type == "active": self.btn_active.setStyleSheet("background-color: #E8DFF5; font-weight: bold; border-radius: 5px; text-align: left; padding: 10px 15px; margin: 0 10px;")
        
        self.load_tasks(filter_type)

    def refresh_planner(self):
        self.load_tasks(self.current_filter)

    def load_tasks(self, filter_type):
        self.grid.setRowCount(0)
        self.grid.blockSignals(True) 
        
        tasks = self.api._run(["--getTasks", filter_type])
        
        print(f"DEBUG TASKS DATA ({filter_type}):", tasks)

        if not tasks: 
             self.grid.blockSignals(False)
             return
        
        self.grid.setSortingEnabled(False)
        now = datetime.now()

        COL_ID, COL_STATUS, COL_TASK, COL_DEADLINE, COL_LEFT, COL_CAT, COL_PRIO, COL_EDIT = range(8)
        self.grid.setColumnHidden(COL_ID, True)

        for t in tasks:
            row = self.grid.rowCount()
            self.grid.insertRow(row)
            
            # ID
            self.grid.setItem(row, COL_ID, QTableWidgetItem(str(t.get('id', 0))))
            
            # Status
            combo_stat = QComboBox()
            for s in self.lookups.statuses: 
                combo_stat.addItem(f"{s['icon']} {s['name']}", s['id'])
            
            raw_stat = t.get('status_id', t.get('status', 1))
            try: safe_stat_id = int(raw_stat)
            except: safe_stat_id = 1
            
            idx_s = combo_stat.findData(safe_stat_id)
            if idx_s != -1: combo_stat.setCurrentIndex(idx_s)
            
            status_str = str(t.get('status', '')) 
            if safe_stat_id == 3: # Done
                 combo_stat.setStyleSheet("color: #7FB06F; font-weight: bold; border: 1px solid #7FB06F;")
            elif safe_stat_id == 4: # Overdue
                 combo_stat.setStyleSheet("color: #D45D5D; font-weight: bold; border: 1px solid #D45D5D;")
            
            combo_stat.currentIndexChanged.connect(lambda idx, c=combo_stat, tid=t.get('id'): self.on_status_change(tid, c.currentData()))
            self.grid.setCellWidget(row, COL_STATUS, combo_stat)
            
            # Task Title
            item_task = QTableWidgetItem(t.get('title', 'No Title'))
            item_task.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            
            if safe_stat_id == 3: # Done 
                font = QFont("Segoe UI", 10)
                font.setStrikeOut(True)
                item_task.setFont(font)
                item_task.setForeground(QColor("#AAA"))
            self.grid.setItem(row, COL_TASK, item_task)
            
            # Deadline
            d_date = t.get('deadline_date', '')
            d_time = t.get('deadline_time', '')
            dt_str = f"{d_date} {d_time}"
            
            item_dt = QTableWidgetItem(d_date)
            item_dt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            is_completed_str = str(t.get('is_completed', '0'))
            if d_date and d_date < datetime.now().strftime("%Y-%m-%d") and is_completed_str == "0":
                 item_dt.setForeground(QColor("#D45D5D")) # Червоний, якщо прострочено
                 item_dt.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            self.grid.setItem(row, COL_DEADLINE, item_dt)

            # Time Left
            try:
                deadline = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
                delta = deadline - now
                
                txt, col = "-", "#383838"
                if safe_stat_id == 3: # Done
                    txt, col = "Done", "#7FB06F"
                elif delta.total_seconds() < 0:
                    txt, col = "Expired", "#D45D5D"
                elif delta.days == 0:
                    hours = int(delta.total_seconds() / 3600)
                    txt, col = f"{hours} hours", "#E0C068"
                else:
                    txt, col = f"{delta.days} days", "#383838"
                
                item_left = QTableWidgetItem(txt)
                item_left.setForeground(QColor(col))
                item_left.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                item_left.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.grid.setItem(row, COL_LEFT, item_left)
            except:
                self.grid.setItem(row, COL_LEFT, QTableWidgetItem("-"))

            # Category
            combo_cat = QComboBox()
            for c in self.lookups.categories: combo_cat.addItem(c['name'], c['id'])
            
            idx_c = combo_cat.findData(int(t.get('category_id', 1)))
            if idx_c != -1: combo_cat.setCurrentIndex(idx_c)
            
            cat_color = t.get('c_color', '#FFF') # Колір з бази або дефолт
            combo_cat.setStyleSheet(f"background-color: {cat_color}; border: none; padding-left: 5px;")
            combo_cat.currentIndexChanged.connect(lambda idx, c=combo_cat, tid=t.get('id'): self.on_category_change(tid, c.currentData()))
            self.grid.setCellWidget(row, COL_CAT, combo_cat)
            
            # Priority
            combo_prio = QComboBox()
            for p in self.lookups.priorities: combo_prio.addItem(p['name'], p['id'])
            
            idx_p = combo_prio.findData(int(t.get('priority_id', 1)))
            if idx_p != -1: combo_prio.setCurrentIndex(idx_p)
            
            p_color = t.get('p_color', '#000')
            combo_prio.setStyleSheet(f"color: {p_color}; font-weight: bold;")
            combo_prio.currentIndexChanged.connect(lambda idx, c=combo_prio, tid=t.get('id'): self.on_priority_change(tid, c.currentData()))
            self.grid.setCellWidget(row, COL_PRIO, combo_prio)

            # Edit Button
            btn_edit = QPushButton("✏️") 
            btn_edit.setFixedSize(30, 30)
            btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_edit.setStyleSheet("""
                QPushButton { background: transparent; border: none; color: #888; font-size: 14px; }
                QPushButton:hover { color: #383838; background-color: #F0F0F0; border-radius: 15px; }
            """)
            
            btn_edit.clicked.connect(lambda checked, task_data=t: self.edit_task_action(task_data))
            
            widget_edit = QWidget()
            layout_edit = QHBoxLayout(widget_edit)
            layout_edit.setContentsMargins(0,0,0,0)
            layout_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout_edit.addWidget(btn_edit)
            self.grid.setCellWidget(row, COL_EDIT, widget_edit)

        self.grid.blockSignals(False)

    def edit_task_action(self, task_data):
        dlg = AddTaskDialog(self.lookups.categories, self.lookups.priorities, is_edit=True)
        dlg.set_data(
            task_data.get('title', ''),
            task_data.get('todo_date', ''),
            task_data.get('deadline_date', ''),
            task_data.get('deadline_time', ''),
            int(task_data.get('category_id', 1)),
            int(task_data.get('priority_id', 1)),
            task_data.get('task_color', '#AFAE9D')
        )
        
        if dlg.exec():
            title, todo, deadline, time, c, p, color = dlg.get_data()
            if title:
                self.api.edit_task(task_data['id'], title, todo, deadline, time, c, p, color)
                self.main_window.refresh_all()
        
        elif dlg.delete_requested:  
            print(f"DEBUG: Deleting task ID {task_data['id']}")  
            self.api.delete_task(task_data['id'])
            self.main_window.refresh_all()

    def add_task_dialog(self):
        dlg = AddTaskDialog(self.lookups.categories, self.lookups.priorities)
        if dlg.exec():
            title, todo, deadline, time, c, p, color = dlg.get_data()
            if title:
                self.api.add_task(title, todo, deadline, time, c, p, color)
                self.main_window.refresh_all()

    def on_status_change(self, task_id, new_status_id):
        self.api.update_task_status(task_id, new_status_id)
        self.main_window.refresh_all()

    def on_category_change(self, task_id, new_cat_id):
        self.api.update_task_cat(task_id, new_cat_id)
        self.main_window.refresh_all()

    def on_priority_change(self, task_id, new_prio_id):
        self.api.update_task_prio(task_id, new_prio_id)
        self.main_window.refresh_all()