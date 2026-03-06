#ifndef PRIORITY_H
#define PRIORITY_H

#include "ISerializable.h"
#include <string>
#include <sstream>

class Priority : public ISerializable {
public:
    int id;
    std::string name;
    std::string color;
    int level;

    Priority(int id, std::string name, std::string color, int level)
        : id(id), name(name), color(color), level(level) {}

    std::string toJson() const override {
        std::stringstream ss;
        ss << "{\"id\": " << id << ", \"name\": \"" << name << "\", \"color\": \"" << color << "\", \"level\": " << level << "}";
        return ss.str();
    }
};

#endif