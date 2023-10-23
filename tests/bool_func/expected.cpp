#include "FaultMacros.h"

bool func() {
  FAULT_RETURN_BOOL int i = FAULT_INT(0);
  FAULT_RETURN_BOOL i += FAULT_INT(23);
  FAULT_RETURN_BOOL return true;
}
