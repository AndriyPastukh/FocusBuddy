#ifndef HABIT_H
#define HABIT_H

#include "ISerializable.h"
#include <string>
#include <sstream>

class Habit : public ISerializable {
public:
    int id;
    std::string title;
    int difficultyId;
    int targetStreak;

    Habit(int id, std::string title, int diffId, int target)
        : id(id), title(title), difficultyId(diffId), targetStreak(target) {}

    std::string toJson() const override {
        std::stringstream ss;
        ss << "{\"id\": " << id << ", \"title\": \"" << title 
           << "\", \"difficulty_id\": " << difficultyId << ", \"target\": " << targetStreak << "}";
        return ss.str();
    }
};

#endif