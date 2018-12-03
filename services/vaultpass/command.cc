#include "command.h"
#include "settings.h"
#include "requests.h"

#include <iostream> 
#include <fcntl.h>
#include <sys/file.h>
#include <unistd.h>
#include <vector>

void AddData(const auth::User &user, const std::string &contract_data) {
  FILE *file = fopen(user.GetDataFile().c_str(), "a");
  if (!file) {
    std::cout << "Failed to open data file" << std::endl;
    return;
  }
  setbuf(file, nullptr);
  flock(fileno(file), LOCK_EX);
  fprintf(file, "%s\n", contract_data.c_str());
  flock(fileno(file), LOCK_UN);
  fclose(file);
  std::cout << "Data successfully added" << std::endl;
}

void SendAccessRequest(const auth::User &user, int64_t user_id,
                       const std::string& request_comment) {
  requests::Request request(user.GetId(), request_comment);
  int fd = open(auth::User(user_id).GetRequestsFile().c_str(),
                O_APPEND | O_WRONLY);
  if (fd == -1) {
    std::cout << "User doesn't exist" << std::endl;
    return;
  }
  flock(fd, LOCK_EX);
  if (!requests::WriteAppend(fd, request)) {
    flock(fd, LOCK_UN);
    close(fd);
    std::cout << "Internal error" << std::endl;
    return;
  }
  flock(fd, LOCK_UN);
  close(fd);
  std::cout << "Request successfully send" << std::endl;
}

void ListAccessRequests(const auth::User &user) {
  int fd = open(user.GetRequestsFile().c_str(), O_RDONLY);
  if (fd == -1) {
    std::cout << "Internal error" << std::endl;
    return;
  }
  flock(fd, LOCK_SH);
  std::vector<requests::Request> requests;
  requests::Request request;
  while (requests::ReadNext(fd, &request)) {
    requests.push_back(request);
  }
  flock(fd, LOCK_UN);
  close(fd);
  if (requests.empty()) {
    std::cout << "You don't have any access requests" << std::endl;
  }
  for (size_t i = 0; i < requests.size(); i++) {
    std::cout << "request_id = " << i << "\n"
              << "message = " << requests[i].GetMessage() << "\n"
              << "access_granted = " << requests[i].IsAccessGranted()
              << std::endl;
  }
}

void AcceptAccessRequest(const auth::User &user, int64_t request_id) {
  int fd = open(user.GetRequestsFile().c_str(), O_RDWR);
  if (fd == -1) {
    std::cout << "Internal error" << std::endl;
    return;
  }
  flock(fd, LOCK_EX);
  requests::Request request;
  if (!requests::ReadPos(fd, request_id, &request)) {
    std::cout << "Request not found" << std::endl;
  }
  request.GrantAccess();
  if (!requests::WritePos(fd, request_id, request)) {
    std::cout << "Internal error" << std::endl;
  }
  flock(fd, LOCK_UN);
  close(fd);
  std::cout << "Access granted" << std::endl;
}

void GetUserData(const auth::User &user, int64_t user_id) {
  // Check if user trying to retrieve his own data
  if (user.GetId() != user_id) {
    // Additional validation is required.
    int fd = open(auth::User(user_id).GetRequestsFile().c_str(), O_RDONLY);
    if (fd == -1) {
      std::cout << "User doesn't exist" << std::endl;
      return;
    }
    bool ok = 0;
    flock(fd, LOCK_SH);
    requests::Request request;
    while (requests::ReadNext(fd, &request)) {
      if (request.GetRequester() == user.GetId() &&
          request.IsAccessGranted()) {
        ok = 1;
        break;
      }
    }
    flock(fd, LOCK_UN);
    close(fd);
    if (!ok) {
      std::cout << "Permissions denied" << std::endl;
      return;
    }
  }
  FILE *file = fopen(auth::User(user_id).GetDataFile().c_str(), "r");
  setbuf(file, nullptr);
  flock(fileno(file), LOCK_SH);
  
  char buffer[4096];
  bool data_found = false;
  while (fgets(buffer, 4096, file)) {
    std::cout << buffer;
    data_found = true;
  }
  if (!data_found) {
    std::cout << "No data found... yet.\n";
  }
  flock(fileno(file), LOCK_UN);
  fclose(file);
  std::cout << std::flush;
}
