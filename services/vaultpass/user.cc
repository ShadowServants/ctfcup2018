#include "user.h"
#include "settings.h"

namespace auth
{

std::string User::GetDataFile() const {
  return settings::kDataDir + GetStringId() + ".data";
}

std::string User::GetRequestsFile() const {
  return settings::kDataDir + GetStringId() + ".requests";
}

}  // namespace auth
