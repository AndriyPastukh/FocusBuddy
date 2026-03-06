#ifndef STATUS_H
#define STATUS_H

#include "ISerializable.h"
#include <string>
#include <sstream>

class Status : public ISerializable {
public:
    int id;
    std::string name;
    std::string icon;

    Status(int id, std::string name, std::string icon)
        : id(id), name(name), icon(icon) {}

    std::string toJson() const override {
        std::stringstream ss;
        ss << "{\"id\": " << id << ", \"name\": \"" << name << "\", \"icon\": \"" << icon << "\"}";
        return ss.str();
    }
};

#endif