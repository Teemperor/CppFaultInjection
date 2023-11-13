#include "FaultMacros.h"

int func() {
  FAULT_RETURN_INT if (FAULT_BOOL(FAULT_INT(FAULT_INT(1) + FAULT_INT(1)) < FAULT_INT(2)))
    return FAULT_INT(4);
  FAULT_RETURN_INT return FAULT_INT(0);
}
