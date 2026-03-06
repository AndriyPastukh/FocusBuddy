#include <iostream>
#include <string>
#include <vector>
#include <sstream>
#include "DatabaseManager.h"

#ifdef _WIN32
#include <windows.h>
#endif

void printSuccess() { 
    std::cout << "{\"status\": \"ok\"}" << std::endl; 
}

std::vector<std::string> split(const std::string& s, char delimiter) {
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(s);
    while (std::getline(tokenStream, token, delimiter)) {
        tokens.push_back(token);
    }
    return tokens;
}

int main(int argc, char* argv[]) {
    #ifdef _WIN32
    SetConsoleOutputCP(65001); 
    SetConsoleCP(65001);
    #endif

    DatabaseManager db("trackery.db"); 
    if (!db.initDB()) return 1;

    if (argc > 1) return 0; 

    std::string line;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        if (line == "EXIT") break;

        std::vector<std::string> args = split(line, '|');
        if (args.empty()) continue;
        std::string cmd = args[0];

        try {
            // === USER ===
            if (cmd == "getUser") { std::cout << db.getUserJson() << std::endl; }
            else if (cmd == "updateUsername") { if(args.size() > 1) db.updateUsername(args[1]); printSuccess(); }
            else if (cmd == "getAchievements") { std::cout << db.getAchievementsJson() << std::endl; }
            else if (cmd == "addXP") { if(args.size() > 1) db.addXP(std::stoi(args[1])); printSuccess(); }
            else if (cmd == "setAvatar") { if(args.size() > 1) db.setAvatar(args[1]); printSuccess(); }

            // === CORE ===
            else if (cmd == "getHomePayload") { std::cout << db.getHomePayload() << std::endl; }
            else if (cmd == "getLookups") {
                std::cout << "{\"categories\": " << db.getCategoriesJson() 
                          << ", \"priorities\": " << db.getPrioritiesJson() 
                          << ", \"statuses\": " << db.getStatusesJson() << "}" << std::endl;
            }
            else if (cmd == "getDifficulties") { std::cout << db.getDifficultiesJson() << std::endl; }

            // === TASKS ===
            else if (cmd == "getTasks") { 
                std::string filter = (args.size() > 1) ? args[1] : "all";
                std::cout << db.getTasksJson(filter) << std::endl; 
            }
            else if (cmd == "getTasksByMonth") {
                std::string month = (args.size() > 1) ? args[1] : "";
                std::cout << db.getTasksByMonth(month) << std::endl;
            }
            else if (cmd == "addTask") {
                if(args.size() > 7) {
                    db.addTask(args[1], args[2], args[3], args[4], std::stoi(args[5]), std::stoi(args[6]), args[7]);
                    printSuccess();
                } else printSuccess();
            }
            else if (cmd == "editTask") {
                if(args.size() > 8) {
                    db.editTask(std::stoi(args[1]), args[2], args[3], args[4], args[5], std::stoi(args[6]), std::stoi(args[7]), args[8]);
                    printSuccess();
                } else printSuccess();
            }
            else if (cmd == "deleteTask") { 
                if(args.size() > 1) {
                    db.deleteTask(std::stoi(args[1]));
                    printSuccess();
                } else printSuccess();
            }
            else if (cmd == "completeTask") { if(args.size() > 1) db.updateTaskStatus(std::stoi(args[1]), 3, 1); printSuccess(); }
            else if (cmd == "setTaskStatus") { if(args.size() > 2) db.updateTaskStatusId(std::stoi(args[1]), std::stoi(args[2])); printSuccess(); }
            else if (cmd == "setTaskCat") { if(args.size() > 2) db.updateTaskCategory(std::stoi(args[1]), std::stoi(args[2])); printSuccess(); }
            else if (cmd == "setTaskPrio") { if(args.size() > 2) db.updateTaskPriority(std::stoi(args[1]), std::stoi(args[2])); printSuccess(); }
            
            else if (cmd == "getTodayTasks") { std::cout << db.getTasksForToday() << std::endl; }
            else if (cmd == "getTomorrow") { std::cout << db.getTasksForTomorrow() << std::endl; }
            else if (cmd == "getOverdue") { std::cout << db.getOverdueTasksDetailed() << std::endl; }

            // === HABITS ===
            else if (cmd == "getHabitGrid") { std::string m = (args.size() > 1) ? args[1] : ""; std::cout << db.getHabitGridJson(m) << std::endl; }
            else if (cmd == "addHabit") { if(args.size() > 2) db.addHabit(args[1], std::stoi(args[2])); printSuccess(); }
            else if (cmd == "editHabit") { if(args.size() > 3) db.updateHabit(std::stoi(args[1]), args[2], std::stoi(args[3])); printSuccess(); }
            else if (cmd == "delHabit") { if(args.size() > 1) db.deleteHabit(std::stoi(args[1])); printSuccess(); }
            else if (cmd == "toggleHabit") { if(args.size() > 2) db.toggleHabitDate(std::stoi(args[1]), args[2]); printSuccess(); }
            else if (cmd == "getHabitScoreStats") { if(args.size() > 1) std::cout << db.getHabitScoreStats(args[1]) << std::endl; else std::cout << "[]" << std::endl; }
            else if (cmd == "setReflection") { if(args.size() > 4) db.setDailyReflection(args[1], std::stoi(args[2]), std::stoi(args[3]), std::stoi(args[4])); printSuccess(); }
            else if (cmd == "getReflections") { if(args.size() > 1) std::cout << db.getDailyReflections(args[1]) << std::endl; else std::cout << "[]" << std::endl; }

            // === ANALYTICS ===
            else if (cmd == "getDashboard") { std::cout << db.getDashboardStats() << std::endl; }
            else if (cmd == "getChart") { if(args.size() > 1) std::cout << db.getChartData(args[1]) << std::endl; else printSuccess(); }
            else if (cmd == "getWeeklyStats") { std::cout << db.getWeeklyStatsJson() << std::endl; }
            else if (cmd == "getSessions") { std::cout << db.getSessionsJson() << std::endl; }
            else if (cmd == "logSession") {
                if(args.size() > 6) {
                    db.logSession(args[1], args[2], std::stoi(args[3]), std::stoi(args[4]), std::stoi(args[5]), args[6]);
                    printSuccess();
                } else printSuccess();
            }
            else if (cmd == "completeSession") { if(args.size() > 1) db.completeSession(std::stoi(args[1])); printSuccess(); }

            // === GOALS ===
            else if (cmd == "getGoals") { std::cout << db.getGoalsJson() << std::endl; }
            else if (cmd == "addGoal") { if(args.size() > 6) db.addGoal(args[1], args[2], args[3], args[4], args[5], std::stoi(args[6])); printSuccess(); }
            else if (cmd == "editGoal") { if(args.size() > 7) db.updateGoal(std::stoi(args[1]), args[2], args[3], args[4], args[5], args[6], std::stoi(args[7])); printSuccess(); }
            else if (cmd == "toggleGoal") { if(args.size() > 1) db.toggleGoal(std::stoi(args[1])); printSuccess(); }
            else if (cmd == "delGoal") { if(args.size() > 1) db.deleteGoal(std::stoi(args[1])); printSuccess(); }

            // === SETTINGS ===
            else if (cmd == "addCategory") { if(args.size() > 2) db.addCategory(args[1], args[2]); printSuccess(); }
            else if (cmd == "delCategory") { if(args.size() > 1) db.deleteCategory(std::stoi(args[1])); printSuccess(); }
            else if (cmd == "addPriority") { if(args.size() > 3) db.addPriority(args[1], args[2], std::stoi(args[3])); printSuccess(); }
            else if (cmd == "delPriority") { if(args.size() > 1) db.deletePriority(std::stoi(args[1])); printSuccess(); }
            else if (cmd == "addStatus") { if(args.size() > 2) db.addStatus(args[1], args[2]); printSuccess(); }
            else if (cmd == "delStatus") { if(args.size() > 1) db.deleteStatus(std::stoi(args[1])); printSuccess(); }
            else if (cmd == "addDifficulty") { if(args.size() > 2) db.addDifficulty(args[1], std::stoi(args[2])); printSuccess(); }
            else if (cmd == "delDifficulty") { if(args.size() > 1) db.deleteDifficulty(std::stoi(args[1])); printSuccess(); }

            else { std::cout << "{}" << std::endl; }

        } catch (...) {
            std::cout << "{\"error\": \"Exception\"}" << std::endl;
        }
    }
    return 0;
}