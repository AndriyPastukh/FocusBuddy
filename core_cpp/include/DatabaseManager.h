#ifndef DATABASEMANAGER_H
#define DATABASEMANAGER_H

#include <string>
#include <vector>
#include "sqlite3.h"

class UserRepository;
class TaskRepository;
class HabitRepository;

class DatabaseManager {
public:
    DatabaseManager(const std::string& dbPath);
    ~DatabaseManager();
    bool initDB();
    std::string getHomePayload(); 

    // User
    bool initUser();
    std::string getUserJson();
    void addXP(int amount);
    void setAvatar(std::string avatarSymbol);
    void completeSession(int minutes); 
    void updateUsername(std::string newName); 
    std::string getAchievementsJson();

    // Logs
    void logSession(std::string start, std::string end, int duration, int xp, int taskId, std::string taskTitle);
    std::string getSessionsJson();
    std::string getWeeklyStatsJson();

    // Lookups
    std::string getCategoriesJson();
    std::string getPrioritiesJson();
    std::string getStatusesJson();
    
    // Tasks
    void addTask(std::string title, std::string todoDate, std::string deadlineDate, std::string deadlineTime, int catId, int prioId, std::string color);
    void editTask(int id, std::string title, std::string todoDate, std::string deadlineDate, std::string deadlineTime, int catId, int prioId, std::string color);
    void deleteTask(int id); // <--- ДОДАНО!
    
    void updateTaskStatus(int taskId, int statusId, int isCompleted);
    void updateTaskStatusId(int taskId, int statusId); 
    void updateTaskCategory(int taskId, int catId);
    void updateTaskPriority(int taskId, int prioId);
    void checkDeadlines();
    std::string getTasksJson(std::string filter);
    std::string getTasksByMonth(std::string monthPrefix);   
    std::string getTasksForToday();
    std::string getTasksForTomorrow();
    std::string getOverdueTasksDetailed();

    // Habits
    void addHabit(std::string title, int difficultyId);
    void updateHabit(int id, std::string title, int difficultyId); 
    void deleteHabit(int id);                              
    void toggleHabitDate(int habitId, std::string date);
    std::string getHabitGridJson(std::string month);
    std::string getHabitScoreStats(std::string month);

    // Reflections
    void setDailyReflection(std::string date, int mood, int energy, int motiv);
    std::string getDailyReflections(std::string month);

    // Analytics
    std::string getDashboardStats();
    std::string getChartData(std::string type);

    // Settings
    void addCategory(std::string name, std::string color);
    void deleteCategory(int id);
    void addPriority(std::string name, std::string color, int level);
    void deletePriority(int id);
    void addStatus(std::string name, std::string icon);
    void deleteStatus(int id);
    void addDifficulty(std::string name, int score);
    void deleteDifficulty(int id);
    std::string getDifficultiesJson();

    // Goals
    void addGoal(std::string title, std::string deadline, std::string daily, std::string weekly, std::string monthly, int catId);
    void updateGoal(int id, std::string title, std::string deadline, std::string daily, std::string weekly, std::string monthly, int catId);
    void toggleGoal(int id);
    void deleteGoal(int id);
    std::string getGoalsJson();

private:
    sqlite3* db;
    UserRepository* userRepo;
    TaskRepository* taskRepo;
    HabitRepository* habitRepo;
};

#endif