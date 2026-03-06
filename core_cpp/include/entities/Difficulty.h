#ifndef DIFFICULTY_H
#define DIFFICULTY_H

#include "ISerializable.h"
#include <string>
#include <sstream>

class Difficulty : public ISerializable {
public:
    int id;
    std::string name;
    int score;

    Difficulty(int id, std::string name, int score)
        : id(id), name(name), score(score) {}

    std::string toJson() const override {
        std::stringstream ss;
        ss << "{\"id\": " << id << ", \"name\": \"" << name << "\", \"score\": " << score << "}";
        return ss.str();
    }
};

#endif