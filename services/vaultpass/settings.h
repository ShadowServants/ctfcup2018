#ifndef SETTINGS_H_
#define SETTINGS_H_

namespace settings {

// Auth salt for hashing.
static constexpr char kSALT[] = "CMC3BFF";

// Name of the file that keeps track of current user count.
static constexpr char kUserCountFile[] = "user_count.txt";

// Directory, containing user data
static constexpr char kDataDir[] = "user_data/";

}  // namespace settings

#endif
