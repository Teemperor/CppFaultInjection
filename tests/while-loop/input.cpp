#include <vector>

#include "FaultMacros.h"

int main() {
  std::vector<int> res;
  int i = 0;
  while(true) {
    res.push_back(i * 8);
  }
}
