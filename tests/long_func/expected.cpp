#include "FaultMacros.h"

long func() {
  FAULT_RETURN_INT int i = FAULT_INT(0);
  FAULT_RETURN_INT FAULT_CONDITIONAL i += FAULT_INT(23);
  FAULT_RETURN_INT return FAULT_INT(i * FAULT_INT(8));
}
