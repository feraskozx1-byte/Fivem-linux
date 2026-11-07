#include "tls-common.h"
IMP U32 GetCurrentThreadId(void);
/* Own static TLS fixture: same raw-data length/alignment/3-callback shape as the
   public Adhesive TLS directory, without any security code or game imports. */
struct TLS_STATE {U32 cookie,order,errors;U8 pad[0x5484];};
_Static_assert(sizeof(struct TLS_STATE)==0x5490,"state plus 16-byte leading TLS marker");
U32 _tls_index;
#pragma section(".tls",read,write)
#pragma section(".tls$ZZZ",read,write)
__declspec(allocate(".tls")) char _tls_start;
__declspec(allocate(".tls$ZZZ")) char _tls_end;
static __declspec(thread) __declspec(align(16)) struct TLS_STATE state={TLS_COOKIE,0,0,{0}};
static void callback_a(void*m,U32 reason,void*r){
 (void)m;(void)r;
 if(reason==1||reason==2){
  if(!GetCurrentThreadId())++state.errors;
  if(state.cookie!=TLS_COOKIE||state.order!=0)++state.errors;
  for(U32 i=0;i<sizeof(state.pad);++i)if(state.pad[i]){++state.errors;break;}
  state.order=1;state.pad[0]=0xa5;state.pad[sizeof(state.pad)-1]=0x5a;
 }
}
static void callback_b(void*m,U32 reason,void*r){(void)m;(void)r;if(reason==1||reason==2)state.order=state.order*10+2;}
static void callback_c(void*m,U32 reason,void*r){(void)m;(void)r;if(reason==1||reason==2)state.order=state.order*10+3;}
typedef void (*CALLBACK)(void*,U32,void*);
#pragma section(".CRT$XLA",read)
#pragma section(".CRT$XLB",read)
#pragma section(".CRT$XLC",read)
#pragma section(".CRT$XLD",read)
#pragma section(".CRT$XLZ",read)
__declspec(allocate(".CRT$XLA")) const CALLBACK callbacks_start=0;
__declspec(allocate(".CRT$XLB")) const CALLBACK callbacks_a=callback_a;
__declspec(allocate(".CRT$XLC")) const CALLBACK callbacks_b=callback_b;
__declspec(allocate(".CRT$XLD")) const CALLBACK callbacks_c=callback_c;
__declspec(allocate(".CRT$XLZ")) const CALLBACK callbacks_end=0;
struct TLS_DIR {SIZE start,end,index,callbacks;U32 zeros,flags;};
const struct TLS_DIR _tls_used={(SIZE)&_tls_start,(SIZE)&_tls_end,(SIZE)&_tls_index,(SIZE)(&callbacks_start+1),0,0x500000};
#pragma comment(linker,"/include:_tls_used")
#pragma comment(linker,"/include:callbacks_a")
#pragma comment(linker,"/include:callbacks_b")
#pragma comment(linker,"/include:callbacks_c")
#pragma comment(linker,"/include:callbacks_end")
BOOL DllMain(HMODULE m,U32 reason,void*r){(void)m;(void)r;if(reason==1||reason==2){if(state.order!=123)++state.errors;state.order=state.order*10+4;}return 1;}
__declspec(dllexport) void QueryTLSState(struct TLS_OBSERVATION*out){
 out->cookie=state.cookie;out->order=state.order;out->errors=state.errors;
 out->pad_first=state.pad[0];out->pad_last=state.pad[sizeof(state.pad)-1];out->address=(SIZE)&state;
}
__declspec(dllexport) void SetTLSCookie(U32 value){state.cookie=value;}
