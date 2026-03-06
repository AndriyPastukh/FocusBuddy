#ifndef BASE_REPOSITORY_H
#define BASE_REPOSITORY_H

#include <string>
#include <vector>
#include <iostream>
#include <sstream>
#include "../../lib/sqlite3.h" 

class BaseRepository {
protected:
    sqlite3* db;

public:
    // Конструктор приймає готове з'єднання з базою
    BaseRepository(sqlite3* dbConnection) : db(dbConnection) {}
    
    virtual ~BaseRepository() = default;

    // Метод для виконання INSERT, UPDATE, DELETE
    void executeQuery(const std::string& sql) {
        char* errMsg = 0;
        int rc = sqlite3_exec(db, sql.c_str(), 0, 0, &errMsg);
        if (rc != SQLITE_OK) {
            std::cerr << "SQL Error: " << errMsg << "\nQuery: " << sql << std::endl;
            sqlite3_free(errMsg);
        }
    }

    // Метод для SELECT, який повертає JSON-рядок
    std::string queryJson(const std::string& sql) {
        sqlite3_stmt* stmt;
        if (sqlite3_prepare_v2(db, sql.c_str(), -1, &stmt, 0) != SQLITE_OK) {
            std::cerr << "Prepare failed: " << sqlite3_errmsg(db) << std::endl;
            return "[]";
        }

        std::stringstream json;
        json << "[";
        
        bool firstRow = true;
        while (sqlite3_step(stmt) == SQLITE_ROW) {
            if (!firstRow) json << ",";
            json << "{";
            
            int colCount = sqlite3_column_count(stmt);
            for (int i = 0; i < colCount; i++) {
                if (i > 0) json << ",";
                
                const char* name = sqlite3_column_name(stmt, i);
                const char* val = (const char*)sqlite3_column_text(stmt, i);
                
                json << "\"" << name << "\": \"" << (val ? val : "") << "\"";
            }
            json << "}";
            firstRow = false;
        }
        
        json << "]";
        sqlite3_finalize(stmt);
        return json.str();
    }
};

#endif  