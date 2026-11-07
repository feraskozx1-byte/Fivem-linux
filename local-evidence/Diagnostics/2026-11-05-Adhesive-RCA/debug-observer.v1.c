#include "../2026-11-05-Compatibility-Fix/winmini.h"
/* Compiler support for aggregate initialization; no external CRT dependency. */
void *memcpy(void *dst,const void *src,SIZE n){volatile U8 *d=dst;const volatile U8 *s=src;for(SIZE i=0;i<n;++i)d[i]=s[i];return dst;}
void *memset(void *dst,int value,SIZE n){volatile U8 *d=dst;for(SIZE i=0;i<n;++i)d[i]=(U8)value;return dst;}
/* Read-only debugger for our own child. No breakpoints inserted, memory writes,
   API hooks, context changes, Wine masking or security entry-point calls. */
struct ER {U32 code,flags;void *nested,*address;U32 count;SIZE parameters[15];};
struct EI {struct ER record;U32 first;};
struct CPI {HANDLE file,process,thread;void *base;U32 debug_offset,debug_size;void *tls,*start,*image;U16 unicode;};
struct LDI {HANDLE file;void *base;U32 debug_offset,debug_size;void *image;U16 unicode;};
struct DE {U32 code,pid,tid;union {struct EI exception;struct CPI process;struct LDI dll;U8 bytes[160];} u;};
struct SI {U32 cb;U16 *reserved,*desktop,*title;U32 x,y,xsize,ysize,xcount,ycount,fill,flags;U16 show,reserved_count;U8 *reserved_data;HANDLE input,output,error;};
struct PI {HANDLE process,thread;U32 pid,tid;};
struct __declspec(align(16)) CTX {U64 home[6];U32 flags,mxcsr;U16 cs,ds,es,fs,gs,ss;U32 eflags;U64 debug[6];U64 rax,rcx,rdx,rbx,rsp,rbp,rsi,rdi,r8,r9,r10,r11,r12,r13,r14,r15,rip;U8 tail[976];};
_Static_assert(sizeof(struct ER)==152,"EXCEPTION_RECORD");
_Static_assert(sizeof(struct DE)==176,"DEBUG_EVENT");
_Static_assert(sizeof(struct SI)==104,"STARTUPINFO");
_Static_assert(sizeof(struct CTX)==1232,"CONTEXT");
IMP BOOL CreateProcessW(const U16*,U16*,void*,void*,BOOL,U32,void*,const U16*,struct SI*,struct PI*);
IMP BOOL WaitForDebugEvent(struct DE*,U32);
IMP BOOL ContinueDebugEvent(U32,U32,U32);
IMP BOOL DebugSetProcessKillOnExit(BOOL);
IMP BOOL ReadProcessMemory(HANDLE,const void*,void*,SIZE,SIZE*);
IMP SIZE VirtualQueryEx(HANDLE,const void*,struct MBI*,SIZE);
IMP HANDLE OpenThread(U32,BOOL,U32);
IMP BOOL GetThreadContext(HANDLE,struct CTX*);
IMP U32 GetFinalPathNameByHandleW(HANDLE,U16*,U32,U32);
IMP U64 GetTickCount64(void);
IMP BOOL TerminateProcess(HANDLE,U32);
static HANDLE output,disk;static SIZE adhesive_base;static U32 captured;
static void put(const char*s){U32 n=0,w;while(s[n])++n;WriteFile(output,s,n,&w,NULL);if(disk)WriteFile(disk,s,n,&w,NULL);}
static void hex(U64 v){const char d[]="0123456789abcdef";char b[19];b[0]='0';b[1]='x';for(U32 i=0;i<16;++i)b[i+2]=d[(v>>(60-4*i))&15];b[18]=0;put(b);}
static void field(const char*n,U64 v){put(n);hex(v);put("\r\n");}
static void wide(const U16*s,U32 n){char b[2];b[1]=0;for(U32 i=0;i<n;++i){b[0]=s[i]<128?(char)s[i]:'?';put(b);}}
static BOOL suffix(const U16*s,U32 n,const U16*w){U32 m=0;while(w[m])++m;if(n<m)return 0;for(U32 i=0;i<m;++i){U16 c=s[n-m+i];if(c>='A'&&c<='Z')c+=32;if(c!=w[i])return 0;}return 1;}
static void region(HANDLE process,const char*label,SIZE at){struct MBI m={0};SIZE n=VirtualQueryEx(process,(void*)at,&m,sizeof(m));put(label);put(" at=");hex(at);put(" returned=");hex(n);put(" base=");hex((SIZE)m.base);put(" allocation=");hex((SIZE)m.allocation);put(" region_size=");hex(m.region_size);put(" state=");hex(m.state);put(" protect=");hex(m.protect);put(" type=");hex(m.type);put("\r\n");}
static void sample(HANDLE process,const U16*path,const char*label,SIZE at,SIZE size){U8 bytes[2048];SIZE n=0;if(size>sizeof(bytes))size=sizeof(bytes);BOOL ok=ReadProcessMemory(process,(void*)at,bytes,size,&n);put(label);put(" read_ok=");hex(ok);put(" bytes=");hex(n);put("\r\n");if(n){HANDLE f=CreateFileW(path,0x40000000,1,NULL,1,0x80,NULL);if(f!=(HANDLE)(SIZE)-1){U32 wrote=0;WriteFile(f,bytes,(U32)n,&wrote,NULL);FlushFileBuffers(f);CloseHandle(f);}}}
static void snapshot(HANDLE process,struct DE *ev){
 HANDLE thread=OpenThread(0x48,0,ev->tid);struct CTX c={0};c.flags=0x100003;
 field("context_thread_handle=",(SIZE)thread);if(!thread)return;
 BOOL ok=GetThreadContext(thread,&c);field("GetThreadContext=",ok);CloseHandle(thread);if(!ok)return;
 field("rip=",c.rip);field("rax=",c.rax);field("rcx=",c.rcx);field("rdx=",c.rdx);field("rbx=",c.rbx);field("rsp=",c.rsp);field("rbp=",c.rbp);field("rsi=",c.rsi);field("rdi=",c.rdi);field("r8=",c.r8);field("r9=",c.r9);field("r10=",c.r10);field("r11=",c.r11);field("r12=",c.r12);field("r13=",c.r13);field("r14=",c.r14);field("r15=",c.r15);
 region(process,"r9-region",c.r9);region(process,"read-target-region",ev->u.exception.record.parameters[1]);
 sample(process,L"C:\\rca-r9-sample.bin","r9_sample",c.r9,256);
 sample(process,L"C:\\rca-stack-sample.bin","stack_sample",c.rsp,2048);
 captured=1;put("SNAPSHOT_CAPTURED=1\r\n");FlushFileBuffers(disk);
}
void mainCRTStartup(void){
 output=GetStdHandle((U32)-11);disk=CreateFileW(L"C:\\rca-debug-result.txt",0x40000000,1,NULL,1,0x80,NULL);if(disk==(HANDLE)(SIZE)-1)ExitProcess(5);
 U16 app[]=L"S:\\Projects\\FiveM-PR4050-Test\\Diagnostics\\2026-11-05-Adhesive-Phase2\\private\\fullhost\\FiveM.exe";
 U16 command[]=L"\"S:\\Projects\\FiveM-PR4050-Test\\Diagnostics\\2026-11-05-Adhesive-Phase2\\private\\fullhost\\FiveM.exe\"";
 struct SI startup={0};struct PI pi={0};startup.cb=sizeof(startup);
 put("DEBUG_OBSERVER_V1; debugger visible; exceptions NOT_HANDLED; no context or memory writes\r\n");
 BOOL ok=CreateProcessW(app,command,NULL,NULL,0,2,NULL,NULL,&startup,&pi);field("CreateProcess=",ok);if(!ok){field("error=",GetLastError());ExitProcess(2);}
 field("child_pid=",pi.pid);field("child_tid=",pi.tid);DebugSetProcessKillOnExit(1);
 U64 deadline=GetTickCount64()+40000;U32 initial_breakpoint_handled=0;U64 captured_at=0;
 while(GetTickCount64()<deadline){
  struct DE ev={0};if(!WaitForDebugEvent(&ev,250)){if(captured_at&&GetTickCount64()-captured_at>1000)break;continue;}
  U32 disposition=0x10002;
  if(ev.code==6){
   if(ev.u.dll.file){U16 path[1024];U32 n=GetFinalPathNameByHandleW(ev.u.dll.file,path,1024,0);if(n&&n<1024&&suffix(path,n,L"adhesive.dll")){adhesive_base=(SIZE)ev.u.dll.base;field("adhesive_base=",adhesive_base);put("adhesive_path=");wide(path,n);put("\r\n");}CloseHandle(ev.u.dll.file);}
  }else if(ev.code==3){if(ev.u.process.file)CloseHandle(ev.u.process.file);}
  else if(ev.code==2){if(ev.u.process.file)CloseHandle(ev.u.process.file);}
  else if(ev.code==1){
   disposition=0x80010001u;struct ER *r=&ev.u.exception.record;
   put("EXCEPTION code=");hex(r->code);put(" first_chance=");hex(ev.u.exception.first);put(" address=");hex((SIZE)r->address);put("\r\n");
   if(!initial_breakpoint_handled&&r->code==0x80000003u){initial_breakpoint_handled=1;disposition=0x10002;put("INITIAL_DEBUGGER_BREAKPOINT_HANDLED=1\r\n");}
   if(adhesive_base&&(SIZE)r->address>=adhesive_base&&(SIZE)r->address<adhesive_base+0x340d000&&r->code==0xc0000005u&&ev.u.exception.first&&!captured){
    field("fault_rva=",(SIZE)r->address-adhesive_base);field("access_kind=",r->parameters[0]);field("read_target=",r->parameters[1]);snapshot(pi.process,&ev);captured_at=GetTickCount64();
   }
  }else if(ev.code==5){field("CHILD_EXIT=",*(U32*)ev.u.bytes);ContinueDebugEvent(ev.pid,ev.tid,disposition);break;}
  ContinueDebugEvent(ev.pid,ev.tid,disposition);
  if(captured_at&&GetTickCount64()-captured_at>1000)break;
 }
 TerminateProcess(pi.process,0);CloseHandle(pi.thread);CloseHandle(pi.process);put(captured?"RESULT=SNAPSHOT\r\n":"RESULT=NO_MATCHING_FAULT\r\n");FlushFileBuffers(disk);CloseHandle(disk);ExitProcess(captured?0:10);
}
