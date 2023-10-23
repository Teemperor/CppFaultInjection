#include "FaultMacros.h"

long func() {
  FAULT_RETURN_INT int i = FAULT_INT(0);
  FAULT_RETURN_INT i += FAULT_INT(23);
  FAULT_RETURN_INT return i * FAULT_INT(8);
}
