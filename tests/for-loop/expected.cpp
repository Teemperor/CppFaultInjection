#include <vector>

#include "FaultMacros.h"

int main() {
  FAULT_RETURN_INT std::vector<int> res;
  FAULT_RETURN_INT for (int i = FAULT_INT(0); i < FAULT_INT(100); i++) {
    FAULT_RETURN_INT FAULT_BREAK FAULT_CONDITIONAL res.push_back(FAULT_INT(i * 8));
  }
}
