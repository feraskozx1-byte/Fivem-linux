#include "../2026-11-05-Compatibility-Fix/winmini.h"
/* Public PE export-table contract, independent of Adhesive/FiveM. */
static HANDLE output,disk;static U32 failures,checks;
static void put(const char*s){U32 n=0,w;while(s[n])++n;WriteFile(output,s,n,&w,NULL);WriteFile(disk,s,n,&w,NULL);}
static void hex(U64 v){char b[19];const char*d="0123456789abcdef";b[0]='0';b[1]='x';for(U32 i=0;i<16;++i)b[i+2]=d[(v>>(60-4*i))&15];b[18]=0;put(b);}
static void field(const char*n,U64 v){put(n);hex(v);put("\r\n");}
static void check(const char*n,BOOL ok){++checks;if(!ok)++failures;put(ok?"PASS ":"FAIL ");put(n);put("\r\n");}
static BOOL range(U32 at,U64 size,U32 image){return at<=image&&size<=image-at;}
void mainCRTStartup(void){
 output=GetStdHandle((U32)-11);disk=CreateFileW(L"C:\\rca-export-probe-result.txt",0x40000000,1,NULL,1,0x80,NULL);if(disk==(HANDLE)(SIZE)-1)ExitProcess(5);
 U8*base=GetModuleHandleW(L"ntdll.dll");check("loaded public NTDLL available",base!=NULL);if(!base)ExitProcess(2);
 U32 pe=*(U32*)(base+60);check("PE signature",*(U32*)(base+pe)==0x4550);check("PE32+",*(U16*)(base+pe+24)==0x20b);
 U32 image=*(U32*)(base+pe+80),er=*(U32*)(base+pe+136),esz=*(U32*)(base+pe+140);
 if(!range(er,40,image))ExitProcess(3);
 U8*ed=base+er;U32 nf=*(U32*)(ed+20),nn=*(U32*)(ed+24),af=*(U32*)(ed+28),an=*(U32*)(ed+32),ao=*(U32*)(ed+36);
 field("SizeOfImage=",image);field("NumberOfFunctions=",nf);field("NumberOfNames=",nn);field("AddressOfNames=",an);field("AddressOfNameOrdinals=",ao);
 BOOL tables=range(af,4ULL*nf,image)&&range(an,4ULL*nn,image)&&range(ao,2ULL*nn,image);
 check("export tables fit SizeOfImage",tables);if(!tables)ExitProcess(3);
 U32 malformed=0,resolver_mismatch=0,forwarders=0;
 for(U32 i=0;i<nn;++i){
  U32 name=*(U32*)(base+an+4*i);U16 ord=*(U16*)(base+ao+2*i);
  if(!range(name,1,image)||ord>=nf){++malformed;continue;}
  U32 end=name;while(end<image&&base[end])++end;if(end==image){++malformed;continue;}
  U32 fn=*(U32*)(base+af+4*ord);if(!range(fn,1,image)){++malformed;continue;}
  if(fn>=er&&fn-er<esz){++forwarders;continue;}
  FARPROC resolved=GetProcAddress(base,(const char*)(base+name));
  if((SIZE)resolved!=(SIZE)(base+fn))++resolver_mismatch;
 }
 field("names_checked=",nn);field("forwarders_skipped=",forwarders);field("malformed_entries=",malformed);field("resolver_mismatches=",resolver_mismatch);
 check("all declared names/ordinals/functions structurally valid",malformed==0);
 check("GetProcAddress agrees with every direct named export",resolver_mismatch==0);
 /* Replay only the captured table-index arithmetic; do not dereference a bad RVA. */
 U32 index=1477;field("captured_index=",index);
 check("captured index rejected by NumberOfNames bound",index>=nn);
 U32 at=an+index*4;
 if(range(at,4,image)){
  U32 value=*(U32*)(base+at);field("unchecked_table_lookup_RVA=",value);
  check("lookup spills into ordinal table",at==ao+(index-nn)*4);
  check("captured DWORD reproduced",value==0x130012);
  check("reproduced RVA rejected by SizeOfImage bound",!range(value,1,image));
 }else check("captured lookup location inside image",0);
 field("checks=",checks);field("failures=",failures);put(failures?"RESULT=FAIL\r\n":"RESULT=PASS\r\n");FlushFileBuffers(disk);CloseHandle(disk);ExitProcess(failures?1:0);
}
