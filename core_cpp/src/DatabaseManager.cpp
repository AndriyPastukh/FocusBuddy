#include "DatabaseManager.h"
#include "repositories/UserRepository.h"
#include "repositories/TaskRepository.h"
#include "repositories/HabitRepository.h"
#include <iostream>

DatabaseManager::DatabaseManager(const std::string& path) {
    if (sqlite3_open(path.c_str(), &db)) {
        std::cerr << "DB Error: " << sqlite3_errmsg(db) << std::endl;
    }
    userRepo = new UserRepository(db);
    taskRepo = new TaskRepository(db);
    habitRepo = new HabitRepository(db);
}

DatabaseManager::~DatabaseManager() {
    delete userRepo;
    delete taskRepo;
    delete habitRepo;
    sqlite3_close(db);
}

bool DatabaseManager::initDB() {
    userRepo->initUser();
    taskRepo->initTasks();
    habitRepo->initHabits();
    return true;
}

// User
bool DatabaseManager::initUser() { return userRepo->initUser(); }
std::string DatabaseManager::getUserJson() { return userRepo->getUserJson(); }
void DatabaseManager::addXP(int amount) { userRepo->addXP(amount); }
void DatabaseManager::setAvatar(std::string s) { userRepo->setAvatar(s); }
void DatabaseManager::completeSession(int m) { userRepo->completeSession(m); }
void DatabaseManager::updateUsername(std::string n) { userRepo->updateUsername(n); }
std::string DatabaseManager::getAchievementsJson() { return userRepo->getAchievementsJson(); }

// Logs
void DatabaseManager::logSession(std::string s, std::string e, int d, int x, int t, std::string tt) { userRepo->logSession(s, e, d, x, t, tt); }
std::string DatabaseManager::getSessionsJson() { return userRepo->getSessionsJson(); }
std::string DatabaseManager::getWeeklyStatsJson() { return userRepo->getWeeklyStatsJson(); }

// Tasks
std::string DatabaseManager::getCategoriesJson() { return taskRepo->getCategoriesJson(); }
std::string DatabaseManager::getPrioritiesJson() { return taskRepo->getPrioritiesJson(); }
std::string DatabaseManager::getStatusesJson() { return taskRepo->getStatusesJson(); }
void DatabaseManager::addTask(std::string t, std::string td, std::string dd, std::string dt, int c, int p, std::string col) { taskRepo->addTask(t, td, dd, dt, c, p, col); }
void DatabaseManager::editTask(int id, std::string t, std::string td, std::string dd, std::string dt, int c, int p, std::string col) { taskRepo->editTask(id, t, td, dd, dt, c, p, col); }
void DatabaseManager::deleteTask(int id) { taskRepo->remove(id); } // <--- ДОДАНО!
void DatabaseManager::updateTaskStatus(int id, int s, int c) { taskRepo->updateTaskStatus(id, s, c); }
void DatabaseManager::updateTaskStatusId(int id, int s) { taskRepo->updateTaskStatusId(id, s, userRepo); }
void DatabaseManager::updateTaskCategory(int id, int c) { taskRepo->updateTaskCategory(id, c); }
void DatabaseManager::updateTaskPriority(int id, int p) { taskRepo->updateTaskPriority(id, p); }
void DatabaseManager::checkDeadlines() { taskRepo->checkDeadlines(); }
std::string DatabaseManager::getTasksJson(std::string f) { return taskRepo->getTasksJson(f); }
std::string DatabaseManager::getTasksByMonth(std::string m) { return taskRepo->getTasksByMonth(m); }
std::string DatabaseManager::getTasksForToday() { return taskRepo->getTasksForToday(); }
std::string DatabaseManager::getTasksForTomorrow() { return taskRepo->getTasksForTomorrow(); }
std::string DatabaseManager::getOverdueTasksDetailed() { return taskRepo->getOverdueTasksDetailed(); }
std::string DatabaseManager::getDashboardStats() { return taskRepo->getDashboardStats(); }
std::string DatabaseManager::getChartData(std::string t) { return taskRepo->getChartData(t); }

// Settings
void DatabaseManager::addCategory(std::string n, std::string c) { taskRepo->addCategory(n, c); }
void DatabaseManager::deleteCategory(int id) { taskRepo->deleteCategory(id); }
void DatabaseManager::addPriority(std::string n, std::string c, int l) { taskRepo->addPriority(n, c, l); }
void DatabaseManager::deletePriority(int id) { taskRepo->deletePriority(id); }
void DatabaseManager::addStatus(std::string n, std::string i) { taskRepo->addStatus(n, i); }
void DatabaseManager::deleteStatus(int id) { taskRepo->deleteStatus(id); }

// Habits
void DatabaseManager::addHabit(std::string t, int d) { habitRepo->addHabit(t, d); }
void DatabaseManager::updateHabit(int id, std::string t, int d) { habitRepo->updateHabit(id, t, d); }
void DatabaseManager::deleteHabit(int id) { habitRepo->deleteHabit(id); }
void DatabaseManager::toggleHabitDate(int id, std::string d) { habitRepo->toggleHabitDate(id, d, userRepo); }
std::string DatabaseManager::getHabitGridJson(std::string m) { return habitRepo->getHabitGridJson(m); }
std::string DatabaseManager::getHabitScoreStats(std::string m) { return habitRepo->getHabitScoreStats(m); }
std::string DatabaseManager::getDifficultiesJson() { return habitRepo->getDifficultiesJson(); }
void DatabaseManager::addDifficulty(std::string n, int s) { habitRepo->addDifficulty(n, s); }
void DatabaseManager::deleteDifficulty(int id) { habitRepo->deleteDifficulty(id); }

// Reflections
void DatabaseManager::setDailyReflection(std::string d, int m, int e, int mo) { habitRepo->setDailyReflection(d, m, e, mo); }
std::string DatabaseManager::getDailyReflections(std::string m) { return habitRepo->getDailyReflections(m); }

// Goals
void DatabaseManager::addGoal(std::string t, std::string d, std::string da, std::string w, std::string m, int c) { habitRepo->addGoal(t, d, da, w, m, c); }
void DatabaseManager::updateGoal(int id, std::string t, std::string d, std::string da, std::string w, std::string m, int c) { habitRepo->updateGoal(id, t, d, da, w, m, c); }
void DatabaseManager::toggleGoal(int id) { habitRepo->toggleGoal(id); }
void DatabaseManager::deleteGoal(int id) { habitRepo->deleteGoal(id); }
std::string DatabaseManager::getGoalsJson() { return habitRepo->getGoalsJson(); }

// Payload
std::string DatabaseManager::getHomePayload() {
    std::string json = "{";
    json += "\"user\": " + userRepo->getUserJson() + ",";
    json += "\"dashboard\": " + taskRepo->getDashboardStats() + ",";
    json += "\"weekly_stats\": " + userRepo->getWeeklyStatsJson() + ",";
    json += "\"prio_chart\": " + taskRepo->getChartData("priority") + ",";
    json += "\"overdue\": " + taskRepo->getOverdueTasksDetailed() + ",";
    json += "\"today\": " + taskRepo->getTasksForToday() + ",";
    json += "\"tomorrow\": " + taskRepo->getTasksForTomorrow() + ",";
    
    time_t t = time(nullptr);
    tm* now = localtime(&t);
    char buf[10];
    strftime(buf, sizeof(buf), "%Y-%m", now);
    json += "\"habits\": " + habitRepo->getHabitGridJson(std::string(buf));
    json += "}";
    return json;
}