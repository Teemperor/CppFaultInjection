#pragma once

extern "C" {
char *getenv(const char *) noexcept(true);
}

namespace Faults {
inline bool isActive(const char *BugName) { return getenv(BugName) != nullptr; }
} // namespace Faults

#define FAULT_STRINGIZE_DETAIL(x) #x
#define FAULT_STRINGIZE(x) FAULT_STRINGIZE_DETAIL(x)

#define FAULT_GENERATE_UID                                                     \
  "INJECTED_FAULT_" __FILE_NAME__ "__LINE__" FAULT_STRINGIZE(                  \
      __LINE__) "__REASON__" FAULT_STRINGIZE(__COUNTER__)

#define FAULT_IF_IS_ACTIVE(SUFFIX)                                             \
  if (Faults::isActive(FAULT_GENERATE_UID "_" FAULT_STRINGIZE(SUFFIX)))

#define FAULT_IS_ACTIVE(SUFFIX)                                                \
  Faults::isActive(FAULT_GENERATE_UID "_" FAULT_STRINGIZE(SUFFIX))

#define FAULT_IF_IS_ACTIVE_SUFFIX(SUFFIX) if (FAULT_IS_ACTIVE(SUFFIX))

#define FAULT_RETURN FAULT_IF_IS_ACTIVE(RETURN_VOID) return;

#define FAULT_RETURN_INT FAULT_IF_IS_ACTIVE_SUFFIX(RETURN_ZERO) return 0;

#define FAULT_CONDITIONAL if (!FAULT_IS_ACTIVE(CONDITIONAL_SKIP))

#define FAULT_RETURN_BOOL                                                      \
  FAULT_IF_IS_ACTIVE(RETURN_TRUE) return true;                                 \
  FAULT_IF_IS_ACTIVE(RETURN_FALSE) return false;

#define FAULT_RETURN_VAL(VAL) FAULT_IF_IS_ACTIVE(RETURN_VAL) return (VAL);

#define FAULT_BREAK FAULT_IF_IS_ACTIVE(BREAK) break;

#define FAULT_INT_IMPL(NUM, TYPE)                                              \
  (FAULT_IS_ACTIVE(INT_LESS)                                                   \
       ? ((TYPE)((NUM) - (TYPE)1))                                             \
       : (FAULT_IS_ACTIVE(INT_MORE)                                            \
              ? ((TYPE)((NUM) + (TYPE)1))                                      \
              : (FAULT_IS_ACTIVE(INT_INVERSE) ? ((TYPE)(~(NUM)))               \
                                              : ((TYPE)(NUM)))))
#define FAULT_INT(NUM) ((decltype(NUM))FAULT_INT_IMPL(NUM, decltype(NUM)))

#define FAULT_BOOL_IMPL(NUM, TYPE)                                             \
  (FAULT_IS_ACTIVE(BOOL_FLIP) ? ((TYPE)(!(NUM))) : ((TYPE)(NUM)))
#define FAULT_BOOL(NUM) ((decltype(NUM))FAULT_BOOL_IMPL(NUM, decltype(NUM)))

#define FAULT_IF_COND                                                          \
  FAULT_IS_ACTIVE(FORCE_ENABLE_COND) || !FAULT_IS_ACTIVE(FORCE_DISABLE_COND) &&
