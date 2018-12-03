#include "requests.h"

#include <unistd.h>

namespace requests
{

namespace 
{

bool SafeRead(int fd, char *buffer, int sz) {
  int total_read = 0;
  while (total_read != sz) {
    int cur_read = read(fd, &buffer[total_read], sz - total_read);
    if (cur_read <= 0) {
      return false;
    }
    total_read += cur_read;
  }  
  return true;
}

bool SafeWrite(int fd, char *buffer, int sz) {
  int cur_written = 0;
  while (cur_written != sz) {
    int written = write(fd, &buffer[cur_written], sz - cur_written);
    if (written <= 0) {
      return false;
    }
    cur_written += written;
  }
  return true;
}

}  // namespace

Request::Request(int64_t requester_id, const std::string &message) {
    requester_id_ = requester_id;
    is_access_granted_ = 0;
    size_t len = std::min(kRequestMessageSize, strlen(message.c_str()));
    const char *s = message.c_str();
    for (size_t i = 0; i <= len; i++) {
      message_[i] = s[i];
    }
}

std::string Request::GetMessage() const {
  std::string s;
  for (size_t i = 0; i < kRequestMessageSize; i++) {
    if (message_[i] == '\0') {
      break;
    }
    s += message_[i];
  }
  return s;
}

bool ReadNext(int fd, Request *request) {
  return SafeRead(fd, (char*)request, sizeof(Request));
}

bool ReadPos(int fd, int pos, Request *request) {
  if (lseek(fd, pos * sizeof(Request), SEEK_SET) < 0) {
    return false;
  }
  return ReadNext(fd, request);
}

bool WriteAppend(int fd, const Request &request) {
  return SafeWrite(fd, (char*)&request, sizeof(Request));
}

bool WritePos(int fd, int pos, const Request &request) {
  if (lseek(fd, pos * sizeof(Request), SEEK_SET) < 0) {
    return false;
  }
  return WriteAppend(fd, request);
}

}  // namespace requests
