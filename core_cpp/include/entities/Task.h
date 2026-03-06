#ifndef TASK_H
#define TASK_H

#include "ISerializable.h"
#include <string>
#include <sstream>

class Task : public ISerializable {
public:
    int id;
    std::string title;
    std::string todoDate;
    std::string deadline;
    int priorityId;
    int categoryId;
    int statusId;
    bool isCompleted;

    Task(int id, std::string title, std::string date, std::string dline, int prio, int cat, int stat, bool completed)
        : id(id), title(title), todoDate(date), deadline(dline), 
          priorityId(prio), categoryId(cat), statusId(stat), isCompleted(completed) {}

    std::string toJson() const override {
        std::stringstream ss;
        ss << "{\"id\": " << id << ", \"title\": \"" << title << "\", \"todo_date\": \"" << todoDate 
           << "\", \"deadline\": \"" << deadline << "\", \"priority_id\": " << priorityId 
           << ", \"category_id\": " << categoryId << ", \"status_id\": " << statusId 
           << ", \"is_completed\": " << (isCompleted ? 1 : 0) << "}";
        return ss.str();
    }
};

#endif