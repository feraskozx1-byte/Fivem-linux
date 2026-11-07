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
struct CALL {SIZE ret,out;U32 kind;char name[128],initiator[80];};
struct THREAD {U32 id,depth;SIZE armed[4];struct CALL calls[8];};
struct MODULE {SIZE base,size;char name[80];};
static struct THREAD threads[128];static U32 thread_count;
static struct MODULE modules[256];static U32 module_count;
static HANDLE process,disk;static SIZE ntbase,ntapi,winapi,adhesive,lookup,watch;
static U32 errors,entries,ntdll_calls,returns,failed_returns,lookups,watch_events,adh_watch_events,captured;
static U32 primary_tid;
static BOOL seen_first_lookup;
static void put(const char*s){U32 n=0,w;while(s[n])n++;WriteFile(disk,s,n,&w,NULL);}
static void hex(U64 v){char b[19];const char*d="0123456789abcdef";b[0]='0';b[1]='x';for(U32 i=0;i<16;i++)b[i+2]=d[(v>>(60-4*i))&15];b[18]=0;put(b);}
static void field(const char*n,U64 v){put(n);hex(v);put("\r\n");}
static BOOL read_at(SIZE at,void*b,SIZE n){SIZE got=0;return ReadProcessMemory(process,(void*)at,b,n,&got)&&got==n;}
static BOOL equal(const char*a,const char*b){while(*a&&*a==*b){a++;b++;}return *a==*b;}
static void copystr(char*d,const char*s,U32 cap){U32 i=0;while(i+1<cap&&s[i]){d[i]=s[i];i++;}d[i]=0;}
static const char*owner(SIZE address){for(U32 i=0;i<module_count;i++)if(address>=modules[i].base&&address<modules[i].base+modules[i].size)return modules[i].name;return "unknown";}
static struct THREAD*get_thread(U32 id){for(U32 i=0;i<thread_count;i++)if(threads[i].id==id)return &threads[i];if(thread_count==128){errors++;return NULL;}memset(&threads[thread_count],0,sizeof(threads[thread_count]));threads[thread_count].id=id;return &threads[thread_count++];}
static void add_module(SIZE base,HANDLE file,const char*fallback){
 if(module_count==256){errors++;return;}struct MODULE*m=&modules[module_count++];memset(m,0,sizeof(*m));m->base=base;
 U8 h[512];if(read_at(base,h,sizeof(h))){U32 pe=*(U32*)(h+60);if(pe<sizeof(h)-84)m->size=*(U32*)(h+pe+80);}
 U16 path[1024];U32 n=file?GetFinalPathNameByHandleW(file,path,1024,0):0;
 if(n&&n<1024){U32 start=n;while(start&&path[start-1]!='\\'&&path[start-1]!='/')start--;for(U32 i=0;i<79&&start+i<n;i++){U16 c=path[start+i];if(c>='A'&&c<='Z')c+=32;m->name[i]=c<128?(char)c:'?';}}
 else copystr(m->name,fallback,80);
}
static void remove_module(SIZE base){for(U32 i=0;i<module_count;i++)if(modules[i].base==base){modules[i]=modules[--module_count];break;}}
static SIZE export_address(SIZE base,const char*name){
 U8 h[512],ed[40];if(!read_at(base,h,sizeof(h)))return 0;U32 pe=*(U32*)(h+60);if(pe>sizeof(h)-144)return 0;
 U32 er=*(U32*)(h+pe+136);if(!read_at(base+er,ed,40))return 0;
 U32 nf=*(U32*)(ed+20),nn=*(U32*)(ed+24),af=*(U32*)(ed+28),an=*(U32*)(ed+32),ao=*(U32*)(ed+36);if(nn>10000)return 0;
 for(U32 i=0;i<nn;i++){U32 nr;char s[128]={0};if(!read_at(base+an+4*i,&nr,4)||!read_at(base+nr,s,127))return 0;if(equal(s,name)){U16 ord;U32 fn;if(!read_at(base+ao+2*i,&ord,2)||ord>=nf||!read_at(base+af+4*ord,&fn,4))return 0;return base+fn;}}
 return 0;
}
static BOOL set_debug(struct THREAD*t,struct CTX*c){
 for(U32 i=0;i<4;i++)if(t->armed[i]&&!(c->debug[5]&(3ULL<<(i*2)))){errors++;put("MONITOR_CONTINUITY_LOST\r\n");return 0;}
 for(U32 i=0;i<4;i++)if((c->debug[5]&(3ULL<<(i*2)))&&c->debug[i]!=t->armed[i]){errors++;put("REFUSE_UNKNOWN_DEBUG_REGISTER\r\n");return 0;}
 SIZE at[4]={ntapi,t->depth?t->calls[t->depth-1].ret:0,winapi,watch?watch:lookup};
 for(U32 i=0;i<4;i++){c->debug[i]=at[i];t->armed[i]=at[i];}
 c->debug[4]=0;c->debug[5]=(at[0]?1:0)|(at[1]?4:0)|(at[2]?16:0)|(at[3]?64:0)|(watch?(0xfULL<<28):0);
 return 1;
}
static NOINLINE BOOL configure(struct THREAD*t){
 if(adhesive){put("ARM_THREAD_BEGIN=");hex(t->id);put("\r\n");}
 HANDLE h=OpenThread(0x58,0,t->id);if(!h)return 0;struct CTX c={0};c.flags=0x100010;
 if(adhesive)put("ARM_OPEN_OK\r\n");
 BOOL ok=GetThreadContext(h,&c);if(adhesive)put("ARM_GET_CONTEXT_DONE\r\n");
 if(ok)ok=set_debug(t,&c)&&SetThreadContext(h,&c);if(adhesive)put("ARM_SET_CONTEXT_DONE\r\n");
 CloseHandle(h);return ok;
}
static void configure_event_thread(U32 tid){if(tid!=primary_tid)return;struct THREAD*t=get_thread(tid);if(!t||!configure(t)){errors++;put("CONFIGURE_FAILED\r\n");}}
static void name_at(SIZE at,char*out,U32 n){
 if(!at||n>=128){copystr(out,"<ordinal-or-long-name>",128);return;}
 for(U32 i=0;i<127;i++){U8 c;if((n&&i==n)||!read_at(at+i,&c,1)||!c){out[i]=0;return;}out[i]=c>=32&&c<127?(char)c:'?';}out[127]=0;
}
static NOINLINE BOOL on_debug(struct DE*ev){
 if(ev->tid!=primary_tid)return 0;
 struct THREAD*t=get_thread(ev->tid);if(!t)return 0;HANDLE h=OpenThread(0x58,0,t->id);if(!h)return 0;struct CTX c={0};c.flags=0x100013;
 if(!GetThreadContext(h,&c)){CloseHandle(h);errors++;return 0;}
 U32 which=(c.rip==ntapi&&ntapi&&(c.debug[4]&1))?1:
  (t->depth&&c.rip==t->calls[t->depth-1].ret&&(c.debug[4]&2))?2:
  (c.rip==winapi&&winapi&&(c.debug[4]&4))?4:
  ((c.debug[4]&8)&&((watch!=0)||(lookup&&c.rip==lookup)))?8:0;
 if(!which){CloseHandle(h);return 0;}
 if(which==1||which==4){
  entries++;if(!(entries%1024))field("PROGRESS_ALL_ENTRIES=",entries);
  if(c.rcx==ntbase){
   ntdll_calls++;if(t->depth==8){errors++;CloseHandle(h);return 0;}
   struct CALL*a=&t->calls[t->depth];memset(a,0,sizeof(*a));a->kind=which==1?1:2;
   if(!read_at(c.rsp,&a->ret,8))errors++;
   copystr(a->initiator,t->depth?t->calls[0].initiator:owner(a->ret),80);
   if(which==4){if(c.rdx>0xffff)name_at(c.rdx,a->name,0);else copystr(a->name,"<ordinal>",128);}
   else if(c.rdx){U8 ansi[16];if(read_at(c.rdx,ansi,16))name_at(*(SIZE*)(ansi+8),a->name,*(U16*)ansi);else errors++;a->out=c.r9;}
   else copystr(a->name,"<ordinal>",128);
   t->depth++;
   put("RESOLVE_CALL tid=");hex(ev->tid);put(a->kind==1?" api=NT":" api=Win32");put(" name=");put(a->name);put(" caller=");put(owner(a->ret));put(" initiator=");put(a->initiator);put(" after_first_lookup=");hex(seen_first_lookup);put("\r\n");
  }
 }else if(which==2){
  struct CALL*a=&t->calls[t->depth-1];returns++;BOOL fail=a->kind==1?(U32)c.rax!=0:c.rax==0;if(fail)failed_returns++;
  put("RESOLVE_RETURN tid=");hex(ev->tid);put(a->kind==1?" api=NT":" api=Win32");put(" name=");put(a->name);put(" value=");hex(a->kind==1?(U32)c.rax:(c.rax!=0));put(" initiator=");put(a->initiator);put(" after_first_lookup=");hex(seen_first_lookup);put("\r\n");t->depth--;
 }else if(watch){
  watch_events++;if(equal(owner(c.rip),"adhesive.dll"))adh_watch_events++;
  U32 n=0;if(!read_at(watch,&n,4))errors++;put("COUNT_ACCESS after_instruction_owner=");put(owner(c.rip));put(" rva=");hex(adhesive&&equal(owner(c.rip),"adhesive.dll")?c.rip-adhesive:c.rip);put(" count_now=");hex(n);put(" after_AV=");hex(captured);put("\r\n");
 }else{
  lookups++;seen_first_lookup=1;field("INITIALIZER_THREAD=",ev->tid);
#ifdef OWN_FIXTURE
  watch=c.rcx;field("CONTROL_COUNT_WATCH=",watch);
#else
  U64 slots[7]={0};U8 ed[40];if(!read_at(c.rsp,slots,sizeof(slots))||!read_at(slots[4]+slots[6],ed,40))errors++;
  else {watch=slots[4]+slots[6]+24;field("FIRST_INDEX=",(U32)c.rsi);field("BUFFER_BASE=",slots[4]);field("EXPORT_RVA=",slots[6]);field("NUMBER_OF_NAMES=",*(U32*)(ed+24));field("NUMBER_OF_FUNCTIONS=",*(U32*)(ed+20));field("ADDRESS_OF_NAMES=",*(U32*)(ed+32));field("ADDRESS_OF_ORDINALS=",*(U32*)(ed+36));field("COPIED_COUNT_WATCH=",watch);}
#endif
 }
 c.eflags|=0x10000;c.flags=0x100011;BOOL ok=set_debug(t,&c)&&SetThreadContext(h,&c);CloseHandle(h);if(!ok)errors++;
 return ok;
}
static void audit_fault(U32 tid){
 HANDLE h=OpenThread(0x58,0,tid);struct CTX c={0};c.flags=0x100013;
 if(!h||!GetThreadContext(h,&c)){errors++;if(h)CloseHandle(h);return;}
 field("FAULT_INDEX=",(U32)c.rsi);field("FAULT_NAME_RVA=",c.rax);field("FAULT_BUFFER=",c.r9);
 field("WATCH_AT_AV=",c.debug[3]);field("DR7_AT_AV=",c.debug[5]);
 U32 count=0;if(!watch||!read_at(watch,&count,4))errors++;field("COUNT_AT_AV=",count);
 CloseHandle(h);
}
void mainCRTStartup(void){
 disk=CreateFileW(L"C:\\export-resolver-observer.txt",0x40000000,1,NULL,1,0x80,NULL);if(disk==(HANDLE)(SIZE)-1)ExitProcess(5);
#ifdef OWN_FIXTURE
 U16 app[]=L"Z:\\home\\feras\\Projects\\FiveM-PR4050-Test\\Diagnostics\\2026-11-07-Export-Bounds\\resolver-fixture.exe";
#else
 U16 app[]=L"Z:\\home\\feras\\Projects\\FiveM-PR4050-Test\\Diagnostics\\2026-11-05-Adhesive-Phase2\\private\\fullhost\\FiveM.exe";
#endif
 struct SI si={0};struct PI pi={0};si.cb=sizeof(si);put("PUBLIC_RESOLVER_AND_COUNT_WATCH; visible debugger; no code/memory/return writes\r\n");
 if(!CreateProcessW(app,NULL,NULL,NULL,0,2,NULL,NULL,&si,&pi)){field("CREATE_ERROR=",GetLastError());ExitProcess(2);}process=pi.process;primary_tid=pi.tid;field("PRIMARY_THREAD_ONLY=",primary_tid);
 U64 end=GetTickCount64()+40000,capture_time=0;BOOL startup_break=0;U32 child_exit=0xffffffffu;
 while(GetTickCount64()<end){struct DE ev={0};if(!WaitForDebugEvent(&ev,200)){if(capture_time&&GetTickCount64()-capture_time>700)break;continue;}U32 disposition=0x10002;
  if(ev.code==3){get_thread(ev.tid);add_module((SIZE)ev.u.process.base,ev.u.process.file,"main.exe");if(ev.u.process.file)CloseHandle(ev.u.process.file);
#ifdef OWN_FIXTURE
   lookup=export_address((SIZE)ev.u.process.base,"BoundsMarker");if(!lookup)errors++;configure_event_thread(ev.tid);
#endif
  }else if(ev.code==2){get_thread(ev.tid);}
  else if(ev.code==6){
   add_module((SIZE)ev.u.dll.base,ev.u.dll.file,"unknown.dll");const char*name=modules[module_count-1].name;
   if(equal(name,"ntdll.dll")){ntbase=(SIZE)ev.u.dll.base;ntapi=export_address(ntbase,"LdrGetProcedureAddress");field("NT_RESOLVER=",ntapi);if(!ntapi)errors++;configure_event_thread(ev.tid);}
   if(equal(name,"kernel32.dll")){winapi=export_address((SIZE)ev.u.dll.base,"GetProcAddress");field("WIN32_RESOLVER=",winapi);if(!winapi)errors++;configure_event_thread(ev.tid);}
   if(equal(name,"adhesive.dll")){adhesive=(SIZE)ev.u.dll.base;
#ifndef OWN_FIXTURE
    lookup=adhesive+0xd9fdd5;
#endif
    field("ADHESIVE_BASE=",adhesive);configure_event_thread(ev.tid);put("ADHESIVE_LOAD_EVENT_ARM_DONE\r\n");}
   if(ev.u.dll.file)CloseHandle(ev.u.dll.file);
  }else if(ev.code==7){remove_module(*(SIZE*)ev.u.bytes);}
  else if(ev.code==4){for(U32 i=0;i<thread_count;i++)if(threads[i].id==ev.tid){threads[i]=threads[--thread_count];break;}}
  else if(ev.code==1){struct ER*x=&ev.u.exception.record;disposition=0x80010001u;
   if(x->code==0x80000004u&&on_debug(&ev))disposition=0x10002;
   else if(x->code==0x80000003u&&!startup_break){startup_break=1;disposition=0x10002;}
   else{field("EXCEPTION=",x->code);if(adhesive&&(SIZE)x->address>=adhesive&&(SIZE)x->address<adhesive+0x340d000&&x->code==0xc0000005u){audit_fault(ev.tid);configure_event_thread(ev.tid);field("FAULT_RVA=",(SIZE)x->address-adhesive);captured=1;capture_time=GetTickCount64();}}
  }else if(ev.code==5){child_exit=*(U32*)ev.u.bytes;ContinueDebugEvent(ev.pid,ev.tid,disposition);break;}
  if(adhesive&&ev.code==6)put("DLL_EVENT_CONTINUE_BEGIN\r\n");
  if(!ContinueDebugEvent(ev.pid,ev.tid,disposition)){errors++;break;}
  if(adhesive&&ev.code==6)put("DLL_EVENT_CONTINUE_DONE\r\n");
  if(capture_time&&GetTickCount64()-capture_time>700)break;
 }
 TerminateProcess(process,0);CloseHandle(pi.thread);CloseHandle(process);
 field("ALL_RESOLVER_ENTRIES=",entries);field("NTDLL_RESOLVE_CALLS=",ntdll_calls);field("NTDLL_RESOLVE_RETURNS=",returns);field("FAILED_NTDLL_RETURNS=",failed_returns);
 field("FIRST_LOOKUPS=",lookups);field("COUNT_ACCESSES=",watch_events);field("ADHESIVE_COUNT_ACCESSES=",adh_watch_events);field("OBSERVER_ERRORS=",errors);field("CHILD_EXIT=",child_exit);field("CAPTURED_AV=",captured);
 put("OBSERVER_COMPLETE\r\n");FlushFileBuffers(disk);CloseHandle(disk);ExitProcess(errors?10:0);
}
