#ifndef USER_H_
#define USER_H_

#include <string>

namespace auth
{

class User {
 public:
    User(int64_t id): id_(id) {}

    User(): User(-1) {}

    int64_t GetId() const {
        return id_;
    }

    std::string GetStringId() const {
        return std::to_string(id_);
    }

    std::string GetDataFile() const;

    std::string GetRequestsFile() const;

    void SetId(int64_t id) {
        id_ = id;
    }
 private:
    int64_t id_;
};

}  //  namespace auth

#endif
