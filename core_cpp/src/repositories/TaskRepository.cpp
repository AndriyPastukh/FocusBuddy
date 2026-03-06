#include "repositories/TaskRepository.h"
#include "repositories/UserRepository.h"
#include <iostream>
#include <sstream>
#include <ctime>
#include <iomanip>

TaskRepository::TaskRepository(sqlite3* dbConn) : db(dbConn) {}

void TaskRepository::executeQuery(const std::string& query) {
    char* err = 0;
    sqlite3_exec(db, query.c_str(), 0, 0, &err);
    if(err) sqlite3_free(err);
}

std::string TaskRepository::queryJson(const std::string& sql) {
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

std::string TaskRepository::getToday() {
    auto t = std::time(nullptr);
    auto tm = *std::localtime(&t);
    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y-%m-%d");
    return oss.str();
}

bool TaskRepository::initTasks() {
    executeQuery("CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY, name TEXT, color TEXT);");
    executeQuery("CREATE TABLE IF NOT EXISTS priorities (id INTEGER PRIMARY KEY, name TEXT, color TEXT, level INTEGER);");
    executeQuery("CREATE TABLE IF NOT EXISTS statuses (id INTEGER PRIMARY KEY, name TEXT, icon TEXT);");
    executeQuery("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, todo_date TEXT, deadline_date TEXT, deadline_time TEXT, category_id INTEGER, priority_id INTEGER, status_id INTEGER, task_color TEXT DEFAULT '#AFAE9D', is_completed INTEGER DEFAULT 0, FOREIGN KEY(category_id) REFERENCES categories(id), FOREIGN KEY(priority_id) REFERENCES priorities(id), FOREIGN KEY(status_id) REFERENCES statuses(id));");

    // Seeds
    executeQuery("INSERT OR IGNORE INTO categories (id, name, color) VALUES (1, 'Work', '#E8DFF5'), (2, 'Personal', '#FCE1E4'), (3, 'Health', '#E2F0CB'), (4, 'Learning', '#FFF4E1');");
    executeQuery("INSERT OR IGNORE INTO priorities (id, name, color, level) VALUES (1, 'Low', '#88A0A8', 1), (2, 'Medium', '#E0C068', 2), (3, 'High', '#D45D5D', 3), (4, 'Critical', '#800080', 4);");
    executeQuery("INSERT OR IGNORE INTO statuses (id, name, icon) VALUES (1, 'Pending', '⚪'), (2, 'In Progress', '✏️'), (3, 'Done', '✅'), (4, 'Overdue', '❌');");
    return true;
}

std::string TaskRepository::getCategoriesJson() { return queryJson("SELECT * FROM categories"); }
std::string TaskRepository::getPrioritiesJson() { return queryJson("SELECT * FROM priorities"); }
std::string TaskRepository::getStatusesJson() { return queryJson("SELECT * FROM statuses"); }

void TaskRepository::addTask(std::string title, std::string todoDate, std::string deadlineDate, std::string deadlineTime, int catId, int prioId, std::string color) {
    std::string sql = "INSERT INTO tasks (title, todo_date, deadline_date, deadline_time, category_id, priority_id, status_id, task_color) VALUES ('" + title + "', '" + todoDate + "', '" + deadlineDate + "', '" + deadlineTime + "', " + std::to_string(catId) + ", " + std::to_string(prioId) + ", 1, '" + color + "');";
    executeQuery(sql);
}

void TaskRepository::editTask(int id, std::string title, std::string todoDate, std::string deadlineDate, std::string deadlineTime, int catId, int prioId, std::string color) {
    std::string sql = "UPDATE tasks SET title='" + title + "', todo_date='" + todoDate + "', deadline_date='" + deadlineDate + "', deadline_time='" + deadlineTime + "', category_id=" + std::to_string(catId) + ", priority_id=" + std::to_string(prioId) + ", task_color='" + color + "' WHERE id=" + std::to_string(id);
    executeQuery(sql);
}

void TaskRepository::remove(int id) {
    std::string sql = "DELETE FROM tasks WHERE id=" + std::to_string(id);
    executeQuery(sql);
}

void TaskRepository::updateTaskStatus(int taskId, int statusId, int isCompleted) {
    executeQuery("UPDATE tasks SET status_id=" + std::to_string(statusId) + ", is_completed=" + std::to_string(isCompleted) + " WHERE id=" + std::to_string(taskId));
}

void TaskRepository::updateTaskStatusId(int taskId, int statusId, UserRepository* userRepo) {
    int isCompleted = (statusId == 3) ? 1 : 0;
    if (statusId == 3 && userRepo) {
        userRepo->addXP(50);
    }
    std::string sql = "UPDATE tasks SET status_id=" + std::to_string(statusId) + ", is_completed=" + std::to_string(isCompleted) + " WHERE id=" + std::to_string(taskId);
    executeQuery(sql);
}

void TaskRepository::updateTaskCategory(int taskId, int catId) {
    executeQuery("UPDATE tasks SET category_id=" + std::to_string(catId) + " WHERE id=" + std::to_string(taskId));
}
void TaskRepository::updateTaskPriority(int taskId, int prioId) {
    executeQuery("UPDATE tasks SET priority_id=" + std::to_string(prioId) + " WHERE id=" + std::to_string(taskId));
}

void TaskRepository::checkDeadlines() {
    std::string today = getToday();
    executeQuery("UPDATE tasks SET status_id=4 WHERE deadline_date < '" + today + "' AND is_completed=0");
}

std::string TaskRepository::getTasksJson(std::string filter) {
    checkDeadlines();
    
    std::string sql = "SELECT t.id, t.title, t.todo_date, t.deadline_date, t.deadline_time, t.is_completed, t.task_color, "
                      "t.category_id, t.priority_id, t.status_id, "
                      "c.name as category, p.name as priority, s.name as status, p.color as p_color, s.icon as s_icon "
                      "FROM tasks t "
                      "JOIN categories c ON t.category_id = c.id "
                      "JOIN priorities p ON t.priority_id = p.id "
                      "JOIN statuses s ON t.status_id = s.id ";
    
    std::string today = getToday();

    if (filter == "today") {
        sql += "WHERE t.todo_date = '" + today + "' ";
    } 
    else if (filter == "overdue") {
        sql += "WHERE t.deadline_date < '" + today + "' AND t.is_completed = 0 ";
    }
    else if (filter == "active") { 
        sql += "WHERE t.is_completed = 0 ";
    }
    else if (filter == "important") {
        sql += "WHERE t.priority_id >= 3 AND t.is_completed = 0 ";
    }
    
    sql += "ORDER BY t.is_completed ASC, t.priority_id DESC, t.deadline_date ASC;";
    
    return queryJson(sql);
}

std::string TaskRepository::getTasksByMonth(std::string monthPrefix) {
    std::string sql = "SELECT t.id, t.title, t.todo_date, t.deadline_date, t.deadline_time, t.is_completed, t.task_color, t.category_id, t.priority_id, t.status_id, c.name as category, p.name as priority, s.name as status, p.color as p_color, s.icon as s_icon, c.color as c_color FROM tasks t JOIN categories c ON t.category_id = c.id JOIN priorities p ON t.priority_id = p.id JOIN statuses s ON t.status_id = s.id WHERE t.todo_date LIKE '" + monthPrefix + "%' ORDER BY t.todo_date ASC, t.deadline_time ASC;";
    return queryJson(sql);
}

std::string TaskRepository::getTasksForToday() {
    return getTasksJson("today");
}

std::string TaskRepository::getTasksForTomorrow() {
    time_t t = time(nullptr); t += 24 * 60 * 60; tm* tomorrow = localtime(&t); char buf[20]; strftime(buf, sizeof(buf), "%Y-%m-%d", tomorrow);
    std::string sql = "SELECT t.id, t.title, t.deadline_date, c.color, p.color FROM tasks t LEFT JOIN categories c ON t.category_id = c.id LEFT JOIN priorities p ON t.priority_id = p.id WHERE t.todo_date = '" + std::string(buf) + "' AND t.is_completed = 0 ORDER BY t.priority_id DESC;";
    return queryJson(sql);
}

std::string TaskRepository::getOverdueTasksDetailed() {
    std::string today = getToday();
    std::string sql = "SELECT t.id, t.title, t.deadline_date, c.color, p.color FROM tasks t LEFT JOIN categories c ON t.category_id = c.id LEFT JOIN priorities p ON t.priority_id = p.id WHERE t.deadline_date < '" + today + "' AND t.deadline_date != '' AND t.is_completed = 0 ORDER BY t.deadline_date ASC;";
    return queryJson(sql);
}

// Analytics
std::string TaskRepository::getDashboardStats() {
    std::string today = getToday();
    std::stringstream ss; ss << "{";
    sqlite3_stmt* stmt;
    sqlite3_prepare_v2(db, "SELECT COUNT(*) FROM tasks WHERE is_completed=0", -1, &stmt, 0); if(sqlite3_step(stmt)==SQLITE_ROW) ss << "\"total_active\": " << sqlite3_column_int(stmt, 0) << ","; sqlite3_finalize(stmt);
    sqlite3_prepare_v2(db, ("SELECT COUNT(*) FROM tasks WHERE todo_date='" + today + "'").c_str(), -1, &stmt, 0); if(sqlite3_step(stmt)==SQLITE_ROW) ss << "\"today_count\": " << sqlite3_column_int(stmt, 0) << ","; sqlite3_finalize(stmt);
    sqlite3_prepare_v2(db, ("SELECT COUNT(*) FROM tasks WHERE deadline_date < '" + today + "' AND is_completed=0").c_str(), -1, &stmt, 0); if(sqlite3_step(stmt)==SQLITE_ROW) ss << "\"overdue_count\": " << sqlite3_column_int(stmt, 0) << ","; sqlite3_finalize(stmt);
    sqlite3_prepare_v2(db, "SELECT COUNT(*) FROM tasks WHERE is_completed=1", -1, &stmt, 0); if(sqlite3_step(stmt)==SQLITE_ROW) ss << "\"done_total\": " << sqlite3_column_int(stmt, 0); sqlite3_finalize(stmt);
    ss << "}"; return ss.str();
}

std::string TaskRepository::getChartData(std::string type) {
    std::string sql;
    if (type == "priority") sql = "SELECT p.name, COUNT(t.id) as count FROM tasks t JOIN priorities p ON t.priority_id = p.id GROUP BY p.name";
    else if (type == "status") sql = "SELECT s.name, COUNT(t.id) as count FROM tasks t JOIN statuses s ON t.status_id = s.id GROUP BY s.name";
    else sql = "SELECT c.name, COUNT(t.id) as count FROM tasks t JOIN categories c ON t.category_id = c.id GROUP BY c.name";
    return queryJson(sql);
}

// Settings wrappers
void TaskRepository::addCategory(std::string name, std::string color) { executeQuery("INSERT INTO categories (name, color) VALUES ('" + name + "', '" + color + "');"); }
void TaskRepository::deleteCategory(int id) { executeQuery("DELETE FROM categories WHERE id=" + std::to_string(id)); executeQuery("UPDATE tasks SET category_id=1 WHERE category_id=" + std::to_string(id)); }
void TaskRepository::addPriority(std::string name, std::string color, int level) { executeQuery("INSERT INTO priorities (name, color, level) VALUES ('" + name + "', '" + color + "', " + std::to_string(level) + ");"); }
void TaskRepository::deletePriority(int id) { executeQuery("DELETE FROM priorities WHERE id=" + std::to_string(id)); executeQuery("UPDATE tasks SET priority_id=1 WHERE priority_id=" + std::to_string(id)); }
void TaskRepository::addStatus(std::string name, std::string icon) { executeQuery("INSERT INTO statuses (name, icon) VALUES ('" + name + "', '" + icon + "');"); }
void TaskRepository::deleteStatus(int id) { executeQuery("DELETE FROM statuses WHERE id=" + std::to_string(id)); executeQuery("UPDATE tasks SET status_id=1 WHERE status_id=" + std::to_string(id)); }