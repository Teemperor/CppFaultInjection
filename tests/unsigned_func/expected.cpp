#include "FaultMacros.h"

unsigned func() {
  FAULT_RETURN_INT unsigned i = FAULT_INT(0U);
  FAULT_RETURN_INT i += FAULT_INT(23U);
  FAULT_RETURN_INT return i * FAULT_INT(8U);
}
