#include <vector>

#include "FaultMacros.h"

int main() {
  FAULT_RETURN_INT std::vector<int> res;
  FAULT_RETURN_INT for (int i : res) {
    FAULT_RETURN_INT FAULT_BREAK FAULT_CONDITIONAL res.push_back(FAULT_INT(FAULT_INT(i) * FAULT_INT(8)));
  }
}
