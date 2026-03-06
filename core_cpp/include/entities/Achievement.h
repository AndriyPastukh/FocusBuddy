#ifndef ACHIEVEMENT_H
#define ACHIEVEMENT_H

#include "ISerializable.h"
#include <string>
#include <sstream>

class Achievement : public ISerializable {
public:
    std::string title;
    std::string description;
    std::string icon;
    bool isUnlocked;

    Achievement(std::string t, std::string d, std::string i, bool unlocked)
        : title(t), description(d), icon(i), isUnlocked(unlocked) {}

    std::string toJson() const override {
        std::stringstream ss;
        ss << "{\"title\": \"" << title << "\", \"desc\": \"" << description 
           << "\", \"icon\": \"" << icon << "\", \"unlocked\": " << (isUnlocked ? "true" : "false") << "}";
        return ss.str();
    }
};

#endif