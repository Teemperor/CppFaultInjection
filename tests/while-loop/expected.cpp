#include <vector>

#include "FaultMacros.h"

int main() {
  FAULT_RETURN_INT std::vector<int> res;
  FAULT_RETURN_INT int i = FAULT_INT(0);
  FAULT_RETURN_INT while(true) {
    FAULT_RETURN_INT FAULT_BREAK res.push_back(i * FAULT_INT(8));
  }
}