import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QSpinBox, QMessageBox, QApplication,
    QProgressBar, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtMultimedia import QSoundEffect

from dialogs import TaskSelectDialog, HistoryDialog

class PomodoroWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.api = main_window.api
        
        # Audio Setup
        self.sound_effect = QSoundEffect()
        sound_path = os.path.abspath("assets/notification.wav") 
        if os.path.exists(sound_path):
            self.sound_effect.setSource(QUrl.fromLocalFile(sound_path))
            self.sound_effect.setVolume(1.0)

        # Timer State
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.is_running = False
        
        self.total_seconds = 25 * 60
        self.current_seconds = self.total_seconds
        self.mode = "FOCUS" 
        
        # Session Data
        self.start_timestamp = None
        self.selected_task = None 

        # --- UI LAYOUT ---
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(10, 10, 10, 10)

        # Main Card
        card = QFrame()
        card.setObjectName("Card")
        card.setFixedSize(480, 620)
        card.setStyleSheet("""
            QFrame#Card { 
                background-color: white; 
                border-radius: 20px; 
                border: 1px solid #E0E0E0;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20); shadow.setYOffset(5); shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)
        
        l = QVBoxLayout(card)
        l.setSpacing(15)
        l.setContentsMargins(30, 25, 30, 25)

        # 1. Header Label
        self.lbl_mode = QLabel("DEEP FOCUS SESSION")
        self.lbl_mode.setFont(QFont("Oswald", 14, QFont.Weight.Bold))
        self.lbl_mode.setStyleSheet("color: #6C5CE7; letter-spacing: 2px; background-color: #F3F0FF; padding: 5px 10px; border-radius: 5px;")
        self.lbl_mode.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.lbl_mode, alignment=Qt.AlignmentFlag.AlignHCenter)

        # 2. Task Selector
        self.task_frame = QFrame()
        self.task_frame.setStyleSheet("background-color: #FAFAF9; border-radius: 8px; border: 1px dashed #CCC;")
        tf_layout = QHBoxLayout(self.task_frame)
        tf_layout.setContentsMargins(10, 5, 10, 5)
        
        self.lbl_current_task = QLabel("No task selected")
        self.lbl_current_task.setStyleSheet("color: #555; font-style: italic; border: none;")
        self.lbl_current_task.setWordWrap(True)
        
        btn_pick_task = QPushButton("🎯 Select Task")
        btn_pick_task.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_pick_task.setFixedSize(90, 25)
        btn_pick_task.setStyleSheet("background-color: white; border: 1px solid #CCC; border-radius: 4px; font-weight: bold; font-size: 10px;")
        btn_pick_task.clicked.connect(self.open_task_selector)
        
        tf_layout.addWidget(self.lbl_current_task)
        tf_layout.addWidget(btn_pick_task)
        l.addWidget(self.task_frame)

        # 3. Timer Display
        self.lbl_time = QLabel("25:00")
        self.lbl_time.setFont(QFont("Oswald", 90, QFont.Weight.Bold))
        self.lbl_time.setStyleSheet("color: #383838; margin-top: -5px;")
        self.lbl_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.addWidget(self.lbl_time)

        # 4. Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, self.total_seconds)
        self.progress_bar.setValue(self.total_seconds)
        self.progress_bar.setStyleSheet("""
            QProgressBar { border: none; background-color: #F0F0F0; border-radius: 3px; }
            QProgressBar::chunk { background-color: #6C5CE7; border-radius: 3px; }
        """)
        l.addWidget(self.progress_bar)

        l.addSpacing(5)

        # 5. Mode Buttons
        modes_layout = QHBoxLayout()
        modes_layout.setSpacing(10)
        self.btn_focus = self.create_mode_btn("🔥 Focus 25", 25, True)
        self.btn_short = self.create_mode_btn("☕ Short 5", 5)
        self.btn_long = self.create_mode_btn("💤 Long 15", 15)
        modes_layout.addWidget(self.btn_focus)
        modes_layout.addWidget(self.btn_short)
        modes_layout.addWidget(self.btn_long)
        l.addLayout(modes_layout)

        # 6. Custom Timer
        custom_layout = QHBoxLayout()
        custom_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_custom = QSpinBox()
        self.spin_custom.setRange(1, 180)
        self.spin_custom.setValue(45)
        self.spin_custom.setFixedWidth(60)
        
        btn_apply = QPushButton("✔")
        btn_apply.setFixedSize(30, 26)
        btn_apply.clicked.connect(self.set_custom_time)
        
        custom_layout.addWidget(QLabel("Custom (min):"))
        custom_layout.addWidget(self.spin_custom)
        custom_layout.addWidget(btn_apply)
        l.addLayout(custom_layout)

        l.addSpacing(10)

        # 7. Controls (Start/Reset)
        ctrl_layout = QHBoxLayout()
        self.btn_start = QPushButton("START TIMER")
        self.btn_start.setFixedHeight(55)
        self.btn_start.setStyleSheet("background-color: #383838; color: white; border-radius: 27px; font-weight: bold; font-size: 16px;")
        self.btn_start.clicked.connect(self.toggle_timer)
        
        self.btn_reset = QPushButton("RESET")
        self.btn_reset.setFixedSize(80, 55)
        self.btn_reset.setStyleSheet("background-color: white; color: #888; border: 2px solid #EEE; border-radius: 27px; font-weight: bold;")
        self.btn_reset.clicked.connect(self.reset_timer)
        
        ctrl_layout.addWidget(self.btn_start)
        ctrl_layout.addWidget(self.btn_reset)
        l.addLayout(ctrl_layout)

        l.addStretch()

        # 8. History Link
        btn_history = QPushButton("📋 View All Sessions")
        btn_history.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_history.setStyleSheet("background-color: transparent; color: #6C5CE7; border: none; font-weight: bold; text-decoration: underline;")
        btn_history.clicked.connect(self.open_history)
        l.addWidget(btn_history, alignment=Qt.AlignmentFlag.AlignCenter)

        # 9. Stats Footer
        stats_layout = QHBoxLayout()
        self.stat_sessions_val = QLabel("0")
        self.stat_sessions_val.setFont(QFont("Oswald", 18, QFont.Weight.Bold))
        self.stat_hours_val = QLabel("0.0")
        self.stat_hours_val.setFont(QFont("Oswald", 18, QFont.Weight.Bold))
        
        stats_layout.addStretch()
        v1 = QVBoxLayout(); v1.addWidget(self.stat_sessions_val, alignment=Qt.AlignmentFlag.AlignCenter); v1.addWidget(QLabel("SESSIONS"))
        v2 = QVBoxLayout(); v2.addWidget(self.stat_hours_val, alignment=Qt.AlignmentFlag.AlignCenter); v2.addWidget(QLabel("HOURS"))
        stats_layout.addLayout(v1)
        stats_layout.addSpacing(20)
        stats_layout.addLayout(v2)
        stats_layout.addStretch()
        l.addLayout(stats_layout)

        layout.addWidget(card)
        self.refresh_stats()

    # --- LOGIC ---

    def open_task_selector(self):
        all_tasks = self.api._run(["--getTasks", "all"])
        dlg = TaskSelectDialog(all_tasks)
        if dlg.exec():
            task = dlg.get_data()
            if task:
                self.selected_task = task
                self.lbl_current_task.setText(f"Working on: {task['title']}")
                self.lbl_current_task.setStyleSheet("color: #383838; font-weight: bold; border: none;")

    def open_history(self):
        sessions = self.api.get_sessions()
        dlg = HistoryDialog(sessions)
        dlg.exec()

    def toggle_timer(self):
        if self.is_running:
            self.timer.stop()
            self.btn_start.setText("RESUME")
            self.btn_start.setStyleSheet("background-color: #E0C068; color: #383838; border-radius: 27px; font-weight: bold; font-size: 16px;")
            self.start_timestamp = None 
        else:
            self.timer.start(1000)
            self.btn_start.setText("PAUSE")
            self.btn_start.setStyleSheet("background-color: #E0C068; color: #383838; border-radius: 27px; font-weight: bold; font-size: 16px;")
            if self.start_timestamp is None:
                self.start_timestamp = datetime.now()
        
        self.is_running = not self.is_running

    def update_timer(self):
        self.current_seconds -= 1
        self.progress_bar.setValue(self.current_seconds)
        m = self.current_seconds // 60
        s = self.current_seconds % 60
        self.lbl_time.setText(f"{m:02d}:{s:02d}")
        
        if self.current_seconds <= 0:
            self.finish_session()

    def finish_session(self):
        self.timer.stop()
        self.is_running = False
        self.current_seconds = 0
        QApplication.beep()
        if not self.sound_effect.source().isEmpty():
            self.sound_effect.play()
        
        minutes_done = self.total_seconds // 60
        
        if self.mode == "FOCUS":
            # XP Calculation (1 min = 3 XP)
            xp_earned = minutes_done * 3
            
            end_time = datetime.now()
            start_str = self.start_timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.start_timestamp else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
            
            t_id = int(self.selected_task['id']) if self.selected_task else 0
            t_title = self.selected_task['title'] if self.selected_task else "No task selected"
            
            # Send to Backend
            self.api.log_session(start_str, end_str, minutes_done, xp_earned, t_id, t_title)
            
            # Refresh UI
            if hasattr(self.main_window, 'gamification_widget'):
                self.main_window.gamification_widget.refresh_profile()
            if hasattr(self.main_window, 'refresh_all'):
                self.main_window.refresh_all()
            
            self.refresh_stats()
            QMessageBox.information(self, "Session Complete!", f"Awesome! +{xp_earned} XP earned.\nLog saved.")
        else:
            QMessageBox.information(self, "Break Over", "Time to focus!")

        self.reset_timer()

    def reset_timer(self):
        self.timer.stop()
        self.is_running = False
        
        # Restore time based on mode
        if "CUSTOM" in self.lbl_mode.text(): self.set_custom_time()
        elif "SHORT" in self.lbl_mode.text(): self.current_seconds = 5 * 60
        elif "LONG" in self.lbl_mode.text(): self.current_seconds = 15 * 60
        else: self.current_seconds = 25 * 60
        
        self.total_seconds = self.current_seconds
        self.progress_bar.setRange(0, self.total_seconds)
        self.progress_bar.setValue(self.total_seconds)
        
        m = self.current_seconds // 60
        s = self.current_seconds % 60
        self.lbl_time.setText(f"{m:02d}:{s:02d}")
        
        self.btn_start.setText("START TIMER")
        self.btn_start.setStyleSheet("background-color: #383838; color: white; border-radius: 27px; font-weight: bold; font-size: 16px;")
        self.start_timestamp = None

    def create_mode_btn(self, text, mins, is_active=False):
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFixedHeight(40)
        base_style = "border-radius: 20px; font-size: 13px; font-weight: bold; padding: 0 15px;"
        
        if is_active:
            btn.setStyleSheet(f"background-color: #E8DFF5; color: #6C5CE7; border: 1px solid #6C5CE7; {base_style}")
        else:
            btn.setStyleSheet(f"background-color: white; color: #666; border: 1px solid #DDD; {base_style}")
            
        btn.clicked.connect(lambda: self.set_mode(mins, btn))
        return btn

    def set_mode(self, mins, btn_sender):
        if self.is_running: return 
        
        self.total_seconds = mins * 60
        self.current_seconds = self.total_seconds
        self.progress_bar.setRange(0, self.total_seconds)
        self.progress_bar.setValue(self.total_seconds)
        
        m = self.current_seconds // 60
        s = self.current_seconds % 60
        self.lbl_time.setText(f"{m:02d}:{s:02d}")
        
        # Reset button styles
        for b in [self.btn_focus, self.btn_short, self.btn_long]:
            b.setStyleSheet("background-color: white; color: #666; border: 1px solid #DDD; border-radius: 20px; font-size: 13px; font-weight: bold; padding: 0 15px;")
        
        btn_sender.setStyleSheet("background-color: #E8DFF5; color: #6C5CE7; border: 1px solid #6C5CE7; border-radius: 20px; font-size: 13px; font-weight: bold; padding: 0 15px;")
        
        # Mode-specific styling
        if mins == 25: 
            self.lbl_mode.setText("DEEP FOCUS SESSION")
            self.mode = "FOCUS"
            self.lbl_mode.setStyleSheet("color: #6C5CE7; letter-spacing: 2px; background-color: #F3F0FF; padding: 5px 10px; border-radius: 5px;")
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #6C5CE7; border-radius: 3px; } QProgressBar { background-color: #F0F0F0; border-radius: 3px; border: none; }")
        elif mins == 5: 
            self.lbl_mode.setText("SHORT BREAK")
            self.mode = "SHORT"
            self.lbl_mode.setStyleSheet("color: #E0C068; letter-spacing: 2px; background-color: #FFF9E6; padding: 5px 10px; border-radius: 5px;")
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #E0C068; border-radius: 3px; } QProgressBar { background-color: #F0F0F0; border-radius: 3px; border: none; }")
        elif mins == 15: 
            self.lbl_mode.setText("LONG BREAK")
            self.mode = "LONG"
            self.lbl_mode.setStyleSheet("color: #7FB06F; letter-spacing: 2px; background-color: #E8F5E9; padding: 5px 10px; border-radius: 5px;")
            self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #7FB06F; border-radius: 3px; } QProgressBar { background-color: #F0F0F0; border-radius: 3px; border: none; }")

    def set_custom_time(self):
        if self.is_running: return
        mins = self.spin_custom.value()
        self.total_seconds = mins * 60
        self.current_seconds = self.total_seconds
        
        self.progress_bar.setRange(0, self.total_seconds)
        self.progress_bar.setValue(self.total_seconds)
        self.lbl_mode.setText(f"CUSTOM SESSION ({mins} MIN)")
        self.mode = "FOCUS"
        
        m = self.current_seconds // 60
        s = self.current_seconds % 60
        self.lbl_time.setText(f"{m:02d}:{s:02d}")

    def refresh_stats(self):
        user = self.api.get_user()
        if user:
            total_poms = user.get('total_pomodoros', 0)
            total_mins = user.get('total_minutes', 0)
            hours = round(int(total_mins) / 60, 1)
            
            self.stat_sessions_val.setText(str(total_poms))
            self.stat_hours_val.setText(str(hours))