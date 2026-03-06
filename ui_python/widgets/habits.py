from datetime import datetime, date as dt_date
from calendar import monthrange
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QDateEdit, QFrame, 
    QAbstractItemView, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

# Dialogs
from dialogs import AddHabitDialog, EditHabitDialog
from charts import LineChart 

class HabitsWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.api = main_window.api
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15) 
        
        # --- 1. HEADER (Controls) ---
        h_ctrl = QHBoxLayout()
        
        lbl_period = QLabel("PERIOD:")
        lbl_period.setStyleSheet("color: #666; font-weight: bold; font-size: 11px;")
        h_ctrl.addWidget(lbl_period)
        
        self.habit_month_sel = QDateEdit()
        self.habit_month_sel.setDisplayFormat("MMMM yyyy")
        self.habit_month_sel.setDate(datetime.now().date())
        self.habit_month_sel.setFixedWidth(130)
        self.habit_month_sel.setStyleSheet("""
            QDateEdit { 
                padding: 5px; border: 1px solid #CCC; border-radius: 4px; color: #333; font-weight: bold;
            }
            QDateEdit::drop-down { border: none; }
        """)
        self.habit_month_sel.dateChanged.connect(self.load_habit_grid)
        h_ctrl.addWidget(self.habit_month_sel)
        
        h_ctrl.addStretch()
        
        btn_add = QPushButton("+ ADD HABIT")
        btn_add.setObjectName("PrimaryBtn")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.setFixedSize(100, 30)
        btn_add.setStyleSheet("""
            QPushButton {
                background-color: #383838; color: white; 
                border-radius: 4px; font-weight: bold; font-size: 11px;
            }
            QPushButton:hover { background-color: #555; }
        """)
        btn_add.clicked.connect(self.add_habit_dialog)
        h_ctrl.addWidget(btn_add)
        
        layout.addLayout(h_ctrl)
        
        # --- 2. CHART SECTION ---
        chart_frame = QFrame()
        chart_frame.setObjectName("Card")
        chart_frame.setFixedHeight(220) 
        chart_frame.setStyleSheet("""
            QFrame#Card { 
                background-color: white; 
                border: 1px solid #E0E0E0; 
                border-radius: 8px; 
            }
        """)
        
        cf_layout = QVBoxLayout(chart_frame)
        cf_layout.setContentsMargins(10, 10, 10, 5) 
        
        self.chart = LineChart()
        cf_layout.addWidget(self.chart)
        
        layout.addWidget(chart_frame)

        # --- 3. HABIT GRID ---
        self.habit_grid = QTableWidget()
        self.habit_grid.verticalHeader().setVisible(False)
        self.habit_grid.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.habit_grid.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.habit_grid.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        self.habit_grid.setStyleSheet("""
            QTableWidget { 
                border: 1px solid #E0E0E0; 
                background-color: white; 
                border-radius: 8px; 
                gridline-color: #F0F0F0;
            }
            QHeaderView::section { 
                background-color: #FAFAF9; 
                border: none; 
                border-bottom: 1px solid #E0E0E0;
                font-weight: bold; 
                color: #555; 
                padding: 4px;
            }
        """)
        self.habit_grid.cellClicked.connect(self.on_habit_cell_click)
        
        layout.addWidget(self.habit_grid)

        # --- 4. REFLECTIONS ---
        r_frame = QFrame()
        r_frame.setObjectName("Card")
        r_frame.setFixedHeight(140)
        r_frame.setStyleSheet("""
            QFrame#Card { 
                background-color: white; 
                border: 1px solid #E0E0E0; 
                border-radius: 8px; 
            }
        """)
        
        rl = QVBoxLayout(r_frame)
        rl.setContentsMargins(15, 10, 15, 10)
        rl.setSpacing(5)
        
        lbl_ref = QLabel("DAILY REFLECTIONS (Score 1-10)")
        lbl_ref.setStyleSheet("color: #6C5CE7; font-weight: bold; font-size: 11px; letter-spacing: 1px;")
        rl.addWidget(lbl_ref)
        
        self.reflect_grid = QTableWidget()
        self.reflect_grid.verticalHeader().setVisible(True)
        self.reflect_grid.verticalHeader().setFixedWidth(100)
        self.reflect_grid.horizontalHeader().setVisible(False)
        self.reflect_grid.setStyleSheet("""
            QTableWidget { border: none; background-color: transparent; }
            QHeaderView::section { background-color: white; border: none; font-weight: bold; color: #888; text-align: left; }
        """)
        self.reflect_grid.cellChanged.connect(self.on_reflection_change)
        
        rl.addWidget(self.reflect_grid)
        layout.addWidget(r_frame)

    def load_habit_grid(self):
        sel_date = self.habit_month_sel.date()
        month_str = sel_date.toString("yyyy-MM")
        days_in_month = monthrange(sel_date.year(), sel_date.month())[1]
        
        habits = self.api.get_habit_grid(month_str)
        reflections = self.api.get_reflections(month_str)
        
        # --- A. HABIT GRID ---
        self.habit_grid.blockSignals(True)
        self.habit_grid.clear()
        self.habit_grid.setRowCount(len(habits))
        self.habit_grid.setColumnCount(1 + days_in_month + 1)
        
        headers = ["HABIT"] + [str(d) for d in range(1, days_in_month + 1)] + ["%"]
        self.habit_grid.setHorizontalHeaderLabels(headers)
        
        self.habit_grid.setColumnWidth(0, 180)
        self.habit_grid.setColumnWidth(days_in_month+1, 50)
        for i in range(1, days_in_month + 1): 
            self.habit_grid.setColumnWidth(i, 28)
            
        for row, h in enumerate(habits):
            # Title (Read-only)
            it = QTableWidgetItem(h['title'])
            it.setData(Qt.ItemDataRole.UserRole, h['id'])
            it.setFont(QFont("Segoe UI", 10))
            it.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self.habit_grid.setItem(row, 0, it)
            
            done_count = 0
            for day in range(1, days_in_month + 1):
                item = QTableWidgetItem("")
                item.setFlags(Qt.ItemFlag.ItemIsEnabled) 
                
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                bg = QColor("#FFFFFF") if ((day - 1) // 7) % 2 == 0 else QColor("#FAFAF9")
                item.setBackground(bg)
                
                if day in h['days']:
                    item.setText("✔")
                    item.setForeground(QColor("#7FB06F"))
                    item.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
                    done_count += 1
                
                self.habit_grid.setItem(row, day, item)
            
            # Percentage
            target = h['target'] if h['target'] > 0 else days_in_month
            perc = int((done_count/target)*100)
            p_item = QTableWidgetItem(f"{perc}%")
            p_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            p_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            
            if perc >= 100: 
                p_item.setForeground(QColor("#6C5CE7"))
                p_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            else: 
                p_item.setForeground(QColor("#888"))
            
            self.habit_grid.setItem(row, days_in_month+1, p_item)
            
        self.habit_grid.blockSignals(False)
        
        # --- B. CHART ---
        stats = self.api.get_habit_score_stats(month_str)
        full_dates = [f"{d:02d}" for d in range(1, days_in_month + 1)]
        full_scores = [0] * days_in_month
        
        if stats:
            for s in stats:
                try:
                    day_idx = int(s['date'][8:]) - 1
                    if 0 <= day_idx < days_in_month:
                        full_scores[day_idx] = int(s['total_score'])
                except: pass
        
        self.chart.plot(full_dates, full_scores, "PRODUCTIVITY SCORE")

        # --- C. REFLECTIONS ---
        self.reflect_grid.blockSignals(True)
        self.reflect_grid.clear()
        self.reflect_grid.setRowCount(3)
        self.reflect_grid.setColumnCount(days_in_month)
        self.reflect_grid.setVerticalHeaderLabels(["MOOD", "ENERGY", "MOTIVATION"])
        
        ref_map = {}
        for r in reflections: 
            try: ref_map[int(r['date'].split('-')[-1])] = r 
            except: pass
            
        for col in range(days_in_month):
            self.reflect_grid.setColumnWidth(col, 28)
            data = ref_map.get(col+1, {})
            
            for r_idx, key in enumerate(['mood', 'energy', 'motivation']):
                val = str(data.get(key, ""))
                if val == "0": val = ""
                it = QTableWidgetItem(val)
                it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                bg = QColor("#FFFFFF") if ((col) // 7) % 2 == 0 else QColor("#FAFAF9")
                it.setBackground(bg)
                self.reflect_grid.setItem(r_idx, col, it)
                
        self.reflect_grid.blockSignals(False)

    def add_habit_dialog(self):
        diffs = self.api.get_difficulties()
        dlg = AddHabitDialog(diffs)
        if dlg.exec():
            t, d_id = dlg.get_data()
            if t:
                self.api.add_habit(t, d_id)
                self.load_habit_grid()

    def on_habit_cell_click(self, row, col):
        hid_item = self.habit_grid.item(row, 0)
        if not hid_item: return
        hid = hid_item.data(Qt.ItemDataRole.UserRole)
        
        if col == 0: # Edit Habit
            current_title = hid_item.text()
            diffs = self.api.get_difficulties()
            dlg = EditHabitDialog(diffs, current_title, 3) 
            if dlg.exec():
                new_title, new_diff = dlg.get_data()
                if new_title:
                    self.api.edit_habit(hid, new_title, new_diff)
                    self.load_habit_grid()
            elif dlg.delete_requested:
                self.api.del_habit(hid)
                self.load_habit_grid()
            return

        if col == self.habit_grid.columnCount() - 1: return # Skip %
        
        d = self.habit_month_sel.date()
        
        try:
            day_num = col 
            date_str = f"{d.year()}-{d.month():02d}-{day_num:02d}"
            
            selected_date = datetime(d.year(), d.month(), day_num).date()
            
            # Future protection
            if selected_date > dt_date.today(): 
                QMessageBox.warning(self, "Hold on!", "You cannot complete habits in the future.\nWait for that day to come! ⏳")
                return 

            self.api.toggle_habit_date(hid, date_str)
            self.load_habit_grid()
            self.main_window.gamification_widget.refresh_profile()
            self.main_window.refresh_all()
        except ValueError:
            pass 

    def on_reflection_change(self, row, col):
        item = self.reflect_grid.item(row, col)
        if not item: return
        
        val_str = item.text()
        if not val_str: val_int = 0
        else:
            try:
                val_int = int(val_str)
                if val_int < 1 or val_int > 10: raise ValueError
            except:
                item.setText("")
                return

        d = self.habit_month_sel.date()
        date_str = f"{d.year()}-{d.month():02d}-{col+1:02d}"
        
        def get_val(r): 
            it = self.reflect_grid.item(r, col)
            if it and it.text().isdigit(): return int(it.text())
            return 5
            
        mood = get_val(0)
        energy = get_val(1)
        motiv = get_val(2)
        
        if row == 0: mood = val_int
        elif row == 1: energy = val_int
        elif row == 2: motiv = val_int

        self.api.set_reflection(date_str, mood, energy, motiv)