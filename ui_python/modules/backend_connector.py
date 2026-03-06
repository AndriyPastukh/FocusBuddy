import subprocess
import os
import json
import atexit
import sys

class BackendConnector:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BackendConnector, cls).__new__(cls)
            cls._instance.init_process()
        return cls._instance

    def init_process(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        possible_paths = [
            os.path.join(current_dir, "..", "core_cpp", "bin", "core.exe"),
            
            os.path.join(current_dir, "..", "..", "core_cpp", "bin", "core.exe"),
            
            os.path.join(current_dir, "..", "bin", "core.exe"),
            
            os.path.join(current_dir, "core.exe"),


        ]

        self.exe_path = None

        for path in possible_paths:
            normalized_path = os.path.normpath(path) 
            if os.path.exists(normalized_path):
                self.exe_path = normalized_path
                break
        
        if self.exe_path:
            print(f"DEBUG: Found core.exe at: {self.exe_path}")
        else:
            print("CRITICAL: core.exe not found in any expected location!")
            print(f"Searched in: {[os.path.normpath(p) for p in possible_paths]}")
            self.process = None
            return

        my_env = os.environ.copy()
        my_env["PYTHONIOENCODING"] = "utf-8"
        
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        try:
            self.process = subprocess.Popen(
                [self.exe_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=0,
                startupinfo=startupinfo,
                env=my_env
            )
            atexit.register(self.close)
            print("DEBUG: Backend connected successfully.")
        except Exception as e:
            print(f"DEBUG: Connection failed: {e}")
            self.process = None

    def close(self):
        if self.process:
            try:
                self.process.stdin.write("EXIT\n")
                self.process.terminate()
            except: pass
            self.process = None

    def _send_command(self, cmd_str):
        if not self.process:
            self.init_process()
            if not self.process: return {}

        try:
            self.process.stdin.write(cmd_str + "\n")
            self.process.stdin.flush()
            output = self.process.stdout.readline()
            
            if not output: 
                print("C++ Backend crashed or returned nothing!")
                return {}

            return json.loads(output.strip())
        except Exception as e:
            print(f"Error communicating: {e}")
            return {}

    def _run(self, args):
        if len(args) > 0:
            cmd = args[0].replace("--", "")
            params = "|".join(str(x) for x in args[1:]) # str(x) is safer
            return self._send_command(f"{cmd}|{params}")
        return {}

    # === API METHODS ===

    def get_tasks_by_month(self, month_str): return self._send_command(f"getTasksByMonth|{month_str}")
    def get_home_payload(self): return self._send_command("getHomePayload")
    
    def get_tasks(self, filter_type="all"): return self._send_command(f"getTasks|{filter_type}")
    def add_task(self, t, d, dd, dt, c, p, col): self._send_command(f"addTask|{t}|{d}|{dd}|{dt}|{c}|{p}|{col}")
    def edit_task(self, id, t, d, dd, dt, c, p, col): self._send_command(f"editTask|{id}|{t}|{d}|{dd}|{dt}|{c}|{p}|{col}")
    def complete_task(self, id): self._send_command(f"completeTask|{id}")
    def update_task_status(self, id, s): self._send_command(f"setTaskStatus|{id}|{s}")
    def update_task_cat(self, id, c): self._send_command(f"setTaskCat|{id}|{c}")
    def update_task_prio(self, id, p): self._send_command(f"setTaskPrio|{id}|{p}")
    
    def get_today_tasks(self): return self._send_command("getTodayTasks")
    def get_tomorrow_tasks(self): return self._send_command("getTomorrow")
    def get_overdue_tasks(self): return self._send_command("getOverdue")

    def get_habit_grid(self, m): return self._send_command(f"getHabitGrid|{m}")
    def add_habit(self, t, d): self._send_command(f"addHabit|{t}|{d}")
    def toggle_habit_date(self, id, date): self._send_command(f"toggleHabit|{id}|{date}")
    def edit_habit(self, id, t, d): self._send_command(f"editHabit|{id}|{t}|{d}")
    def del_habit(self, id): self._send_command(f"delHabit|{id}")
    def get_habit_score_stats(self, m): return self._send_command(f"getHabitScoreStats|{m}")
    def get_reflections(self, m): return self._send_command(f"getReflections|{m}")
    def set_reflection(self, d, m, e, mot): self._send_command(f"setReflection|{d}|{m}|{e}|{mot}")

    def get_goals(self): return self._send_command("getGoals")
    def add_goal(self, t, d, da, w, m, c): self._send_command(f"addGoal|{t}|{d}|{da}|{w}|{m}|{c}")
    def edit_goal(self, id, t, d, da, w, m, c): self._send_command(f"editGoal|{id}|{t}|{d}|{da}|{w}|{m}|{c}")
    def toggle_goal(self, id): self._send_command(f"toggleGoal|{id}")
    def del_goal(self, id): self._send_command(f"delGoal|{id}")

    def get_user(self): 
        r = self._send_command("getUser")
        return r[0] if isinstance(r, list) and r else {}
    
    def get_lookups(self): return self._send_command("getLookups")
    def get_difficulties(self): return self._send_command("getDifficulties")
    
    def add_category(self, n, c): self._send_command(f"addCategory|{n}|{c}")
    def del_category(self, id): self._send_command(f"delCategory|{id}")
    def add_priority(self, n, c, l): self._send_command(f"addPriority|{n}|{c}|{l}")
    def del_priority(self, id): self._send_command(f"delPriority|{id}")
    def add_status(self, n, i): self._send_command(f"addStatus|{n}|{i}")
    def del_status(self, id): self._send_command(f"delStatus|{id}")
    def add_difficulty(self, n, s): self._send_command(f"addDifficulty|{n}|{s}")
    def del_difficulty(self, id): self._send_command(f"delDifficulty|{id}")

    def get_dashboard_stats(self): return self._send_command("getDashboard")
    def get_chart_data(self, t): return self._send_command(f"getChart|{t}")
    def get_weekly_stats(self): return self._send_command("getWeeklyStats")
    
    def add_xp(self, a): self._send_command(f"addXP|{a}")
    def set_avatar(self, s): self._send_command(f"setAvatar|{s}")
    def log_session(self, s, e, d, x, ti, tt): self._send_command(f"logSession|{s}|{e}|{d}|{x}|{ti}|{tt}")
    def get_sessions(self): return self._send_command("getSessions")
    def complete_session(self, m): self._send_command(f"completeSession|{m}")
    def update_username(self, name): self._send_command(f"updateUsername|{name}")
        
    def get_achievements(self): return self._send_command("getAchievements")
    def update_task_prio(self, id, p): self._send_command(f"setTaskPrio|{id}|{p}")
    def delete_task(self, id): self._send_command(f"deleteTask|{id}")