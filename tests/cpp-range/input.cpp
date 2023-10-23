#include <vector>

#include "FaultMacros.h"

int main() {
  std::vector<int> res;
  for (int i : res) {
    res.push_back(i * 8);
  }
}
