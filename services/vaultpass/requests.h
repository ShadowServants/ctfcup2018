#ifndef REQUESTS_H_
#define REQUESTS_H_

#include <string>
#include <string.h>

namespace requests 
{

static constexpr size_t kRequestMessageSize = 1024;

class Request{
 public:
  Request(): requester_id_(-1), is_access_granted_(0) {}

  Request(int64_t requester_id, const std::string& message);

  std::string GetMessage() const;

  int64_t GetRequester() const {
    return requester_id_;
  }

  bool IsAccessGranted() const {
    return is_access_granted_ != 0;
  }

  void GrantAccess() {
    is_access_granted_ = 1;
  }

 private:
  int64_t requester_id_;
  char message_[kRequestMessageSize];
  int is_access_granted_;
};

// Read next Request from fd. Assumes, that we are holding a read lock
// and that the file contains a list of Request in binary format.
bool ReadNext(int fd, Request *request);

// Read i-th Request from fd. Assumes, that we are holding a read lock
// and that the file contains a list of Request in binary format.
bool ReadPos(int fd, int pos, Request *request);

// Append Request to fd. Assumes, that we are holding a write lock
// and that the file contains a list of Request in binary format.
bool WriteAppend(int fd, const Request &request);

// Rewrite Request on i-th position in fd. Assumes, that we are holding a write 
// lock and that the file contains a list of Request in binary format.
bool WritePos(int fd, int pos, const Request &request);

}  // namespace requests

#endif
