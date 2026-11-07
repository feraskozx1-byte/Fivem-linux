#include "winmini.h"
IMP void SetLastError(U32);
struct ANSI {U16 length,maximum;char *buffer;};
typedef U32 (*LDR)(HMODULE,const struct ANSI*,U32,FARPROC*);
static volatile U32 count=1468,sink;static volatile SIZE marker_sink;
static HANDLE log;static U32 checks,failures;
static void check(const char*s,BOOL ok){U32 n=0,w;while(s[n])n++;checks++;if(!ok)failures++;WriteFile(log,ok?"PASS ":"FAIL ",5,&w,NULL);WriteFile(log,s,n,&w,NULL);WriteFile(log,"\r\n",2,&w,NULL);}
EXPORT NOINLINE void BoundsMarker(volatile U32*p){marker_sink=(SIZE)p;}
void mainCRTStartup(void){
 log=CreateFileW(L"C:\\export-fixture.txt",0x40000000,1,NULL,1,0x80,NULL);if(log==(HANDLE)(SIZE)-1)ExitProcess(5);
 HMODULE n=GetModuleHandleW(L"ntdll.dll");
 LDR ldr=(LDR)GetProcAddress(n,"LdrGetProcedureAddress");check("public NT resolver available",ldr!=NULL);
 FARPROC known=GetProcAddress(n,"NtClose");check("known public export resolves",known!=NULL);
 SetLastError(0);FARPROC absent=GetProcAddress(n,"CodexAbsentExport_20261107");U32 error=GetLastError();
 check("missing name returns NULL",absent==NULL);check("missing name gives ERROR_PROC_NOT_FOUND",error==127);
 SetLastError(0);FARPROC wrongcase=GetProcAddress(n,"ntclose");error=GetLastError();
 check("name matching is case sensitive",wrongcase==NULL&&error==127);
 struct ANSI a={7,8,"NtClose"};FARPROC out=NULL;U32 status=ldr(n,&a,0,&out);
 check("NT resolver agrees on present name",status==0&&out==known);
 struct ANSI b={sizeof("CodexAbsentExport_20261107")-1,sizeof("CodexAbsentExport_20261107"),"CodexAbsentExport_20261107"};out=NULL;status=ldr(n,&b,0,&out);
 check("NT resolver returns PROCEDURE_NOT_FOUND",status==0xc000007au);
 BoundsMarker(&count);
 for(U32 i=0;i<4;i++)sink+=count;
 check("watch validation uses four unmodified reads",sink==4*1468);
 U32 w;WriteFile(log,failures?"RESULT=FAIL\r\n":"RESULT=PASS\r\n",13,&w,NULL);FlushFileBuffers(log);CloseHandle(log);ExitProcess(failures?1:0);
}
