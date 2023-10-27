#include "FaultMacros.h"

int func() {
  static int i = 0;
  return i;
}
