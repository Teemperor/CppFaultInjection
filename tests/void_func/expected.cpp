#include "FaultMacros.h"

void foo() {
  FAULT_RETURN int i = FAULT_INT(3);
  FAULT_RETURN FAULT_CONDITIONAL i += FAULT_INT(123);
}
