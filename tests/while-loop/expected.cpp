#include <vector>

#include "FaultMacros.h"

int main() {
  FAULT_RETURN_INT std::vector<int> res;
  FAULT_RETURN_INT int i = FAULT_INT(0);
  FAULT_RETURN_INT while(true) {
    FAULT_RETURN_INT FAULT_BREAK FAULT_CONDITIONAL res.push_back(FAULT_INT(i * 8));
  }
}
