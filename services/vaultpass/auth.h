#ifndef AUTH_H_
#define AUTH_H_

#include "sha256.h"
#include "user.h"

#include <string>

namespace auth {

// Validates the user_id and hash and populates the user pointer.
bool Authenticate(const std::string &user_id,
                  const std::string &hash, User *user);

// Creates a new user, returns the auth hash and populates User pointer.
// Returns empty string on error.
std::string RegisterUser(User *user);

}  // namespace auth

#endif
