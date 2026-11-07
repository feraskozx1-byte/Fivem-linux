#include "tls-common.h"
static HANDLE console,disk,gate,ready;
static QueryTLS query;static SetTLS set;
typedef LONG (*LdrDisable)(HMODULE);
typedef void (*QueryControl)(U32*);
static U32 checks,failures;
static struct TLS_OBSERVATION existing_observation,new_observation;
static void put(const char*s){U32 n=0,w;while(s[n])++n;WriteFile(console,s,n,&w,NULL);if(disk)WriteFile(disk,s,n,&w,NULL);}
static void hex(U64 v){char b[19];const char*d="0123456789abcdef";b[0]='0';b[1]='x';for(U32 i=0;i<16;++i)b[2+i]=d[(v>>(60-i*4))&15];b[18]=0;put(b);}
static void field(const char*n,U64 v){put(n);hex(v);put("\r\n");}
static void check(const char*n,BOOL ok){++checks;if(!ok)++failures;put(ok?"PASS ":"FAIL ");put(n);put("\r\n");}
static void observe(const char*name,const struct TLS_OBSERVATION*x){put("OBS ");put(name);put(" cookie=");hex(x->cookie);put(" order=");hex(x->order);put(" errors=");hex(x->errors);put(" pad_first=");hex(x->pad_first);put(" pad_last=");hex(x->pad_last);put(" aligned16=");hex((x->address&15)==0);put("\r\n");}
static void path(U16*p,const U16*name){U32 n=GetModuleFileNameW(NULL,p,1024);while(n&&p[n-1]!='\\'&&p[n-1]!='/')--n;for(U32 j=0;;++j){p[n++]=name[j];if(!name[j])break;}}
static U32 existing_worker(void*unused){(void)unused;SetEvent(ready);if(WaitForSingleObject(gate,10000)!=0)return 1;query(&existing_observation);set(0x22222222);return 0;}
static U32 new_worker(void*unused){(void)unused;query(&new_observation);set(0x33333333);return 0;}
void mainCRTStartup(void){
 U16 filename[1024];console=GetStdHandle((U32)-11);path(filename,L"tls-result.txt");disk=CreateFileW(filename,0x40000000,1,NULL,1,0x80,NULL);if(disk==(HANDLE)(SIZE)-1)ExitProcess(5);
 put("TLS_CAUSALITY_V2; own static-TLS and no-TLS DLLs; no FiveM libraries\r\n");
 gate=CreateEventW(NULL,1,0,NULL);check("existing-thread gate",gate!=NULL);
 ready=CreateEventW(NULL,1,0,NULL);check("existing-thread readiness event",ready!=NULL);
 HANDLE older=CreateThread(NULL,0,existing_worker,NULL,0,NULL);check("thread exists before DLL load",older!=NULL);
 check("existing thread running before DLL load",WaitForSingleObject(ready,10000)==0);
 path(filename,L"tls-fixture.dll");HMODULE dll=LoadLibraryW(filename);check("dynamic load",dll!=NULL);
 if(!dll){field("LoadLibrary-error=",GetLastError());ExitProcess(2);}
 query=(QueryTLS)GetProcAddress(dll,"QueryTLSState");set=(SetTLS)GetProcAddress(dll,"SetTLSCookie");check("owned fixture exports",query&&set);if(!query||!set)ExitProcess(2);
 struct TLS_OBSERVATION main_state;query(&main_state);observe("loading-thread",&main_state);
 check("TLS template available before first callback",main_state.cookie==TLS_COOKIE&&main_state.errors==0);
 check("three callbacks precede DllMain in declared order",main_state.order==1234);
 check("TLS zero data and callback writes preserved",main_state.pad_first==0xa5&&main_state.pad_last==0x5a);
 check("TLS aligned16",(main_state.address&15)==0);
 LdrDisable ldr=(LdrDisable)GetProcAddress(GetModuleHandleW(L"ntdll.dll"),"LdrDisableThreadCalloutsForDll");check("NT loader call available",ldr!=NULL);
 if(ldr)field("LdrDisableThreadCalloutsForDll-static-status=",(U32)ldr(dll));
 BOOL disabled=DisableThreadLibraryCalls(dll);field("DisableThreadLibraryCalls-static-return=",disabled);field("DisableThreadLibraryCalls-static-error=",disabled?0:GetLastError());
 /* Observe the BOOL rather than asserting the documented FALSE: modern native
    Windows may return TRUE while retaining static-TLS thread notifications. */
 path(filename,L"tls-control.dll");HMODULE control=LoadLibraryW(filename);check("no-TLS control loaded",control!=NULL);
 QueryControl control_query=control?(QueryControl)GetProcAddress(control,"QueryControlCounts"):NULL;check("control query available",control_query!=NULL);
 U32 control_counts[2]={0,0};if(control_query)control_query(control_counts);check("control process attach called",control_counts[0]==1);
 BOOL control_disabled=control?DisableThreadLibraryCalls(control):0;field("DisableThreadLibraryCalls-control-return=",control_disabled);check("no-TLS disabling succeeds",control_disabled);
 set(0x11111111);SetEvent(gate);check("pre-existing thread completes",WaitForSingleObject(older,10000)==0);observe("pre-existing-thread",&existing_observation);
 check("pre-existing thread gets independent initialized template",existing_observation.cookie==TLS_COOKIE&&existing_observation.errors==0);
 check("no retroactive thread-attach callbacks",existing_observation.order==0&&existing_observation.pad_first==0&&existing_observation.pad_last==0);
 check("pre-existing thread TLS aligned16",(existing_observation.address&15)==0);
 HANDLE newer=CreateThread(NULL,0,new_worker,NULL,0,NULL);check("new thread created",newer!=NULL);check("new thread completes",WaitForSingleObject(newer,10000)==0);observe("new-thread",&new_observation);
 check("new thread template/callback order",new_observation.cookie==TLS_COOKIE&&new_observation.errors==0&&new_observation.order==1234);
 check("new thread initialized padding",new_observation.pad_first==0xa5&&new_observation.pad_last==0x5a);
 check("new thread TLS aligned16",(new_observation.address&15)==0);
 if(control_query)control_query(control_counts);field("control-thread-attach-count=",control_counts[1]);check("no-TLS control thread calls suppressed",control_counts[1]==0);
 query(&main_state);check("worker writes do not leak into main TLS",main_state.cookie==0x11111111);
 CloseHandle(older);CloseHandle(newer);CloseHandle(gate);CloseHandle(ready);if(control)FreeLibrary(control);check("unload after threads finish",FreeLibrary(dll));
 path(filename,L"tls-fixture.dll");dll=LoadLibraryW(filename);check("reload",dll!=NULL);if(dll){query=(QueryTLS)GetProcAddress(dll,"QueryTLSState");if(query){query(&main_state);observe("reload-thread",&main_state);check("reload has fresh TLS data and callback order",main_state.cookie==TLS_COOKIE&&main_state.order==1234&&main_state.errors==0);}FreeLibrary(dll);}
 field("checks=",checks);field("failures=",failures);put(failures?"RESULT=FAIL\r\n":"RESULT=PASS\r\n");FlushFileBuffers(disk);CloseHandle(disk);ExitProcess(failures?1:0);
}
