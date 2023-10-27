#include "FaultMacros.h"

static int global = FAULT_INT(3);

int func() {
  FAULT_RETURN_INT static int i = 0;
  FAULT_RETURN_INT return FAULT_INT(i);
}
