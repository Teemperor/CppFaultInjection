#include "FaultMacros.h"

int func() {
  FAULT_RETURN_INT static int i = 0;
  FAULT_RETURN_INT return FAULT_INT(i);
}
