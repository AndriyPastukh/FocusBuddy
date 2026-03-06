#ifndef HABIT_REPOSITORY_H
#define HABIT_REPOSITORY_H

#include <string>
#include <vector>
#include "sqlite3.h"

// === ВАЖЛИВО: Попереднє оголошення ===
class UserRepository;
// =====================================

class HabitRepository {
    sqlite3* db;
    void executeQuery(const std::string& query);
    std::string queryJson(const std::string& query);

public:
    HabitRepository(sqlite3* db);
    bool initHabits();

    // Habits
    void addHabit(std::string title, int difficultyId);
    void updateHabit(int id, std::string title, int difficultyId);
    void deleteHabit(int id);
    
    // Тут також потрібен userRepo для нарахування XP
    void toggleHabitDate(int habitId, std::string date, UserRepository* userRepo); 
    
    std::string getHabitGridJson(std::string month);
    std::string getHabitScoreStats(std::string month);

    // Difficulties
    std::string getDifficultiesJson();
    void addDifficulty(std::string name, int score);
    void deleteDifficulty(int id);

    // Reflections
    void setDailyReflection(std::string date, int mood, int energy, int motiv);
    std::string getDailyReflections(std::string month);

    // Goals
    void addGoal(std::string title, std::string deadline, std::string daily, std::string weekly, std::string monthly, int catId);
    void updateGoal(int id, std::string title, std::string deadline, std::string daily, std::string weekly, std::string monthly, int catId);
    void toggleGoal(int id);
    void deleteGoal(int id);
    std::string getGoalsJson();
};

#endif