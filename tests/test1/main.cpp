#include <vector>

#include "FaultMacros.h"

int main() {
  std::vector<int> res;
  for (int i = 0; i < 100; i++) {
    res.push_back(i * 8);
  }
}
