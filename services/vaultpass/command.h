#ifndef COMMAND_H_
#define COMMAND_H_ 
 
#include "auth.h"

void AddData(const auth::User &user, const std::string &contract_data);

void SendAccessRequest(const auth::User &user, int64_t user_id,
                       const std::string &request_comment);

void ListAccessRequests(const auth::User &user);

void AcceptAccessRequest(const auth::User &user, int64_t request_id);

void GetUserData(const auth::User &user, int64_t user_id);

#endif
