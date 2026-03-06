#ifndef CATEGORY_H
#define CATEGORY_H

#include "ISerializable.h"
#include <string>
#include <sstream>

class Category : public ISerializable {
public:
    int id;
    std::string name;
    std::string color;

    Category(int id, std::string name, std::string color)
        : id(id), name(name), color(color) {}

    std::string toJson() const override {
        std::stringstream ss;
        ss << "{\"id\": " << id << ", \"name\": \"" << name << "\", \"color\": \"" << color << "\"}";
        return ss.str();
    }
};

#endif