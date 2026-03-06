#ifndef GOAL_H
#define GOAL_H

#include "ISerializable.h"
#include <string>
#include <sstream>

class Goal : public ISerializable {
public:
    int id;
    std::string title;
    std::string deadline;
    int categoryId;
    bool isCompleted;

    Goal(int id, std::string t, std::string d, int cat, bool comp)
        : id(id), title(t), deadline(d), categoryId(cat), isCompleted(comp) {}

    std::string toJson() const override {
        std::stringstream ss;
        ss << "{\"id\": " << id << ", \"title\": \"" << title << "\", \"deadline\": \"" << deadline 
           << "\", \"category_id\": " << categoryId << ", \"is_completed\": " << (isCompleted ? 1 : 0) << "}";
        return ss.str();
    }
};

#endif