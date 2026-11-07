#include "tls-common.h"
IMP U32 GetCurrentThreadId(void);
static U32 process_attach,thread_attach;
BOOL DllMain(HMODULE m,U32 reason,void*r){
 (void)m;(void)r;
 if(reason==1&&GetCurrentThreadId())++process_attach;
 if(reason==2)++thread_attach;
 return 1;
}
__declspec(dllexport) void QueryControlCounts(U32*out){out[0]=process_attach;out[1]=thread_attach;}
