#include "FaultMacros.h"

#include <cstdint>

std::uint64_t func() {
  unsigned i = 0U;
  i += 23U;
  return i * 8U;
}
