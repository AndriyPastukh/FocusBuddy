#ifndef ISERIALIZABLE_H
#define ISERIALIZABLE_H

#include <string>

class ISerializable {
public:
    virtual ~ISerializable() {}
    virtual std::string toJson() const = 0;
};

#endif