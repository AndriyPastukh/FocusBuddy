#ifndef USER_REPOSITORY_H
#define USER_REPOSITORY_H

#include <string>
#include <vector>
#include "sqlite3.h"

class UserRepository {
    sqlite3* db;
    void executeQuery(const std::string& query);
    std::string queryJson(const std::string& query);

public:
    UserRepository(sqlite3* db);
    
    bool initUser();
    std::string getUserJson();
    void updateUsername(std::string newName);
    void setAvatar(std::string avatarSymbol);
    void addXP(int amount);
    
    // Stats & Sessions
    void completeSession(int minutes);
    void logSession(std::string start, std::string end, int duration, int xp, int taskId, std::string taskTitle);
    std::string getSessionsJson();
    std::string getWeeklyStatsJson();
    std::string getAchievementsJson();
};

#endif