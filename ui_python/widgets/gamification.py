from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QFrame, QGridLayout, QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

class GamificationWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.api = main_window.api
        
        # Setup Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        
        content = QWidget()
        self.layout = QVBoxLayout(content)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(30)
        
        # --- 1. PROFILE HERO CARD ---
        profile_card = QFrame()
        profile_card.setObjectName("Card")
        profile_card.setStyleSheet("""
            QFrame#Card { 
                background-color: white; 
                border-radius: 16px; 
                border: 1px solid #E0E0E0;
            }
        """)
        
        pc_layout = QHBoxLayout(profile_card)
        pc_layout.setContentsMargins(30, 30, 30, 30)
        pc_layout.setSpacing(25)
        
        # Avatar
        self.avatar_lbl = QLabel("😎")
        self.avatar_lbl.setFixedSize(100, 100)
        self.avatar_lbl.setFont(QFont("Segoe UI Emoji", 60))
        self.avatar_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_lbl.setStyleSheet("background-color: #F8F9FA; border-radius: 50px;")
        pc_layout.addWidget(self.avatar_lbl)
        
        # Stats Info
        stats_v = QVBoxLayout()
        self.name_lbl = QLabel("Hero")
        self.name_lbl.setFont(QFont("Oswald", 24, QFont.Weight.Bold))
        self.name_lbl.setStyleSheet("color: #2D3436;")
        
        self.lvl_lbl = QLabel("Level 1")
        self.lvl_lbl.setStyleSheet("color: #6C5CE7; font-weight: bold; font-size: 16px; margin-bottom: 5px;")
        
        self.xp_bar = QProgressBar()
        self.xp_bar.setFixedHeight(12)
        self.xp_bar.setStyleSheet("""
            QProgressBar { border-radius: 6px; background-color: #F0F0F0; text-align: center; }
            QProgressBar::chunk { border-radius: 6px; background-color: qlineargradient(stop:0 #6C5CE7, stop:1 #a29bfe); }
        """)
        self.xp_text = QLabel("0 / 100 XP")
        self.xp_text.setStyleSheet("color: #888; font-size: 12px; margin-top: 5px;")
        self.xp_text.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        stats_v.addWidget(self.name_lbl)
        stats_v.addWidget(self.lvl_lbl)
        stats_v.addWidget(self.xp_bar)
        stats_v.addWidget(self.xp_text)
        
        pc_layout.addLayout(stats_v)
        self.layout.addWidget(profile_card)
        
        # --- 2. ACHIEVEMENTS SECTION ---
        lbl_ach = QLabel("🏆 ACHIEVEMENTS HALL")
        lbl_ach.setFont(QFont("Oswald", 16, QFont.Weight.Bold))
        lbl_ach.setStyleSheet("color: #383838; margin-top: 10px;")
        self.layout.addWidget(lbl_ach)
        
        # Grid for achievements
        self.ach_grid = QGridLayout()
        self.ach_grid.setSpacing(20)
        self.layout.addLayout(self.ach_grid)
        
        self.layout.addStretch()
        
        scroll.setWidget(content)
        main_l = QVBoxLayout(self)
        main_l.setContentsMargins(0,0,0,0)
        main_l.addWidget(scroll)

    def refresh_profile(self):
        # 1. Update user data
        user = self.api.get_user()
        if user:
            self.name_lbl.setText(user.get('username', 'Hero'))
            self.lvl_lbl.setText(f"Level {user.get('level', 1)}")
            self.avatar_lbl.setText(user.get('avatar', '😎'))
            
            xp = int(user.get('xp', 0))
            lvl = int(user.get('level', 1))
            needed = lvl * 100
            
            self.xp_bar.setMaximum(needed)
            self.xp_bar.setValue(xp)
            self.xp_text.setText(f"{xp} / {needed} XP")

        # 2. Update achievements
        self.load_achievements()

    def load_achievements(self):
        while self.ach_grid.count():
            item = self.ach_grid.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        achievements = self.api.get_achievements()
        if not achievements: return

        row, col = 0, 0
        for ach in achievements:
            card = self.create_ach_card(ach)
            self.ach_grid.addWidget(card, row, col)
            
            col += 1
            if col > 1: # 2 columns
                col = 0
                row += 1

    def create_ach_card(self, ach):
        frame = QFrame()
        is_unlocked = str(ach['unlocked']) == "1"
        
        bg_color = "white" if is_unlocked else "#FAFAFA"
        border_color = "#6C5CE7" if is_unlocked else "#E0E0E0"
        opacity = "1.0" if is_unlocked else "0.6"
        
        frame.setStyleSheet(f"""
            QFrame {{ 
                background-color: {bg_color}; 
                border: 2px solid {border_color}; 
                border-radius: 12px;
            }}
        """)
        frame.setFixedHeight(100)
        
        l = QHBoxLayout(frame)
        l.setContentsMargins(15, 15, 15, 15)
        
        # Icon
        icon_lbl = QLabel(ach['icon'])
        icon_lbl.setFont(QFont("Segoe UI Emoji", 32))
        icon_lbl.setStyleSheet(f"border: none; background: transparent; opacity: {opacity};")
        icon_lbl.setFixedWidth(60)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Text Info
        text_v = QVBoxLayout()
        title = QLabel(ach['title'])
        title.setFont(QFont("Oswald", 12, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {'#333' if is_unlocked else '#999'}; border: none;")
        
        desc = QLabel(ach['desc'])
        desc.setFont(QFont("Segoe UI", 10))
        desc.setStyleSheet("color: #888; border: none;")
        desc.setWordWrap(True)
        
        text_v.addWidget(title)
        text_v.addWidget(desc)
        
        l.addWidget(icon_lbl)
        l.addLayout(text_v)
        
        if not is_unlocked:
            lock = QLabel("🔒")
            lock.setStyleSheet("border: none; font-size: 16px;")
            l.addWidget(lock)
            
        return frame