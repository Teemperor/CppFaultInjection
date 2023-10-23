#include <vector>

#include "FaultMacros.h"

int main() {
  FAULT_RETURN_INT std::vector<int> res;
  FAULT_RETURN_INT for (int i = FAULT_INT(0); i < FAULT_INT(100); i++) {
    FAULT_RETURN_INT res.push_back(i * FAULT_INT(8));
  }
}
