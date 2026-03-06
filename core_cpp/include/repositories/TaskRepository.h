#ifndef TASK_REPOSITORY_H
#define TASK_REPOSITORY_H

#include <string>
#include <vector>
#include "sqlite3.h" 

class UserRepository; 

class TaskRepository {
    sqlite3* db;
    void executeQuery(const std::string& query);
    std::string queryJson(const std::string& query);
    std::string getToday();

public:
    TaskRepository(sqlite3* db);
    bool initTasks();
    
    // Lookups
    std::string getCategoriesJson();
    std::string getPrioritiesJson();
    std::string getStatusesJson();
    
    // Tasks CRUD
    void addTask(std::string title, std::string todoDate, std::string deadlineDate, std::string deadlineTime, int catId, int prioId, std::string color);
    void editTask(int id, std::string title, std::string todoDate, std::string deadlineDate, std::string deadlineTime, int catId, int prioId, std::string color);
    
    void remove(int id); // <--- ДОДАНО ЦЕЙ МЕТОД
    
    void updateTaskStatus(int taskId, int statusId, int isCompleted);
    void updateTaskStatusId(int taskId, int statusId, UserRepository* userRepo); 
    void updateTaskCategory(int taskId, int catId);
    void updateTaskPriority(int taskId, int prioId);
    
    void checkDeadlines();
    std::string getTasksJson(std::string filter);
    std::string getTasksByMonth(std::string monthPrefix);
    
    // Home Screens
    std::string getTasksForToday();
    std::string getTasksForTomorrow();
    std::string getOverdueTasksDetailed();
    
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
};

#endif