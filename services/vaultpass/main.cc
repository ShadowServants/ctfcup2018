#include "auth.h"
#include "settings.h"
#include "command.h"

#include <iostream>
#include <string>
#include <unordered_map>

namespace {

constexpr char kInitMessage[] =
  (
  "Welcome to VaultPass, a secure and easy way to store your secrets in \n"
  "the event of atomic annihilation\n"
  "\n"
  "If you want to register, type 'register' and press Enter\n"
  "If you want to login, type your login, user_id and auth token\n"
  "separated by newline");

constexpr char kFailedLoginMessage[] =
  ("Login attempt failed");

constexpr char kLoginSuccess[] =
  ("Login completed");

constexpr char kRegistrationSuccess[] = 
  (
  "Registration completed. Write down your auth token,\n"
  "since its recovery is impossible");

constexpr char kRegistrationFailure[] =
  ("Registration attempt failed");

constexpr char kHelpMessage[] = 
  (
  "\n"
  "0) To see this message again, type 'help'\n"
  "1) If you want to exit, type 'exit'\n"
  "2) If you want to add password data, type 'add_data' and the\n"
  "  data, separated by newline\n"
  "3) If you want to send access request to another user, type\n"
  "  'send_request', the user_id and your request message, \n"
  "  separated by newline\n"
  "4) If you want to list requests for your data, type 'list_requests'\n"
  "5) If you want to accept request for your data, type\n"
  "  'accept_request' and the number of request, separated by newline\n"
  "6) If you want get password data of the user, including yourself, type\n"
  "  'get_data' and the user_id, separated by newline\n");

}  // namespace

std::string GetToken() {
  std::string s;
  int c;
  while ((c = getchar()) != EOF) {
    if (c == '\n') {
      break;
    }
    s += (char)c;
  }
  return s;
}

int64_t GetId() {
  const auto token = GetToken();
  auto id = std::atoll(token.c_str());
  return id;
}

auth::User InitLoop() {
  std::cout << kInitMessage << std::endl;
  std::string command;
  while ((command = GetToken()) != "") {
    if (command == "register") {
      auth::User user;
      const auto hash = auth::RegisterUser(&user);
      if (hash == "") {
        std::cout << kRegistrationFailure << std::endl;
        continue;
      }
      std::cout << kRegistrationSuccess << "\n" 
                << "user_id = " << user.GetId() << "\n"
                << "auth_token = " << hash << std::endl;
      return user;
    }
    else if (command == "login") {
      const auto user_id = GetToken();
      const auto hash = GetToken();
      auth::User user;
      if (auth::Authenticate(user_id, hash, &user)) {
        std::cout << kLoginSuccess << std::endl;
        return user;
      }
      std::cout << kFailedLoginMessage << std::endl;
    }
    else {
      std::cout << "Invalid command" << std::endl;
    }
    std::cout << kInitMessage << std::endl;
  }
  return {-1};
}

void CommandLoop(const auth::User &user) {
  std::cout << kHelpMessage << std::endl;
  std::string command;
  while ((command = GetToken()) != "") {
    if (command == "help") {
      std::cout << kHelpMessage << std::endl;
    }
    else if (command == "exit") {
      return;
    }
    else if (command == "add_data") {
      const auto data = GetToken();
      AddData(user, data);
    }
    else if (command == "send_request") {
      const auto user_id = GetId();
      if (user_id <= 0) {
        std::cout << "Incorrect user_id" << std::endl;
        continue;
      }
      const auto comment = GetToken();
      SendAccessRequest(user, user_id, comment);
    }
    else if (command == "list_requests") {
      ListAccessRequests(user);
    }
    else if (command == "accept_request") {
      const auto request_id = GetId();
      if (request_id < 0) {
        std::cout << "Incorrect request_id" << std::endl;
        continue;
      }
      AcceptAccessRequest(user, request_id);
    }
    else if (command == "get_data") {
      const auto user_id = GetId();
      if (user_id <= 0) {
        std::cout << "Incorrect user_id" << std::endl;
      }
      GetUserData(user, user_id);
    }
    else {
      std::cout << "Invalid command" << std::endl;
    }
  }
}

int main() {
  auth::User user = InitLoop();
  if (user.GetId() == -1) {
    return 0;
  }
  CommandLoop(user);
}
