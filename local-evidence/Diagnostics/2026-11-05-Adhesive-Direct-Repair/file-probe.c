#include "../2026-11-05-Compatibility-Fix/winmini.h"
/* Replays public file-I/O only for the TWO files named by actual Adhesive trace. */
struct US {U16 length,max;U16 *buffer;};
struct OA {U32 length;HANDLE root;struct US *name;U32 attributes;void *security,*qos;};
_Static_assert(sizeof(struct US)==16,"UNICODE_STRING");
_Static_assert(sizeof(struct OA)==48,"OBJECT_ATTRIBUTES");
typedef LONG (*OpenFn)(HANDLE*,U32,struct OA*,struct IOSB*,U32,U32);
typedef LONG (*QueryFn)(HANDLE,struct IOSB*,void*,U32,U32);
typedef LONG (*ReadFn)(HANDLE,HANDLE,void*,void*,struct IOSB*,void*,U32,I64*,U32*);
typedef LONG (*CloseFn)(HANDLE);
static HANDLE disk,console;static U32 failures;
static void put(const char *s){U32 n=0,w;while(s[n])++n;WriteFile(console,s,n,&w,NULL);WriteFile(disk,s,n,&w,NULL);}
static void hex(U64 x){const char d[]="0123456789abcdef";char b[19];b[0]='0';b[1]='x';for(U32 i=0;i<16;++i)b[i+2]=d[(x>>(60-4*i))&15];b[18]=0;put(b);}
static void field(const char *n,U64 v){put(n);hex(v);put("\r\n");}
static void check(const char *n,BOOL good){put(good?"PASS ":"FAIL ");put(n);put("\r\n");if(!good)++failures;}
static void one(const U16 *path,const char *label,U32 request,U32 previously_observed,OpenFn open,QueryFn query,ReadFn read,CloseFn close){
 put("FILE=");put(label);put("\r\n");U32 len=0;while(path[len])++len;struct US name={(U16)(len*2),(U16)((len+1)*2),(U16*)path};struct OA attr={sizeof(attr),NULL,&name,0x40,NULL,NULL};struct IOSB io={0};HANDLE file=NULL;
 LONG s=open(&file,0x00100001,&attr,&io,7,0x24);field("open_status=",(U32)s);check("open-observed-options",s==0);if(s)return;
 struct STANDARD info={0};s=query(file,&io,&info,sizeof(info),5);field("query_status=",(U32)s);field("query_information=",io.information);field("end_of_file=",(U64)info.end);field("allocation_size=",(U64)info.allocation);check("query-file-standard",s==0&&io.information==sizeof(info));
 U8 *bytes=VirtualAlloc(NULL,(SIZE)request+32,0x3000,4);check("buffer-allocated",bytes!=NULL);if(!bytes){close(file);return;}
 for(U32 i=0;i<request+32;++i)bytes[i]=0xa5;
 io.status=(LONG)0x55555555;io.information=(SIZE)-1;
 s=read(file,NULL,NULL,NULL,&io,bytes,request,NULL,NULL);
 field("requested_length=",request);field("read_status=",(U32)s);field("iosb_status=",(U32)io.status);field("actual_bytes=",io.information);
 check("read-size-matches-file-and-host-trace",s==0&&io.status==0&&io.information==(U64)info.end&&io.information==previously_observed);
 BOOL tail=io.information<=request;for(SIZE i=io.information;i<request+32&&tail;++i)if(bytes[i]!=0xa5)tail=0;
 check("unread-tail-not-overwritten",tail);
 U64 hash=0xcbf29ce484222325ull;if(io.information<=request)for(SIZE i=0;i<io.information;++i){hash^=bytes[i];hash*=0x100000001b3ull;}
 field("valid_bytes_fnv1a64=",hash);
 check("close",close(file)==0);check("release",VirtualFree(bytes,0,0x8000));
}
void mainCRTStartup(void){
 console=GetStdHandle((U32)-11);disk=CreateFileW(L"C:\\adhesive-fileprobe-result.txt",0x40000000,1,NULL,1,0x80,NULL);if(disk==(HANDLE)(SIZE)-1)ExitProcess(5);
 HMODULE nt=GetModuleHandleW(L"ntdll.dll");OpenFn open=(OpenFn)GetProcAddress(nt,"NtOpenFile");QueryFn query=(QueryFn)GetProcAddress(nt,"NtQueryInformationFile");ReadFn read=(ReadFn)GetProcAddress(nt,"NtReadFile");CloseFn close=(CloseFn)GetProcAddress(nt,"NtClose");
 check("required-exports",open&&query&&read&&close);
 if(open&&query&&read&&close){
  one(L"\\??\\C:\\windows\\system32\\ntdll.dll","ntdll.dll",0x13d000,1296644,open,query,read,close);
  one(L"\\??\\C:\\windows\\system32\\win32u.dll","win32u.dll",0x61000,393400,open,query,read,close);
 }
 field("failures=",failures);put(failures?"RESULT=FAIL\r\n":"RESULT=PASS\r\n");FlushFileBuffers(disk);CloseHandle(disk);ExitProcess(failures?1:0);
}
