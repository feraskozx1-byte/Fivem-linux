#include "winmini.h"
#define TLS_COOKIE 0x11223344u
struct TLS_OBSERVATION {U32 cookie,order,errors,pad_first,pad_last;SIZE address;};
typedef void (*QueryTLS)(struct TLS_OBSERVATION*);
typedef void (*SetTLS)(U32);
IMP HANDLE CreateThread(void*,SIZE,U32(*)(void*),void*,U32,U32*);
IMP HANDLE CreateEventW(void*,BOOL,BOOL,const U16*);
IMP BOOL SetEvent(HANDLE);
IMP U32 WaitForSingleObject(HANDLE,U32);
IMP BOOL DisableThreadLibraryCalls(HMODULE);
