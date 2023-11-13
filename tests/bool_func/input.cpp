#include "FaultMacros.h"

int func() {
  if (1 + 1 < 2)
    return 4;
  return 0;
}
