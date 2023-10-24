#include "FaultMacros.h"

int func() {
  FAULT_RETURN_INT if (true) { FAULT_RETURN_INT return FAULT_INT(3); }
  FAULT_RETURN_INT return FAULT_INT(4);
}
