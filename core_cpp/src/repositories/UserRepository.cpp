#include "repositories/UserRepository.h"
#include <iostream>
#include <sstream>
#include <ctime>
#include <iomanip>

UserRepository::UserRepository(sqlite3* dbConn) : db(dbConn) {}

void UserRepository::executeQuery(const std::string& query) {
    char* err = 0;
    sqlite3_exec(db, query.c_str(), 0, 0, &err);
    if(err) sqlite3_free(err);
}

std::string UserRepository::queryJson(const std::string& sql) {
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

bool UserRepository::initUser() {
    executeQuery("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY CHECK (id = 1), username TEXT DEFAULT 'Hero', xp INTEGER DEFAULT 0, level INTEGER DEFAULT 1, avatar TEXT DEFAULT '😎', total_pomodoros INTEGER DEFAULT 0, total_minutes INTEGER DEFAULT 0);");
    executeQuery("INSERT OR IGNORE INTO user (id, username, xp, level, avatar) VALUES (1, 'FocusBuddy', 0, 1, '😎');");
    
    executeQuery("CREATE TABLE IF NOT EXISTS pomodoro_sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, start_time TEXT, end_time TEXT, duration INTEGER, xp_earned INTEGER, task_id INTEGER DEFAULT 0, task_title TEXT);");
    return true;
}

std::string UserRepository::getUserJson() {
    return queryJson("SELECT * FROM user WHERE id=1");
}

void UserRepository::updateUsername(std::string newName) {
    executeQuery("UPDATE user SET username='" + newName + "' WHERE id=1");
}

void UserRepository::setAvatar(std::string avatarSymbol) {
    executeQuery("UPDATE user SET avatar='" + avatarSymbol + "' WHERE id=1");
}

void UserRepository::addXP(int amount) {
    int currentXP = 0;
    int currentLevel = 1;
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(db, "SELECT xp, level FROM user WHERE id=1", -1, &stmt, 0) == SQLITE_OK) {
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            currentXP = sqlite3_column_int(stmt, 0);
            currentLevel = sqlite3_column_int(stmt, 1);
        }
    }
    sqlite3_finalize(stmt);

    int newXP = currentXP + amount;
    int xpForNextLevel = currentLevel * 100; 
    int newLevel = currentLevel;
    
    while (newXP >= xpForNextLevel) {
        newXP -= xpForNextLevel;
        newLevel++;
        xpForNextLevel = newLevel * 100;
    }
    executeQuery("UPDATE user SET xp=" + std::to_string(newXP) + ", level=" + std::to_string(newLevel) + " WHERE id=1");
}

void UserRepository::completeSession(int minutes) {
    int xpEarned = (minutes / 5) * 10;
    if (xpEarned < 5) xpEarned = 5; 
    addXP(xpEarned);

    int totalPoms = 0, totalMins = 0;
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(db, "SELECT total_pomodoros, total_minutes FROM user WHERE id=1", -1, &stmt, 0) == SQLITE_OK) {
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            totalPoms = sqlite3_column_int(stmt, 0);
            totalMins = sqlite3_column_int(stmt, 1);
        }
    }
    sqlite3_finalize(stmt);

    totalPoms++;
    totalMins += minutes;
    executeQuery("UPDATE user SET total_pomodoros=" + std::to_string(totalPoms) + ", total_minutes=" + std::to_string(totalMins) + " WHERE id=1");
}

void UserRepository::logSession(std::string start, std::string end, int duration, int xp, int taskId, std::string taskTitle) {
    std::string sql = "INSERT INTO pomodoro_sessions (start_time, end_time, duration, xp_earned, task_id, task_title) VALUES ('" + 
                      start + "', '" + end + "', " + std::to_string(duration) + ", " + 
                      std::to_string(xp) + ", " + std::to_string(taskId) + ", '" + taskTitle + "');";
    executeQuery(sql);
    addXP(xp); 
    
    // Update totals
    int currentPoms = 0, currentMins = 0;
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(db, "SELECT total_pomodoros, total_minutes FROM user WHERE id=1", -1, &stmt, 0) == SQLITE_OK) {
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            currentPoms = sqlite3_column_int(stmt, 0);
            currentMins = sqlite3_column_int(stmt, 1);
        }
    }
    sqlite3_finalize(stmt);
    executeQuery("UPDATE user SET total_pomodoros=" + std::to_string(currentPoms + 1) + ", total_minutes=" + std::to_string(currentMins + duration) + " WHERE id=1");
}

std::string UserRepository::getSessionsJson() {
    return queryJson("SELECT * FROM pomodoro_sessions ORDER BY id DESC LIMIT 50");
}

std::string UserRepository::getWeeklyStatsJson() {
    std::stringstream json;
    json << "[";
    for (int i = 6; i >= 0; i--) {
        time_t t = time(nullptr);
        t -= (i * 24 * 60 * 60);
        tm* info = localtime(&t);
        char buffer[20];
        strftime(buffer, 20, "%Y-%m-%d", info);
        std::string dateStr(buffer);
        
        int focusMins = 0;
        std::string sql1 = "SELECT SUM(duration) FROM pomodoro_sessions WHERE start_time LIKE '" + dateStr + "%'";
        sqlite3_stmt* stmt1;
        if (sqlite3_prepare_v2(db, sql1.c_str(), -1, &stmt1, 0) == SQLITE_OK) {
            if (sqlite3_step(stmt1) == SQLITE_ROW) focusMins = sqlite3_column_int(stmt1, 0);
        }
        sqlite3_finalize(stmt1);
        
        int tasksDone = 0;
        std::string sql2 = "SELECT COUNT(*) FROM tasks WHERE todo_date = '" + dateStr + "' AND is_completed = 1";
        sqlite3_stmt* stmt2;
        if (sqlite3_prepare_v2(db, sql2.c_str(), -1, &stmt2, 0) == SQLITE_OK) {
            if (sqlite3_step(stmt2) == SQLITE_ROW) tasksDone = sqlite3_column_int(stmt2, 0);
        }
        sqlite3_finalize(stmt2);
        
        if (i < 6) json << ",";
        json << "{\"date\": \"" << dateStr << "\", \"focus_minutes\": " << focusMins << ", \"tasks_done\": " << tasksDone << "}";
    }
    json << "]";
    return json.str();
}

std::string UserRepository::getAchievementsJson() {
    int totalPoms = 0, totalMins = 0, xp = 0;
    sqlite3_stmt* stmt;
    if (sqlite3_prepare_v2(db, "SELECT total_pomodoros, total_minutes, xp FROM user WHERE id=1", -1, &stmt, 0) == SQLITE_OK) {
        if (sqlite3_step(stmt) == SQLITE_ROW) {
            totalPoms = sqlite3_column_int(stmt, 0);
            totalMins = sqlite3_column_int(stmt, 1);
            xp = sqlite3_column_int(stmt, 2);
        }
    }
    sqlite3_finalize(stmt);

    std::stringstream json;
    json << "[";
    
    int count = 0;
    int totalAchievements = 120; 

    auto addAch = [&](std::string title, std::string desc, std::string icon, bool unlocked) {
        count++;
        json << "{" << "\"title\": \"" << title << "\", \"desc\": \"" << desc << "\", \"icon\": \"" << icon << "\", \"unlocked\": " << (unlocked ? "1" : "0") << "}" << (count < totalAchievements ? "," : "");
    };

    // === 1. SESSION MASTER (40) ===
    addAch("Hello World", "Complete 1 session", "👋", totalPoms >= 1);
    addAch("Warming Up", "Complete 2 sessions", "👟", totalPoms >= 2);
    addAch("Hat Trick", "Complete 3 sessions", "🎩", totalPoms >= 3);
    addAch("Four Leaf Clover", "Complete 4 sessions", "🍀", totalPoms >= 4);
    addAch("High Five", "Complete 5 sessions", "✋", totalPoms >= 5);
    addAch("Six Pack", "Complete 6 sessions", "💪", totalPoms >= 6);
    addAch("Lucky Seven", "Complete 7 sessions", "🎰", totalPoms >= 7);
    addAch("Byte Size", "Complete 8 sessions", "💾", totalPoms >= 8);
    addAch("Cloud Nine", "Complete 9 sessions", "☁️", totalPoms >= 9);
    addAch("Double Digits", "Complete 10 sessions", "🔟", totalPoms >= 10);
    addAch("Bakers Dozen", "Complete 13 sessions", "🍩", totalPoms >= 13);
    addAch("Sweet Sixteen", "Complete 16 sessions", "🍬", totalPoms >= 16);
    addAch("Blackjack", "Complete 21 sessions", "🃏", totalPoms >= 21);
    addAch("Quarter Century", "Complete 25 sessions", "🪙", totalPoms >= 25);
    addAch("Thirty Rock", "Complete 30 sessions", "🗿", totalPoms >= 30);
    addAch("Fit Forty", "Complete 40 sessions", "🏃", totalPoms >= 40);
    addAch("Half Century", "Complete 50 sessions", "🌗", totalPoms >= 50);
    addAch("Sixty Speed", "Complete 60 sessions", "🏎️", totalPoms >= 60);
    addAch("Seventy Split", "Complete 70 sessions", "🍌", totalPoms >= 70);
    addAch("Around the World", "Complete 80 sessions", "🌍", totalPoms >= 80);
    addAch("Centurion", "Complete 100 sessions", "💯", totalPoms >= 100);
    addAch("Gross", "Complete 144 sessions", "📦", totalPoms >= 144);
    addAch("Serious Biz", "Complete 150 sessions", "💼", totalPoms >= 150);
    addAch("Double Century", "Complete 200 sessions", "🛡️", totalPoms >= 200);
    addAch("Spartan", "Complete 300 sessions", "⚔️", totalPoms >= 300);
    addAch("Year of Days", "Complete 365 sessions", "📅", totalPoms >= 365);
    addAch("Focus Machine", "Complete 400 sessions", "🤖", totalPoms >= 400);
    addAch("Error 404", "Complete 404 sessions (Sleep not found)", "🚫", totalPoms >= 404);
    addAch("The 500 Club", "Complete 500 sessions", "🏰", totalPoms >= 500);
    addAch("Devil's Number", "Complete 666 sessions", "😈", totalPoms >= 666);
    addAch("Boeing", "Complete 747 sessions", "✈️", totalPoms >= 747);
    addAch("Jackpot", "Complete 777 sessions", "💎", totalPoms >= 777);
    addAch("Cyberpunk", "Complete 888 sessions", "🦾", totalPoms >= 888);
    addAch("Almost There", "Complete 900 sessions", "🏁", totalPoms >= 900);
    addAch("Grandmaster", "Complete 1000 sessions", "👑", totalPoms >= 1000);
    addAch("Binary Beast", "Complete 1024 sessions", "👾", totalPoms >= 1024);
    addAch("Elite", "Complete 1337 sessions", "💻", totalPoms >= 1337);
    addAch("Unstoppable", "Complete 1500 sessions", "🚀", totalPoms >= 1500);
    addAch("Historical", "Complete 1999 sessions", "📜", totalPoms >= 1999);
    addAch("Focus God", "Complete 2000 sessions", "🪐", totalPoms >= 2000);

    // === 2. TIME LORD (40) ===
    addAch("Just a Minute", "Reach 25 minutes", "⏱️", totalMins >= 25);
    addAch("Short Film", "Reach 45 minutes", "🎞️", totalMins >= 45);
    addAch("Hour of Power", "Reach 60 minutes", "⚡", totalMins >= 60);
    addAch("Two Hours", "Reach 120 minutes", "🕑", totalMins >= 120);
    addAch("Half Day", "Reach 240 minutes", "🏙️", totalMins >= 240);
    addAch("Deep Dive", "Reach 300 minutes", "🌊", totalMins >= 300);
    addAch("Workday", "Reach 480 minutes", "👔", totalMins >= 480);
    addAch("Ten Hours", "Reach 600 minutes", "🕰️", totalMins >= 600);
    addAch("Call Center", "Reach 720 minutes", "📞", totalMins >= 720);
    addAch("Limitless", "Reach 900 minutes", "🧠", totalMins >= 900);
    addAch("Time Master", "Reach 1000 minutes", "⏳", totalMins >= 1000);
    addAch("Day & Night", "Reach 1440 minutes (24h)", "☀️", totalMins >= 1440);
    addAch("Mini Vacation", "Reach 2000 minutes", "🏖️", totalMins >= 2000);
    addAch("Focus Week", "Reach 2400 minutes (40h)", "📆", totalMins >= 2400);
    addAch("Time Traveler", "Reach 3000 minutes", "🛸", totalMins >= 3000);
    addAch("Productivity Beast", "Reach 4000 minutes", "🦍", totalMins >= 4000);
    addAch("Three Days", "Reach 4320 minutes (72h)", "🌓", totalMins >= 4320);
    addAch("Iron Man", "Reach 4500 minutes", "🦾", totalMins >= 4500);
    addAch("Workaholic", "Reach 5000 minutes", "🏗️", totalMins >= 5000);
    addAch("Four Days", "Reach 5760 minutes (96h)", "🛌", totalMins >= 5760);
    addAch("100 Hours", "Reach 6000 minutes", "💡", totalMins >= 6000);
    addAch("Writer", "Reach 7000 minutes", "🖋️", totalMins >= 7000);
    addAch("Scientist", "Reach 8000 minutes", "🔬", totalMins >= 8000);
    addAch("Philosopher", "Reach 9000 minutes", "🦉", totalMins >= 9000);
    addAch("Week of Life", "Reach 10080 minutes (7 days)", "🗓️", totalMins >= 10080);
    addAch("Researcher", "Reach 12000 minutes", "🔎", totalMins >= 12000);
    addAch("Time Lord", "Reach 15000 minutes", "🧙", totalMins >= 15000);
    addAch("Dedicated", "Reach 17500 minutes", "🤝", totalMins >= 17500);
    addAch("Marathon Runner", "Reach 20000 minutes", "👟", totalMins >= 20000);
    addAch("Two Weeks", "Reach 20160 minutes (14 days)", "Fortnite", totalMins >= 20160);
    addAch("Quarter 100k", "Reach 25000 minutes", "¼", totalMins >= 25000);
    addAch("Half Million", "Reach 30000 minutes", "💎", totalMins >= 30000);
    addAch("Lunar Cycle", "Reach 40320 minutes (28 days)", "🌑", totalMins >= 40320);
    addAch("Professional", "Reach 50000 minutes", "🎓", totalMins >= 50000);
    addAch("Expert", "Reach 60000 minutes (1000h)", "🌌", totalMins >= 60000);
    addAch("Mastery", "Reach 75000 minutes", "🥋", totalMins >= 75000);
    addAch("Grandmaster Time", "Reach 90000 minutes", "👴", totalMins >= 90000);
    addAch("Century", "Reach 100000 minutes", "💯", totalMins >= 100000);
    addAch("Living Legend", "Reach 150000 minutes", "🗿", totalMins >= 150000);
    addAch("Timeless", "Reach 200000 minutes", "♾️", totalMins >= 200000);

    // === 3. XP HUNTER (40) ===
    addAch("Newbie", "Earn 100 XP", "🐣", xp >= 100);
    addAch("Getting Started", "Earn 200 XP", "🛴", xp >= 200);
    addAch("Small Steps", "Earn 300 XP", "👣", xp >= 300);
    addAch("Gaining Speed", "Earn 400 XP", "🚲", xp >= 400);
    addAch("Task Crusher", "Earn 500 XP", "🔨", xp >= 500);
    addAch("Level Upper", "Earn 600 XP", "📶", xp >= 600);
    addAch("Lucky XP", "Earn 700 XP", "🎱", xp >= 700);
    addAch("Almost 1k", "Earn 900 XP", "🤏", xp >= 900);
    addAch("Apprentice", "Earn 1000 XP", "📜", xp >= 1000);
    addAch("Keyboard Warrior", "Earn 1500 XP", "⌨️", xp >= 1500);
    addAch("Level Up", "Earn 2000 XP", "🆙", xp >= 2000);
    addAch("Grinder", "Earn 3000 XP", "⚙️", xp >= 3000);
    addAch("Farmer", "Earn 4000 XP", "🌾", xp >= 4000);
    addAch("Skilled", "Earn 5000 XP", "🎓", xp >= 5000);
    addAch("Hunter", "Earn 6000 XP", "🏹", xp >= 6000);
    addAch("Warrior", "Earn 7000 XP", "🛡️", xp >= 7000);
    addAch("Paladin", "Earn 8000 XP", "✨", xp >= 8000);
    addAch("Mage", "Earn 9000 XP", "🔮", xp >= 9000);
    addAch("Elite", "Earn 10000 XP", "🎖️", xp >= 10000);
    addAch("Rogue", "Earn 12000 XP", "🗡️", xp >= 12000);
    addAch("Veteran", "Earn 15000 XP", "🎗️", xp >= 15000);
    addAch("Hero", "Earn 18000 XP", "🦸", xp >= 18000);
    addAch("Master", "Earn 20000 XP", "🥋", xp >= 20000);
    addAch("Champion", "Earn 25000 XP", "🏆", xp >= 25000);
    addAch("Warlord", "Earn 30000 XP", "👺", xp >= 30000);
    addAch("King", "Earn 35000 XP", "🤴", xp >= 35000);
    addAch("Emperor", "Earn 40000 XP", "🏯", xp >= 40000);
    addAch("Conqueror", "Earn 45000 XP", "🚩", xp >= 45000);
    addAch("Mythic", "Earn 50000 XP", "🦄", xp >= 50000);
    addAch("Dragon", "Earn 60000 XP", "🐉", xp >= 60000);
    addAch("Immortal", "Earn 75000 XP", "⚱️", xp >= 75000);
    addAch("Demigod", "Earn 85000 XP", "⚡", xp >= 85000);
    addAch("The One", "Earn 100000 XP", "🧬", xp >= 100000);
    addAch("Supernova", "Earn 125000 XP", "💥", xp >= 125000);
    addAch("Black Hole", "Earn 150000 XP", "🕳️", xp >= 150000);
    addAch("Galaxy", "Earn 175000 XP", "🌌", xp >= 175000);
    addAch("Universe", "Earn 200000 XP", "🔭", xp >= 200000);
    addAch("Multiverse", "Earn 250000 XP", "⚛️", xp >= 250000);
    addAch("Omnipotent", "Earn 500000 XP", "👁️", xp >= 500000);
    addAch("Focus Infinity", "Earn 1000000 XP", "♾️", xp >= 1000000);

    json << "]";
    return json.str();
}