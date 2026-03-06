#ifndef HABITLOG_H
#define HABITLOG_H

#include "ISerializable.h"
#include <string>
#include <sstream>

class HabitLog : public ISerializable {
public:
    int id;
    int habitId;
    std::string date;

    HabitLog(int id, int hId, std::string d) : id(id), habitId(hId), date(d) {}

    std::string toJson() const override {
        std::stringstream ss;
        ss << "{\"id\": " << id << ", \"habit_id\": " << habitId << ", \"date\": \"" << date << "\"}";
        return ss.str();
    }
};

#endif