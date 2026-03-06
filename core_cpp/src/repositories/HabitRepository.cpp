#include "repositories/HabitRepository.h"
#include "repositories/UserRepository.h" 
#include <iostream>
#include <sstream>

HabitRepository::HabitRepository(sqlite3* dbConn) : db(dbConn) {}

void HabitRepository::executeQuery(const std::string& query) {
    char* err = 0;
    sqlite3_exec(db, query.c_str(), 0, 0, &err);
    if(err) sqlite3_free(err);
}

std::string HabitRepository::queryJson(const std::string& sql) {
    sqlite3_stmt* stmt;
    std::stringstream json;
    json << "[";
    if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, 0) == SQLITE_OK) {
        int cols = sqlite3_column_count(stmt);
        bool firstRow = true;
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            if (!firstRow) json << ",";
            json << "{";
            for (int i = 0; i < cols; i++) {
                std::string colName = sqlite3_column_name(stmt, i);
                const char* val = (const char*)sqlite3_column_text(stmt, i);
                json << "\"" << colName << "\": \"" << (val ? val : "") << "\"";
                if (i < cols - 1) json << ",";
            }
            json << "}";
            firstRow = false;
        }
    }
    sqlite3_finalize(stmt);
    json << "]";
    return json.str();
}

bool HabitRepository::initHabits() {
    executeQuery("CREATE TABLE IF NOT EXISTS difficulties (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, score INTEGER);");
    executeQuery("INSERT OR IGNORE INTO difficulties (id, name, score) VALUES (1, 'Very Easy', 1), (2, 'Easy', 2), (3, 'Medium', 3), (4, 'Hard', 4), (5, 'Hardcore', 5);");
    executeQuery("CREATE TABLE IF NOT EXISTS habits (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, target INTEGER DEFAULT 30, difficulty_id INTEGER DEFAULT 3 REFERENCES difficulties(id));");
    executeQuery("CREATE TABLE IF NOT EXISTS habit_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, habit_id INTEGER, done_date TEXT, FOREIGN KEY(habit_id) REFERENCES habits(id));");
    executeQuery("CREATE TABLE IF NOT EXISTS daily_reflections (date TEXT PRIMARY KEY, mood INTEGER DEFAULT 5, energy INTEGER DEFAULT 5, motivation INTEGER DEFAULT 5);");
    
    executeQuery("CREATE TABLE IF NOT EXISTS goals (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, deadline TEXT, habit_daily TEXT, habit_weekly TEXT, habit_monthly TEXT, category_id INTEGER, is_completed INTEGER DEFAULT 0, FOREIGN KEY(category_id) REFERENCES categories(id));");
    return true;
}

// Habits
void HabitRepository::addHabit(std::string title, int difficultyId) { executeQuery("INSERT INTO habits (title, difficulty_id) VALUES ('" + title + "', " + std::to_string(difficultyId) + ")"); }
void HabitRepository::updateHabit(int id, std::string title, int difficultyId) { executeQuery("UPDATE habits SET title='" + title + "', difficulty_id=" + std::to_string(difficultyId) + " WHERE id=" + std::to_string(id)); }
void HabitRepository::deleteHabit(int id) { executeQuery("DELETE FROM habit_logs WHERE habit_id=" + std::to_string(id)); executeQuery("DELETE FROM habits WHERE id=" + std::to_string(id)); }

void HabitRepository::toggleHabitDate(int habitId, std::string date, UserRepository* userRepo) {
    sqlite3_stmt* stmt;
    std::string check = "SELECT id FROM habit_logs WHERE habit_id=" + std::to_string(habitId) + " AND done_date='" + date + "'";
    bool exists = false;
    if (sqlite3_prepare_v2(db, check.c_str(), -1, &stmt, 0) == SQLITE_OK) { if(sqlite3_step(stmt) == SQLITE_ROW) exists = true; }
    sqlite3_finalize(stmt);
    
    if (exists) {
        executeQuery("DELETE FROM habit_logs WHERE habit_id=" + std::to_string(habitId) + " AND done_date='" + date + "'");
    } else {
        executeQuery("INSERT INTO habit_logs (habit_id, done_date) VALUES (" + std::to_string(habitId) + ", '" + date + "')");
        if (userRepo) userRepo->addXP(10);
    }
}

std::string HabitRepository::getHabitGridJson(std::string month) {
    std::string sqlHabits = "SELECT id, title, target FROM habits";
    sqlite3_stmt* stmt;
    struct GridHabit { int id; std::string title; int target; std::vector<int> days; };
    std::vector<GridHabit> habits;
    if (sqlite3_prepare_v2(db, sqlHabits.c_str(), -1, &stmt, 0) == SQLITE_OK) {
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            GridHabit h; h.id = sqlite3_column_int(stmt, 0); h.title = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1)); h.target = sqlite3_column_int(stmt, 2); habits.push_back(h);
        }
    }
    sqlite3_finalize(stmt);
    for (auto& h : habits) {
        std::string sqlLogs = "SELECT done_date FROM habit_logs WHERE habit_id=" + std::to_string(h.id) + " AND done_date LIKE '" + month + "%'";
        if (sqlite3_prepare_v2(db, sqlLogs.c_str(), -1, &stmt, 0) == SQLITE_OK) {
            while (sqlite3_step(stmt) == SQLITE_ROW) {
                std::string date = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 0));
                try { int day = std::stoi(date.substr(8, 2)); h.days.push_back(day); } catch(...) {}
            }
        }
        sqlite3_finalize(stmt);
    }
    std::stringstream ss; ss << "[";
    for (size_t i = 0; i < habits.size(); ++i) {
        if (i > 0) ss << ",";
        ss << "{\"id\": " << habits[i].id << ", \"title\": \"" << habits[i].title << "\", \"target\": " << habits[i].target << ", \"days\": [";
        for (size_t j = 0; j < habits[i].days.size(); ++j) ss << habits[i].days[j] << (j < habits[i].days.size() - 1 ? "," : "");
        ss << "]}";
    }
    ss << "]";
    return ss.str();
}

std::string HabitRepository::getHabitScoreStats(std::string month) {
    return queryJson("SELECT hl.done_date as date, SUM(d.score) as total_score FROM habit_logs hl JOIN habits h ON hl.habit_id = h.id JOIN difficulties d ON h.difficulty_id = d.id WHERE hl.done_date LIKE '" + month + "%' GROUP BY hl.done_date ORDER BY hl.done_date ASC");
}

std::string HabitRepository::getDifficultiesJson() { return queryJson("SELECT * FROM difficulties ORDER BY score ASC"); }
void HabitRepository::addDifficulty(std::string name, int score) { executeQuery("INSERT INTO difficulties (name, score) VALUES ('" + name + "', " + std::to_string(score) + ");"); }
void HabitRepository::deleteDifficulty(int id) { executeQuery("DELETE FROM difficulties WHERE id=" + std::to_string(id)); executeQuery("UPDATE habits SET difficulty_id=3 WHERE difficulty_id=" + std::to_string(id)); }

void HabitRepository::setDailyReflection(std::string date, int mood, int energy, int motiv) { executeQuery("INSERT OR REPLACE INTO daily_reflections (date, mood, energy, motivation) VALUES ('" + date + "', " + std::to_string(mood) + ", " + std::to_string(energy) + ", " + std::to_string(motiv) + ");"); }
std::string HabitRepository::getDailyReflections(std::string month) { return queryJson("SELECT * FROM daily_reflections WHERE date LIKE '" + month + "%'"); }

void HabitRepository::addGoal(std::string title, std::string deadline, std::string daily, std::string weekly, std::string monthly, int catId) { executeQuery("INSERT INTO goals (title, deadline, habit_daily, habit_weekly, habit_monthly, category_id) VALUES ('" + title + "', '" + deadline + "', '" + daily + "', '" + weekly + "', '" + monthly + "', " + std::to_string(catId) + ");"); }
void HabitRepository::updateGoal(int id, std::string title, std::string deadline, std::string daily, std::string weekly, std::string monthly, int catId) { executeQuery("UPDATE goals SET title='" + title + "', deadline='" + deadline + "', habit_daily='" + daily + "', habit_weekly='" + weekly + "', habit_monthly='" + monthly + "', category_id=" + std::to_string(catId) + " WHERE id=" + std::to_string(id)); }
void HabitRepository::toggleGoal(int id) { executeQuery("UPDATE goals SET is_completed = NOT is_completed WHERE id=" + std::to_string(id)); }
void HabitRepository::deleteGoal(int id) { executeQuery("DELETE FROM goals WHERE id=" + std::to_string(id)); }
std::string HabitRepository::getGoalsJson() { return queryJson("SELECT g.id, g.title, g.deadline, g.habit_daily, g.habit_weekly, g.habit_monthly, g.category_id, g.is_completed, c.name as category, c.color as c_color FROM goals g JOIN categories c ON g.category_id = c.id ORDER BY g.is_completed ASC, g.deadline ASC"); }