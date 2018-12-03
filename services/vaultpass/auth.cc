#include "auth.h"
#include "settings.h"

#include <stdio.h>
#include <string.h>
#include <sys/file.h>
#include <cinttypes>

#include <iostream>

namespace auth {
namespace
{

std::string CalcHash(const std::string &user_id) {
  unsigned char sha256[SHA256_BLOCK_SIZE];
  std::string to_hash = user_id + settings::kSALT;
  const char *s = to_hash.c_str();
  SHA256_CTX ctx;
  sha256_init(&ctx);
  sha256_update(&ctx, (unsigned char*)s,
                strlen(s));
  sha256_final(&ctx, sha256);
  char buffer[SHA256_BLOCK_SIZE * 2 + 1];
  for (int i = 0; i < SHA256_BLOCK_SIZE; i++) {
    sprintf(buffer + (i*2), "%02x", sha256[i]);
  }
  buffer[SHA256_BLOCK_SIZE] = '\0';
  return std::string(buffer);
}

} //  namespace 

bool Authenticate(const std::string &user_id,
                  const std::string &hash, User *user) {
    if (CalcHash(user_id) != hash) {
      return false;
    }
    const int64_t id = std::atoll(user_id.c_str());
    if (id <= 0) {
      return false;
    }
    user->SetId(id);
    return true;
}

std::string RegisterUser(User *user) {
  FILE *file = fopen(settings::kUserCountFile, "r+");
  if (!file) {
    return "";
  }
  setbuf(file, nullptr);
  flock(fileno(file), LOCK_EX);

  int64_t current_user;
  if (fscanf(file, "%" PRId64, &current_user) < 0) {
    flock(fileno(file), LOCK_UN);
    fclose(file);
    return "";
  }
  fseek(file, 0, SEEK_SET);
  fprintf(file, "%" PRId64, current_user + 1);

  flock(fileno(file), LOCK_UN);
  fclose(file);

  user->SetId(current_user);

  // Creating user files.
  file = fopen(user->GetDataFile().c_str(), "w");
  fclose(file);
  file = fopen(user->GetRequestsFile().c_str(), "w");
  fclose(file);

  return CalcHash(std::to_string(current_user));
}

}  // namespace auth
