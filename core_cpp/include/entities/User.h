#ifndef USER_H
#define USER_H

#include "ISerializable.h"
#include <string>
#include <sstream>

class User : public ISerializable {
public:
    int id;
    std::string username;
    int xp;
    int level;
    std::string avatar;

    User(int id, std::string name, int xp, int level, std::string avatar)
        : id(id), username(name), xp(xp), level(level), avatar(avatar) {}

    float getProgressPercent() const {
        int xpNeeded = level * 100;
        return (float)xp / (float)xpNeeded;
    }

    std::string toJson() const override {
        std::stringstream ss;
        ss << "{\"id\": " << id << ", \"username\": \"" << username << "\", \"xp\": " << xp 
           << ", \"level\": " << level << ", \"avatar\": \"" << avatar << "\", \"progress\": " << getProgressPercent() << "}";
        return ss.str();
    }
};

#endif