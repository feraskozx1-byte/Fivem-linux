#include "winmini.h"
/* Own fixture pages only: no FiveM DLL, hooks, identity checks or connections. */
static HANDLE console,disk;
static U32 failures,checks;
static void put(const char *p){U32 n=0,w;while(p[n])++n;WriteFile(console,p,n,&w,NULL);if(disk)WriteFile(disk,p,n,&w,NULL);}
static void hex(U64 x){char b[19];const char d[]="0123456789abcdef";b[0]='0';b[1]='x';for(U32 i=0;i<16;++i)b[i+2]=d[(x>>(60-4*i))&15];b[18]=0;put(b);}
static void val(const char *s,U64 x){put(s);hex(x);put("\r\n");}
static void check(const char *name,BOOL ok){++checks;put(ok?"PASS ":"FAIL ");put(name);put("\r\n");if(!ok)++failures;}
static LONG filter(U32 code,U32 expected){return code==expected?1:0;}
static NOINLINE BOOL read_fault(volatile U8 *p){BOOL caught=0;__try{volatile U8 value=*p;(void)value;}__except(filter(__exception_code(),0xc0000005u)){caught=1;}return caught;}
static NOINLINE BOOL write_fault(volatile U8 *p){BOOL caught=0;__try{*p=0x72;}__except(filter(__exception_code(),0xc0000005u)){caught=1;}return caught;}
static void memory_tests(void){
 struct MBI m;U32 old=0;BOOL ok;U8 *p=VirtualAlloc(NULL,8192,0x2000,4);
 check("vm.reserve",p!=NULL);if(!p)return;
 check("vm.query-reserved",VirtualQuery(p,&m,sizeof(m))==sizeof(m)&&m.state==0x2000);
 check("vm.commit-first-page",VirtualAlloc(p,4096,0x1000,4)==p);
 check("vm.query-committed",VirtualQuery(p,&m,sizeof(m))==sizeof(m)&&m.state==0x1000&&m.protect==4);
 check("vm.query-second-reserved",VirtualQuery(p+4096,&m,sizeof(m))==sizeof(m)&&m.state==0x2000);
 p[0]=0x65;p[4095]=0x43;
 check("vm.reserved-read-raises-AV",read_fault(p+4096));
 ok=VirtualProtect(p,8192,2,&old);val("vm.cross-range-last-error=",ok?0:GetLastError());
 check("vm.protect-mixed-range-fails",!ok);
 check("vm.failed-protect-preserves-first-page",VirtualQuery(p,&m,sizeof(m))==sizeof(m)&&m.protect==4);
 check("vm.protect-readonly",VirtualProtect(p,4096,2,&old)&&old==4);
 check("vm.readonly-keeps-data",p[0]==0x65&&p[4095]==0x43);
 check("vm.readonly-write-raises-AV",write_fault(p));
 check("vm.restore-rw",VirtualProtect(p,4096,4,&old)&&old==2);
 check("vm.decommit",VirtualFree(p,4096,0x4000));
 check("vm.decommit-reserved",VirtualQuery(p,&m,sizeof(m))==sizeof(m)&&m.state==0x2000);
 check("vm.recommit-zero",VirtualAlloc(p,4096,0x1000,4)==p&&p[0]==0&&p[4095]==0);
 check("vm.release",VirtualFree(p,0,0x8000));
 check("vm.released-free",VirtualQuery(p,&m,sizeof(m))==sizeof(m)&&m.state==0x10000);
}
typedef LONG (*ReadFn)(HANDLE,HANDLE,void*,void*,struct IOSB*,void*,U32,I64*,U32*);
typedef LONG (*QueryFn)(HANDLE,struct IOSB*,void*,U32,U32);
#define FILE_BYTES (0x61000u-7u)
static U8 fixture[FILE_BYTES],readbuf[0x61020];
static U8 pattern(U32 i){return (U8)(i*131u+17u);}
static void io_case(ReadFn read,HANDLE file,const char *name,U32 offset,U32 requested,U32 expected,LONG status){
 struct IOSB io;I64 at=offset;for(U32 i=0;i<sizeof(readbuf);++i)readbuf[i]=0xa5;
 io.status=(LONG)0x55555555;io.information=(SIZE)-1;
 LONG actual=read(file,NULL,NULL,NULL,&io,readbuf,requested,&at,NULL);
 put("OBS ");put(name);put(" status=");hex((U32)actual);put(" information=");hex(io.information);put("\r\n");
 BOOL bytes=1;for(U32 i=0;i<expected;++i)if(readbuf[i]!=pattern(offset+i)){bytes=0;break;}
 BOOL tail=1;for(U32 i=expected;i<sizeof(readbuf);++i)if(readbuf[i]!=0xa5){tail=0;break;}
 check(name,actual==status&&io.information==expected&&bytes&&tail);
 /* IOSB.Status is asserted on successful synchronous completion only. */
 if(actual==0)check("io.success-iosb-status",io.status==0);
}
static void io_tests(void){
 HMODULE nt=GetModuleHandleW(L"ntdll.dll");ReadFn read=(ReadFn)GetProcAddress(nt,"NtReadFile");QueryFn query=(QueryFn)GetProcAddress(nt,"NtQueryInformationFile");
 check("io.exports",read&&query);if(!read||!query)return;
 HANDLE f=CreateFileW(L"C:\\compat-fix-fixture-20261105.bin",0xc0000000u,3,NULL,1,0x80,NULL);
 check("io.create-new-owned-fixture",f!=(HANDLE)(SIZE)-1);if(f==(HANDLE)(SIZE)-1)return;
 for(U32 i=0;i<FILE_BYTES;++i)fixture[i]=pattern(i);
 U32 wrote=0;check("io.write-fixture",WriteFile(f,fixture,FILE_BYTES,&wrote,NULL)&&wrote==FILE_BYTES);
 struct IOSB io;struct STANDARD info;LONG s=query(f,&io,&info,sizeof(info),5);
 val("io.standard-query-status=",(U32)s);val("io.standard-information=",io.information);val("io.end-of-file=",(U64)info.end);
 check("io.standard-size",s==0&&io.information==sizeof(info)&&info.end==FILE_BYTES&&!info.directory);
 io_case(read,f,"io.exact-read",0,FILE_BYTES,FILE_BYTES,0);
 io_case(read,f,"io.rounded-request-short-read",0,0x61000,FILE_BYTES,0);
 io_case(read,f,"io.tail-short-read",FILE_BYTES-3,16,3,0);
 io_case(read,f,"io.start-at-EOF",FILE_BYTES,16,0,(LONG)0xc0000011u);
 check("io.close",CloseHandle(f));check("io.delete-owned-fixture",DeleteFileW(L"C:\\compat-fix-fixture-20261105.bin"));
}
typedef void *(*MallocFn)(SIZE);typedef void *(*ReallocFn)(void*,SIZE);typedef SIZE (*MsizeFn)(void*);typedef void (*FreeFn)(void*);
typedef void (*VoidFn)(void);typedef int (*IntFn)(void);typedef void (*InitFn)(VoidFn*,VoidFn*);typedef int (*InitEFn)(IntFn*,IntFn*);
static volatile U32 sequence;
static void init_a(void){sequence=sequence*10+1;}static void init_b(void){sequence=sequence*10+2;}
static void init_throw(void){RaiseException(0xe0420001u,0,0,NULL);}
static int ini_zero(void){sequence=sequence*10+1;return 0;}static int ini_stop(void){sequence=sequence*10+2;return 42;}static int ini_after(void){sequence=999;return 0;}
static void crt_tests(void){
 HMODULE crt=LoadLibraryW(L"ucrtbase.dll");check("crt.load",crt!=NULL);if(!crt)return;
 MallocFn alloc=(MallocFn)GetProcAddress(crt,"malloc");ReallocFn resize=(ReallocFn)GetProcAddress(crt,"realloc");MsizeFn msize=(MsizeFn)GetProcAddress(crt,"_msize");FreeFn release=(FreeFn)GetProcAddress(crt,"free");
 InitFn init=(InitFn)GetProcAddress(crt,"_initterm");InitEFn inite=(InitEFn)GetProcAddress(crt,"_initterm_e");
 check("crt.exports",alloc&&resize&&msize&&release&&init&&inite);if(!alloc||!resize||!msize||!release||!init||!inite)return;
 U8 *p=alloc(0xd8000);check("crt.malloc-request",p!=NULL);if(p){
  val("crt.malloc-usable-size=",msize(p));check("crt.malloc-size-alignment",msize(p)>=0xd8000&&((SIZE)p&15)==0);
  for(U32 i=0;i<0xd8000;++i)p[i]=pattern(i);
  U8 *q=resize(p,0xd9000);check("crt.realloc",q!=NULL);
  if(q){BOOL equal=1;for(U32 i=0;i<0xd8000;++i)if(q[i]!=pattern(i)){equal=0;break;}check("crt.realloc-preserves-request",equal);check("crt.realloc-size",msize(q)>=0xd9000);release(q);}else release(p);
 }
 VoidFn table[]={init_a,NULL,init_b};sequence=0;init(table,table+3);check("crt.initterm-order-null",sequence==12);
 IntFn etable[]={ini_zero,NULL,ini_stop,ini_after};sequence=0;int rc=inite(etable,etable+4);check("crt.initterm-e-stops-nonzero",rc==42&&sequence==12);
 VoidFn throwing[]={init_a,init_throw,init_b};sequence=0;BOOL caught=0;
 __try{init(throwing,throwing+3);}__except(filter(__exception_code(),0xe0420001u)){caught=1;}
 check("crt.initterm-propagates-owned-exception",caught&&sequence==1);
 check("crt.release",FreeLibrary(crt));
}
static void fixture_path(U16 *path,const U16 *name){
 U32 n=GetModuleFileNameW(NULL,path,768);while(n&&path[n-1]!='\\'&&path[n-1]!='/')--n;U32 j=0;while(name[j])path[n++]=name[j++];path[n]=0;
}
static void dll_tests(void){
 U16 path[768];fixture_path(path,L"compat-fixture-ok.dll");HMODULE a=LoadLibraryW(path),b=LoadLibraryW(path);
 check("dll.normal-load-reference-count",a&&a==b);if(a&&b){
  U32 (*count)(void)=(U32(*)(void))GetProcAddress(a,"CompatAttachCount");check("dll.attach-once",count&&count()==1);
  check("dll.free-one-retains",FreeLibrary(a)&&GetModuleHandleW(path)==b);check("dll.free-last-unloads",FreeLibrary(b)&&!GetModuleHandleW(path));
 }
 fixture_path(path,L"compat-fixture-false.dll");a=LoadLibraryW(path);U32 err=a?0:GetLastError();val("dll.false-last-error=",err);check("dll.false-fails",!a);check("dll.false-error-init-failed",!a&&err==1114);
 fixture_path(path,L"compat-fixture-av.dll");a=LoadLibraryW(path);err=a?0:GetLastError();val("dll.owned-AV-last-error-observed=",err);check("dll.owned-AV-fails",!a);
 /* 998 is observation, not a claimed Windows-baseline assertion. */
}
void mainCRTStartup(void){
 console=GetStdHandle((U32)-11);disk=CreateFileW(L"C:\\compat-fix-result.txt",0x40000000,1,NULL,1,0x80,NULL);
 if(disk==(HANDLE)(SIZE)-1){disk=NULL;ExitProcess(5);}
 put("CONTRACT_TESTS_V1 x64; own fixtures only; no FiveM libraries\r\n");
 memory_tests();io_tests();crt_tests();dll_tests();val("checks=",checks);val("failures=",failures);put(failures?"RESULT=FAIL\r\n":"RESULT=PASS\r\n");FlushFileBuffers(disk);CloseHandle(disk);ExitProcess(failures?1:0);
}
