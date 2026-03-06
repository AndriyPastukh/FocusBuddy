#ifndef DAILYREFLECTION_H
#define DAILYREFLECTION_H

#include "ISerializable.h"
#include <string>
#include <sstream>

class DailyReflection : public ISerializable {
public:
    std::string date;
    int mood;
    int energy;
    int motivation;

    DailyReflection(std::string d, int m, int e, int mot)
        : date(d), mood(m), energy(e), motivation(mot) {}

    std::string toJson() const override {
        std::stringstream ss;
        ss << "{\"date\": \"" << date << "\", \"mood\": " << mood 
           << ", \"energy\": " << energy << ", \"motivation\": " << motivation << "}";
        return ss.str();
    }
};

#endif