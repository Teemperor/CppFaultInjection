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
  "INJECTED_FAULT_" __FILE_NAME__                                              \
  "_" FAULT_STRINGIZE(__LINE__) "_" FAULT_STRINGIZE(__COUNTER__)
#define FAULT_IF_IS_ACTIVE if (Faults::isActive(FAULT_GENERATE_UID))

#define FAULT_IS_ACTIVE_SUFFIX(SUFFIX)                                         \
  Faults::isActive(FAULT_GENERATE_UID "_" FAULT_STRINGIZE(SUFFIX))

#define FAULT_IF_IS_ACTIVE_SUFFIX(SUFFIX) if (FAULT_IS_ACTIVE_SUFFIX(SUFFIX))

#define FAULT_RETURN FAULT_IF_IS_ACTIVE return;

#define FAULT_RETURN_INT FAULT_IF_IS_ACTIVE_SUFFIX(TRUE) return 0; 

#define FAULT_CONDITIONAL FAULT_IF_IS_ACTIVE_SUFFIX(TRUE) return 0; 

#define FAULT_RETURN_BOOL                                                      \
  FAULT_IF_IS_ACTIVE_SUFFIX(TRUE) return true;                                 \
  FAULT_IF_IS_ACTIVE_SUFFIX(FALSE) return false;

#define FAULT_RETURN_VAL(VAL) FAULT_IF_IS_ACTIVE return (VAL);

#define FAULT_RETURN_VAL2(VAL1, VAL2)                                          \
  FAULT_IF_IS_ACTIVE_SUFFIX(OPT1) return VAL1;                                 \
  FAULT_IF_IS_ACTIVE_SUFFIX(OPT2) return VAL2;

#define FAULT_BREAK FAULT_IF_IS_ACTIVE break;

#define FAULT_INT_IMPL(NUM, TYPE)                                              \
  (FAULT_IS_ACTIVE_SUFFIX(LESS)                                                \
       ? ((TYPE)((NUM) - (TYPE)1))                                             \
       : (FAULT_IS_ACTIVE_SUFFIX(MORE)                                         \
              ? ((TYPE)((NUM) + (TYPE)1))                                      \
              : (FAULT_IS_ACTIVE_SUFFIX(INVERSE) ? ((TYPE)(~(NUM)))            \
                                                 : ((TYPE)(NUM)))))
#define FAULT_INT(NUM) ((decltype(NUM))FAULT_INT_IMPL(NUM, decltype(NUM)))

#define FAULT_IF_COND                                                          \
  FAULT_IS_ACTIVE_SUFFIX(FORCE_ON) || !FAULT_IS_ACTIVE_SUFFIX(FORCE_OFF) &&
