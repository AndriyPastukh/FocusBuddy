from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, 
    QLineEdit, QComboBox, QPushButton, QMessageBox, 
    QFrame, QGridLayout, QAbstractItemView, QScrollArea, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import shutil
import os

class SettingsWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.api = main_window.api
        self.lookups = main_window.lookups
        
        # Setup Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { width: 10px; background: #F0F0F0; border-radius: 5px; }
            QScrollBar::handle:vertical { background: #C0C0C0; border-radius: 5px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        
        self.content = QWidget()
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(30, 30, 30, 50)
        self.layout.setSpacing(30)

        # 1. Profile Section
        lbl_profile = QLabel("USER PROFILE")
        lbl_profile.setFont(QFont("Oswald", 16, QFont.Weight.Bold))
        lbl_profile.setStyleSheet("color: #383838;")
        self.layout.addWidget(lbl_profile)

        profile_frame = QFrame()
        profile_frame.setObjectName("Card")
        profile_frame.setStyleSheet("""
            QFrame#Card { 
                background-color: white; 
                border-radius: 12px; 
                border: 1px solid #E0E0E0; 
            }
        """)
        pf_layout = QHBoxLayout(profile_frame)
        pf_layout.setContentsMargins(25, 25, 25, 25)
        pf_layout.setSpacing(20)
        
        lbl_style = "font-weight: bold; color: #666; font-size: 13px;"
        
        # Avatar
        v_av = QVBoxLayout()
        v_av.addWidget(QLabel("AVATAR", styleSheet=lbl_style))
        self.inp_avatar = QComboBox()
        self.inp_avatar.addItems(["😎", "🚀", "🐱", "💻", "🔥", "🧠", "🦁", "🤖", "⭐", "⚡"])
        self.inp_avatar.setFixedSize(80, 45)
        self.inp_avatar.setStyleSheet("QComboBox { padding: 5px; border: 1px solid #CCC; border-radius: 6px; font-size: 20px; } QComboBox::drop-down { border: none; }")
        v_av.addWidget(self.inp_avatar)
        pf_layout.addLayout(v_av)
        
        # Username
        v_nm = QVBoxLayout()
        v_nm.addWidget(QLabel("USERNAME", styleSheet=lbl_style))
        self.inp_username = QLineEdit()
        self.inp_username.setPlaceholderText("Enter your display name")
        self.inp_username.setFixedHeight(45)
        self.inp_username.setStyleSheet("QLineEdit { padding: 0 10px; border: 1px solid #CCC; border-radius: 6px; font-size: 14px; color: #333; } QLineEdit:focus { border: 2px solid #6C5CE7; }")
        v_nm.addWidget(self.inp_username)
        pf_layout.addLayout(v_nm, 1) 
        
        # Save Button
        v_btn = QVBoxLayout()
        v_btn.addWidget(QLabel("", styleSheet=lbl_style)) 
        btn_save = QPushButton("SAVE CHANGES")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setFixedSize(140, 45)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #383838; color: white; 
                font-weight: bold; font-size: 12px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #555; }
        """)
        btn_save.clicked.connect(self.save_profile)
        v_btn.addWidget(btn_save)
        pf_layout.addLayout(v_btn)
        
        self.layout.addWidget(profile_frame)

        # 2. Data Management (Export/Import)
        lbl_data = QLabel("DATA MANAGEMENT")
        lbl_data.setFont(QFont("Oswald", 16, QFont.Weight.Bold))
        lbl_data.setStyleSheet("color: #383838; margin-top: 15px;")
        self.layout.addWidget(lbl_data)

        data_frame = QFrame()
        data_frame.setObjectName("Card")
        data_frame.setStyleSheet("""
            QFrame#Card { background-color: white; border-radius: 12px; border: 1px solid #E0E0E0; }
        """)
        data_layout = QHBoxLayout(data_frame)
        data_layout.setContentsMargins(25, 25, 25, 25)
        data_layout.setSpacing(20)

        # Export
        btn_export = QPushButton("📂 BACKUP DATA (EXPORT)")
        btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_export.setFixedHeight(45)
        btn_export.setStyleSheet("""
            QPushButton { background-color: #00B894; color: white; font-weight: bold; border-radius: 6px; font-size: 12px; }
            QPushButton:hover { background-color: #00A383; }
        """)
        btn_export.clicked.connect(self.export_data)
        
        # Import
        btn_import = QPushButton("♻️ RESTORE DATA (IMPORT)")
        btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_import.setFixedHeight(45)
        btn_import.setStyleSheet("""
            QPushButton { background-color: #E0C068; color: #383838; font-weight: bold; border-radius: 6px; font-size: 12px; }
            QPushButton:hover { background-color: #D4B355; }
        """)
        btn_import.clicked.connect(self.import_data)

        data_layout.addWidget(btn_export)
        data_layout.addWidget(btn_import)
        self.layout.addWidget(data_frame)

        # 3. System Configuration
        lbl_db = QLabel("SYSTEM CONFIGURATION")
        lbl_db.setFont(QFont("Oswald", 16, QFont.Weight.Bold))
        lbl_db.setStyleSheet("color: #383838; margin-top: 15px;")
        self.layout.addWidget(lbl_db)

        grid = QGridLayout()
        grid.setSpacing(20)

        # Categories
        self.cat_list = self.create_table(["ID", "NAME", "ACTION"])
        self.inp_cat_name = self.create_input("Category Name...")
        btn_add_cat = self.create_add_btn(self.add_category_action)
        l_cat = QHBoxLayout(); l_cat.addWidget(self.inp_cat_name); l_cat.addWidget(btn_add_cat)
        grid.addWidget(self.create_card("📂 CATEGORIES", self.cat_list, l_cat), 0, 0)

        # Priorities
        self.prio_list = self.create_table(["ID", "NAME", "LVL", "ACTION"]) 
        self.inp_prio_name = self.create_input("Priority Name...")
        self.inp_prio_lvl = QComboBox(); self.inp_prio_lvl.addItems(["1", "2", "3", "4"]); self.inp_prio_lvl.setFixedSize(50, 36)
        self.inp_prio_lvl.setStyleSheet("border: 1px solid #CCC; border-radius: 5px;")
        btn_add_prio = self.create_add_btn(self.add_priority_action)
        l_prio = QHBoxLayout(); l_prio.addWidget(self.inp_prio_name); l_prio.addWidget(self.inp_prio_lvl); l_prio.addWidget(btn_add_prio)
        grid.addWidget(self.create_card("🔥 PRIORITIES", self.prio_list, l_prio), 0, 1)

        # Statuses
        self.stat_list = self.create_table(["ID", "ICON", "NAME", "ACTION"])
        self.inp_stat_icon = self.create_input("Icon"); self.inp_stat_icon.setFixedWidth(50)
        self.inp_stat_name = self.create_input("Status Name...")
        btn_add_stat = self.create_add_btn(self.add_status_action)
        l_stat = QHBoxLayout(); l_stat.addWidget(self.inp_stat_icon); l_stat.addWidget(self.inp_stat_name); l_stat.addWidget(btn_add_stat)
        grid.addWidget(self.create_card("🔄 STATUSES", self.stat_list, l_stat), 1, 0)

        # Difficulties
        self.diff_list = self.create_table(["ID", "NAME", "XP", "ACTION"])
        self.inp_diff_name = self.create_input("Difficulty...")
        self.inp_diff_score = QComboBox(); self.inp_diff_score.addItems(["1", "2", "3", "5", "8", "10"]); self.inp_diff_score.setFixedSize(50, 36)
        self.inp_diff_score.setStyleSheet("border: 1px solid #CCC; border-radius: 5px;")
        btn_add_diff = self.create_add_btn(self.add_difficulty_action)
        l_diff = QHBoxLayout(); l_diff.addWidget(self.inp_diff_name); l_diff.addWidget(self.inp_diff_score); l_diff.addWidget(btn_add_diff)
        grid.addWidget(self.create_card("💪 HABIT DIFFICULTY", self.diff_list, l_diff), 1, 1)

        self.layout.addLayout(grid)
        self.layout.addStretch()
        
        self.scroll.setWidget(self.content)
        main_l = QVBoxLayout(self)
        main_l.setContentsMargins(0,0,0,0)
        main_l.addWidget(self.scroll)

        # Global input styling
        self.setStyleSheet("""
            QLineEdit { padding: 5px; border: 1px solid #CCC; border-radius: 5px; font-size: 13px; }
            QLineEdit:focus { border: 1px solid #6C5CE7; }
            QComboBox { padding: 5px; border: 1px solid #CCC; border-radius: 5px; }
            QComboBox::drop-down { border: none; }
        """)

    # --- Data Logic ---
    
    def get_db_path(self):
        exe_path = self.api.exe_path
        base_dir = os.path.dirname(exe_path)
        return os.path.join(base_dir, "trackery.db")

    def export_data(self):
        db_path = self.get_db_path()
        if not os.path.exists(db_path):
            QMessageBox.critical(self, "Error", "Database file not found!")
            return

        dest_path, _ = QFileDialog.getSaveFileName(self, "Backup Database", "focusbuddy_backup.db", "SQLite Files (*.db)")
        if dest_path:
            try:
                shutil.copy2(db_path, dest_path)
                QMessageBox.information(self, "Success", "Backup created successfully! 🚀")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {e}")

    def import_data(self):
        reply = QMessageBox.question(self, "Restore Data", 
                                     "⚠️ WARNING: This will overwrite your current data.\n\nAre you sure?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            src_path, _ = QFileDialog.getOpenFileName(self, "Select Backup File", "", "SQLite Files (*.db)")
            if src_path:
                try:
                    db_path = self.get_db_path()
                    
                    # 1. Stop Backend
                    self.api.close()
                    
                    # 2. Replace File
                    shutil.copy2(src_path, db_path)
                    
                    # 3. Restart Backend
                    self.api.init_process()
                    
                    # 4. Refresh UI
                    self.main_window.refresh_all()
                    
                    QMessageBox.information(self, "Success", "Data restored successfully! App reloaded.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to restore: {e}\nPlease restart the app manually.")
                    self.api.init_process()

    # --- UI Helpers ---
    def create_input(self, placeholder):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(36)
        inp.setStyleSheet("padding: 0 10px; border: 1px solid #CCC; border-radius: 5px; font-size: 13px; color: #333;")
        return inp

    def create_add_btn(self, callback):
        btn = QPushButton("+")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedSize(36, 36)
        btn.setStyleSheet("""
            QPushButton { background-color: #6C5CE7; color: white; border-radius: 5px; font-weight: bold; font-size: 16px; }
            QPushButton:hover { background-color: #5A4AD1; }
        """)
        btn.clicked.connect(callback)
        return btn

    def create_card(self, title, table_widget, input_layout):
        frame = QFrame()
        frame.setObjectName("Card") 
        frame.setStyleSheet("""
            QFrame#Card { 
                background-color: white; 
                border-radius: 12px; 
                border: 1px solid #E0E0E0; 
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        lbl = QLabel(title)
        lbl.setFont(QFont("Oswald", 11, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #666; letter-spacing: 0.5px;")
        layout.addWidget(lbl)
        
        layout.addWidget(table_widget)
        
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine); line.setStyleSheet("color: #F0F0F0;")
        layout.addWidget(line)
        
        layout.addLayout(input_layout)
        return frame

    def create_table(self, headers):
        tbl = QTableWidget()
        tbl.setColumnCount(len(headers))
        tbl.setHorizontalHeaderLabels(headers)
        tbl.verticalHeader().setVisible(False)
        tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        tbl.setShowGrid(False)
        tbl.setAlternatingRowColors(True)
        tbl.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        tbl.setStyleSheet("""
            QTableWidget { border: none; font-size: 13px; background-color: transparent; alternate-background-color: #FAFAF9; }
            QHeaderView::section { background-color: white; border: none; border-bottom: 2px solid #F0F0F0; padding: 6px; font-weight: bold; color: #888; text-align: left; }
            QTableWidget::item { padding: 6px; border: none; }
        """)
        
        header = tbl.horizontalHeader()
        header.setStretchLastSection(False)
        for i in range(len(headers)):
            if headers[i] in ["NAME", "ICON"]: 
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            else: 
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        tbl.setMinimumHeight(180)
        return tbl

    # --- Core Logic ---
    def save_profile(self):
        new_name = self.inp_username.text().strip()
        new_avatar = self.inp_avatar.currentText()
        if new_name: self.api.update_username(new_name)
        self.api.set_avatar(new_avatar)
        self.main_window.refresh_all()
        QMessageBox.information(self, "Updated", "Your profile has been updated successfully! ✨")

    def refresh_settings(self):
        self.lookups.load_all()
        
        user = self.api.get_user()
        if user:
            self.inp_username.setText(user.get('username', ''))
            idx = self.inp_avatar.findText(user.get('avatar', '😎'))
            if idx != -1: self.inp_avatar.setCurrentIndex(idx)

        self.fill_table(self.cat_list, self.lookups.categories, ["id", "name"], "Category")
        self.fill_table(self.prio_list, self.lookups.priorities, ["id", "name", "level"], "Priority")
        self.fill_table(self.stat_list, self.lookups.statuses, ["id", "icon", "name"], "Status", locked_ids=[1,2,3,4])
        
        diffs = self.api.get_difficulties()
        self.fill_table(self.diff_list, diffs, ["id", "name", "score"], "Difficulty")

    def fill_table(self, table, data, keys, item_type, locked_ids=None):
        table.setRowCount(0)
        for item in data:
            row = table.rowCount()
            table.insertRow(row)
            for i, key in enumerate(keys):
                val = str(item.get(key, ""))
                table.setItem(row, i, QTableWidgetItem(val))
            
            is_locked = locked_ids and int(item['id']) in locked_ids
            if is_locked:
                lbl = QLabel("🔒")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setStyleSheet("color: #CCC; font-size: 12px;")
                table.setCellWidget(row, len(keys), lbl)
            else:
                btn = QPushButton("×")
                btn.setFixedSize(24, 24)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet("""
                    QPushButton { 
                        color: #D45D5D; border: 1px solid #E0E0E0; border-radius: 4px; background: white; font-weight: bold; padding-bottom: 2px;
                    }
                    QPushButton:hover { background-color: #D45D5D; color: white; border: 1px solid #D45D5D; }
                """)
                btn.clicked.connect(lambda ch, i_id=item['id'], i_type=item_type: self.confirm_delete(i_type, i_id))
                
                w = QWidget(); l = QHBoxLayout(w); l.setContentsMargins(0,0,0,0); l.setAlignment(Qt.AlignmentFlag.AlignCenter); l.addWidget(btn)
                table.setCellWidget(row, len(keys), w)

    def add_category_action(self):
        if self.inp_cat_name.text(): 
            self.api.add_category(self.inp_cat_name.text(), "#CCCCCC")
            self.inp_cat_name.clear(); self.main_window.refresh_all()

    def add_priority_action(self):
        if self.inp_prio_name.text(): 
            self.api.add_priority(self.inp_prio_name.text(), "#CCCCCC", int(self.inp_prio_lvl.currentText()))
            self.inp_prio_name.clear(); self.main_window.refresh_all()

    def add_status_action(self):
        if self.inp_stat_name.text(): 
            self.api.add_status(self.inp_stat_name.text(), self.inp_stat_icon.text())
            self.inp_stat_name.clear(); self.inp_stat_icon.clear(); self.main_window.refresh_all()

    def add_difficulty_action(self):
        if self.inp_diff_name.text():
            self.api.add_difficulty(self.inp_diff_name.text(), int(self.inp_diff_score.currentText()))
            self.inp_diff_name.clear(); self.main_window.refresh_all()

    def confirm_delete(self, item_type, item_id):
        if QMessageBox.question(self, "Confirm", f"Delete this {item_type}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            if item_type == "Category": self.api.del_category(item_id)
            elif item_type == "Priority": self.api.del_priority(item_id)
            elif item_type == "Status": self.api.del_status(item_id)
            elif item_type == "Difficulty": self.api.del_difficulty(item_id)
            self.main_window.refresh_all()