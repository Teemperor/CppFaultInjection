#include "FaultMacros.h"

static int global = 3;

int func() {
  static int i = 0;
  return i;
}
