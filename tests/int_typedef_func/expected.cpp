#include "FaultMacros.h"

#include <cstdint>

std::uint64_t func() {
  FAULT_RETURN_INT unsigned i = FAULT_INT(0U);
  FAULT_RETURN_INT FAULT_CONDITIONAL i += FAULT_INT(23U);
  FAULT_RETURN_INT return FAULT_INT(i * FAULT_INT(8U));
}
