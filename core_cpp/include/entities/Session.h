#ifndef SESSION_H
#define SESSION_H

#include "ISerializable.h"
#include <string>
#include <sstream>

class Session : public ISerializable {
public:
    int id;
    std::string startTime;
    int durationMinutes;
    int xpEarned;
    std::string taskTitle;

    Session(int id, std::string start, int duration, int xp, std::string title)
        : id(id), startTime(start), durationMinutes(duration), xpEarned(xp), taskTitle(title) {}

    std::string toJson() const override {
        std::stringstream ss;
        ss << "{\"id\": " << id << ", \"start_time\": \"" << startTime << "\", \"duration\": " << durationMinutes 
           << "\", \"xp\": " << xpEarned << ", \"task_title\": \"" << taskTitle << "\"}";
        return ss.str();
    }
};

#endif