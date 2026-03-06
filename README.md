# FocusBuddy

FocusBuddy is a productivity tracking application that combines a high-performance C++ backend with a Python-based graphical interface. It is designed to help users manage tasks, track habits, and improve concentration through the Pomodoro technique and gamification elements.
<img width="1920" height="1048" alt="image" src="https://github.com/user-attachments/assets/b188e491-e6c0-4e7e-b0ff-85b5de4c7870" />

## Core Features

* **Task Management:** Create and organize tasks with priority levels, categories, and difficulty settings.
* **Habit Tracking:** Monitor daily routines and maintain long-term streaks.
* **Pomodoro Timer:** Integrated focus sessions with session logging.
* **Gamification:** Earn XP and level up an avatar by completing tasks and habits.
* **Statistics:** Visual dashboards and weekly progress reports powered by SQLite.
* **Telegram Integration:** Remote task management via a Python-based bot.

## Tech Stack

* **Backend:** C++ (Core logic and SQLite3 database management).
* **Frontend:** Python (PyQt/PySide for the desktop UI).
* **Database:** SQLite.

---

## Getting Started

### 1. Prerequisites

* A C++ compiler (GCC, Clang, or MSVC) and **CMake**.
* **Python 3.10+**.
* Required Python packages:
```bash
pip install PyQt6 matplotlib requests

```



### 2. Building the C++ Backend

The core logic needs to be compiled before running the UI:

```bash
cd core_cpp
mkdir build
cd build
cmake ..
cmake --build .

```

### 3. Running the Application

Once the backend is ready, start the main interface:

```bash
# From the project root
python ui_python/app.py

```

---

## Project Structure

* `core_cpp/`: Source code for the database manager, entity logic (Tasks, Users, Habits), and C++ repositories.
* `ui_python/`: PyQt-based dashboard, widgets for the Pomodoro timer, and data visualization.
* `telegram_bot/`: Code for the Telegram bot integration.
* `lib/`: External dependencies like SQLite3.

## License

MIT License - feel free to use and modify for your own projects.
