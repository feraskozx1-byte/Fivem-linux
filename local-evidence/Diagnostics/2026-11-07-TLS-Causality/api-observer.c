#include "winmini.h"
#include "debug-types.h"
void *memset(void*d,int v,SIZE n){volatile U8*p=d;for(SIZE i=0;i<n;i++)p[i]=(U8)v;return d;}
void *memcpy(void*d,const void*s,SIZE n){volatile U8*p=d;const volatile U8*q=s;for(SIZE i=0;i<n;i++)p[i]=q[i];return d;}
IMP BOOL CreateProcessW(const U16*,U16*,void*,void*,BOOL,U32,void*,const U16*,struct SI*,struct PI*);
IMP BOOL WaitForDebugEvent(struct DE*,U32);
IMP BOOL ContinueDebugEvent(U32,U32,U32);
IMP BOOL ReadProcessMemory(HANDLE,const void*,void*,SIZE,SIZE*);
IMP HANDLE OpenThread(U32,BOOL,U32);
IMP BOOL GetThreadContext(HANDLE,struct CTX*);
IMP BOOL SetThreadContext(HANDLE,const struct CTX*);
IMP U32 GetFinalPathNameByHandleW(HANDLE,U16*,U32,U32);
IMP U64 GetTickCount64(void);
IMP BOOL TerminateProcess(HANDLE,U32);
struct THREAD {U32 id;SIZE ret,module;};
struct MODULE {SIZE base,size;char name[80];};
static struct THREAD threads[128];static U32 thread_count;
static struct MODULE modules[256];static U32 module_count;
static HANDLE process,output,disk;static SIZE api,adhesive;
static U32 api_calls,api_returns,failed_calls,errors,captured,lookups,producers,producer_mismatches;
static U32 expected_index;static BOOL pending_index;
static void put(const char*s){U32 n=0,w;while(s[n])n++;WriteFile(output,s,n,&w,NULL);WriteFile(disk,s,n,&w,NULL);}
static void hex(U64 v){char b[19];const char*d="0123456789abcdef";b[0]='0';b[1]='x';for(U32 i=0;i<16;i++)b[i+2]=d[(v>>(60-4*i))&15];b[18]=0;put(b);}
static void field(const char*n,U64 v){put(n);hex(v);put("\r\n");}
static BOOL read_at(SIZE at,void*b,SIZE n){SIZE got=0;return ReadProcessMemory(process,(void*)at,b,n,&got)&&got==n;}
static struct THREAD*get_thread(U32 id){for(U32 i=0;i<thread_count;i++)if(threads[i].id==id)return &threads[i];if(thread_count==128){errors++;return NULL;}threads[thread_count].id=id;return &threads[thread_count++];}
static const char*owner(SIZE address){for(U32 i=0;i<module_count;i++)if(address>=modules[i].base&&address<modules[i].base+modules[i].size)return modules[i].name;return "unknown";}
static BOOL equal(const char*a,const char*b){while(*a&&*a==*b){a++;b++;}return *a==*b;}
static void add_module(SIZE base,HANDLE file,const char*fallback){
 if(module_count==256){errors++;return;}struct MODULE*m=&modules[module_count++];m->base=base;
 U8 h[512];if(read_at(base,h,sizeof(h))){U32 pe=*(U32*)(h+60);if(pe<sizeof(h)-84)m->size=*(U32*)(h+pe+80);}
 U16 path[1024];U32 n=file?GetFinalPathNameByHandleW(file,path,1024,0):0;
 if(n&&n<1024){U32 start=n;while(start&&path[start-1]!='\\'&&path[start-1]!='/')start--;for(U32 i=0;i<79&&start+i<n;i++){U16 c=path[start+i];if(c>='A'&&c<='Z')c+=32;m->name[i]=c<128?(char)c:'?';}}
 else{U32 i=0;while(fallback[i]&&i<79){m->name[i]=fallback[i];i++;}}
}
static void remove_module(SIZE base){
 for(U32 i=0;i<module_count;i++)if(modules[i].base==base){put("UNLOAD module=");put(modules[i].name);put(" base=");hex(base);put("\r\n");modules[i]=modules[--module_count];break;}
}
static SIZE export_address(SIZE base,const char*name){
 U8 h[512],ed[40];if(!read_at(base,h,sizeof(h)))return 0;U32 pe=*(U32*)(h+60);if(pe>sizeof(h)-144)return 0;
 U32 er=*(U32*)(h+pe+136);if(!read_at(base+er,ed,40))return 0;
 U32 nf=*(U32*)(ed+20),nn=*(U32*)(ed+24),af=*(U32*)(ed+28),an=*(U32*)(ed+32),ao=*(U32*)(ed+36);if(nn>10000)return 0;
 for(U32 i=0;i<nn;i++){U32 nr;char s[64]={0};if(!read_at(base+an+4*i,&nr,4)||!read_at(base+nr,s,63))return 0;if(equal(s,name)){U16 ord;U32 fn;if(!read_at(base+ao+2*i,&ord,2)||ord>=nf||!read_at(base+af+4*ord,&fn,4))return 0;return base+fn;}}
 return 0;
}
static NOINLINE BOOL configure(struct THREAD*t){
 HANDLE h=OpenThread(0x58,0,t->id);if(!h)return 0;struct CTX c={0};c.flags=0x100010;
 BOOL ok=GetThreadContext(h,&c);
 if(ok){SIZE own[4]={api,t->ret,adhesive?adhesive+0xda4ee8:0,adhesive?adhesive+0xd9fdd5:0};for(U32 i=0;i<4;i++)if((c.debug[5]&(3ULL<<(i*2)))&&(c.debug[i]!=own[i]||((c.debug[5]>>(16+i*4))&15))){ok=0;put("REFUSE_UNKNOWN_DEBUG_REGISTER\r\n");break;}}
 if(ok){c.debug[0]=api;c.debug[1]=t->ret;c.debug[2]=adhesive?adhesive+0xda4ee8:0;c.debug[3]=adhesive?adhesive+0xd9fdd5:0;c.debug[4]=0;c.debug[5]=(api?1:0)|(t->ret?4:0)|(adhesive?0x50:0);ok=SetThreadContext(h,&c);}
 CloseHandle(h);return ok;
}
static void configure_all(void){for(U32 i=0;i<thread_count;i++)if(!configure(&threads[i])){errors++;put("CONFIGURE_FAILED\r\n");}}
static NOINLINE BOOL debug_event(struct DE*ev){
 struct THREAD*t=get_thread(ev->tid);if(!t)return 0;HANDLE h=OpenThread(0x58,0,t->id);if(!h)return 0;struct CTX c={0};c.flags=0x100013;
 if(!GetThreadContext(h,&c)){CloseHandle(h);errors++;return 0;}
 if(api&&(c.debug[0]!=api||!(c.debug[5]&1))){errors++;put("API_MONITOR_CONTINUITY_ERROR\r\n");}
 U32 which=c.rip==api&&api?1:(c.rip==t->ret&&t->ret?2:(adhesive&&c.rip==adhesive+0xda4ee8?4:(adhesive&&c.rip==adhesive+0xd9fdd5?8:0)));
 if(!which||!(c.debug[4]&which)){CloseHandle(h);return 0;}
 if(which==1){
  api_calls++;SIZE ret=0;if(t->ret){errors++;put("NESTED_API_CALL\r\n");}if(!read_at(c.rsp,&ret,8)){errors++;ret=0;}
  t->ret=ret;t->module=c.rcx;put("NT_CALL tid=");hex(t->id);put(" module=");put(owner(c.rcx));put(" module_base=");hex(c.rcx);put(" caller=");put(owner(ret));put(" after_adhesive_load=");hex(adhesive!=0);put("\r\n");
 }else if(which==2){
  api_returns++;if((U32)c.rax!=0)failed_calls++;put("NT_RETURN tid=");hex(t->id);put(" module=");put(owner(t->module));put(" status=");hex((U32)c.rax);put(" after_adhesive_load=");hex(adhesive!=0);put("\r\n");t->ret=0;
 }else if(which==4){
  producers++;U64 previous=0;if(!read_at(c.rsp+0x40,&previous,8)||previous!=c.r13)producer_mismatches++;
  expected_index=(U32)c.r13+1;pending_index=1;
  if(expected_index<4||expected_index>=1466){put("PRODUCER previous=");hex(previous);put(" r13=");hex(c.r13);put(" next=");hex(expected_index);put("\r\n");}
 }else{
  lookups++;if(pending_index&&(U32)c.rsi!=expected_index)producer_mismatches++;pending_index=0;
  if(c.rsi<4||c.rsi>=1466){put("CONSUMER index=");hex((U32)c.rsi);put("\r\n");}
 }
 c.debug[1]=t->ret;c.debug[4]=0;c.debug[5]=(api?1:0)|(t->ret?4:0)|(adhesive?0x50:0);c.eflags|=0x10000;c.flags=0x100011;
 BOOL ok=SetThreadContext(h,&c);CloseHandle(h);if(!ok)errors++;return ok;
}
void mainCRTStartup(void){
 output=GetStdHandle((U32)-11);disk=CreateFileW(L"C:\\tls-api-observer.txt",0x40000000,1,NULL,1,0x80,NULL);if(disk==(HANDLE)(SIZE)-1)ExitProcess(5);
#ifdef OWN_FIXTURE
 U16 app[]=L"Z:\\home\\feras\\Projects\\FiveM-PR4050-Test\\Diagnostics\\2026-11-07-TLS-Causality\\private\\reference-2022\\bin\\tls-test.exe";
 U16 cmd[]=L"\"Z:\\home\\feras\\Projects\\FiveM-PR4050-Test\\Diagnostics\\2026-11-07-TLS-Causality\\private\\reference-2022\\bin\\tls-test.exe\"";
#else
 U16 app[]=L"Z:\\home\\feras\\Projects\\FiveM-PR4050-Test\\Diagnostics\\2026-11-05-Adhesive-Phase2\\private\\fullhost\\FiveM.exe";
 U16 cmd[]=L"\"Z:\\home\\feras\\Projects\\FiveM-PR4050-Test\\Diagnostics\\2026-11-05-Adhesive-Phase2\\private\\fullhost\\FiveM.exe\"";
#endif
 struct SI si={0};struct PI pi={0};si.cb=sizeof(si);put("TLS_CAUSAL_OBSERVER; visible debugger; no memory/code/API-return writes\r\n");
 if(!CreateProcessW(app,cmd,NULL,NULL,0,2,NULL,NULL,&si,&pi)){field("CREATE_ERROR=",GetLastError());ExitProcess(2);}process=pi.process;
 U64 end=GetTickCount64()+45000,capture_time=0;BOOL startup_break=0;U32 child_exit=0xffffffffu;
 while(GetTickCount64()<end){struct DE ev={0};if(!WaitForDebugEvent(&ev,200)){if(capture_time&&GetTickCount64()-capture_time>700)break;continue;}U32 disposition=0x10002;
  if(ev.code==3){get_thread(ev.tid);add_module((SIZE)ev.u.process.base,ev.u.process.file,"main.exe");if(ev.u.process.file)CloseHandle(ev.u.process.file);}
  else if(ev.code==2){struct THREAD*t=get_thread(ev.tid);if(t&&api&&!configure(t))errors++;}
  else if(ev.code==6){
   add_module((SIZE)ev.u.dll.base,ev.u.dll.file,"unknown.dll");const char*name=modules[module_count-1].name;
   if(equal(name,"ntdll.dll")){api=export_address((SIZE)ev.u.dll.base,"LdrDisableThreadCalloutsForDll");field("MONITORED_NT_API=",api);if(!api)errors++;else{U16 branch=0;if(!read_at(api+0x63,&branch,2))errors++;field("NTDLL_STATIC_TLS_BRANCH=",branch);}configure_all();}
   if(equal(name,"adhesive.dll")){adhesive=(SIZE)ev.u.dll.base;field("ADHESIVE_BASE=",adhesive);configure_all();}
   if(ev.u.dll.file)CloseHandle(ev.u.dll.file);
  }else if(ev.code==7){remove_module(*(SIZE*)ev.u.bytes);}
  else if(ev.code==4){for(U32 i=0;i<thread_count;i++)if(threads[i].id==ev.tid){threads[i]=threads[--thread_count];break;}}
  else if(ev.code==1){
   struct ER*x=&ev.u.exception.record;disposition=0x80010001u;
   if(x->code==0x80000004u&&debug_event(&ev))disposition=0x10002;
   else if(x->code==0x80000003u&&!startup_break){startup_break=1;disposition=0x10002;}
   else{field("EXCEPTION=",x->code);if(adhesive&&(SIZE)x->address>=adhesive&&(SIZE)x->address<adhesive+0x340d000){field("ADHESIVE_EXCEPTION_RVA=",(SIZE)x->address-adhesive);if(x->code==0xc0000005u){field("READ_TARGET=",x->parameters[1]);captured=1;capture_time=GetTickCount64();}}}
  }else if(ev.code==5){child_exit=*(U32*)ev.u.bytes;ContinueDebugEvent(ev.pid,ev.tid,disposition);break;}
  if(!ContinueDebugEvent(ev.pid,ev.tid,disposition)){errors++;break;}
  if(capture_time&&GetTickCount64()-capture_time>700)break;
 }
 TerminateProcess(process,0);CloseHandle(pi.thread);CloseHandle(process);
 field("API_CALLS=",api_calls);field("API_RETURNS=",api_returns);field("NONZERO_API_RETURNS=",failed_calls);field("LOOKUPS=",lookups);field("PRODUCERS=",producers);field("PRODUCER_MISMATCHES=",producer_mismatches);field("OBSERVER_ERRORS=",errors);field("CHILD_EXIT=",child_exit);field("CAPTURED_AV=",captured);
 FlushFileBuffers(disk);CloseHandle(disk);ExitProcess(errors?10:0);
}
