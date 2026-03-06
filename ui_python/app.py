import sys
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == "__main__":
    print("🚀 1. App start....")
    app = QApplication(sys.argv)
    
    print("🖼️ 2. Creacting window...")
    try:
        w = MainWindow()
        print("✅ 3.window created successfully.  Setting up UI...")
        
        w.show()
        print("👀 4.  show() executed successfully. Entering app ")
        
        sys.exit(app.exec())
    except Exception as e:
        print(f"❌ Critical Error {e}")
        import traceback
        traceback.print_exc()