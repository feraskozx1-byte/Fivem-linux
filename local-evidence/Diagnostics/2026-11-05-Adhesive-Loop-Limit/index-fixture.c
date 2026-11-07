#include "../2026-11-05-Compatibility-Fix/winmini.h"
static volatile U64 checksum;
__declspec(dllexport) __declspec(noinline) void IndexBoundary(U32 value){checksum+=value;}
__declspec(dllexport) __declspec(noinline) void LimitBoundary(U32 value){checksum+=2ULL*value;}
__declspec(dllexport) __declspec(noinline) void ReturnBoundary(U32 value){checksum+=3ULL*value;}
void mainCRTStartup(void){
 IndexBoundary(0);LimitBoundary(1);
 IndexBoundary(1);LimitBoundary(2);
 IndexBoundary(9);LimitBoundary(10);
 IndexBoundary(1467);LimitBoundary(1468);
 IndexBoundary(1477);LimitBoundary(1478);
 ReturnBoundary(5);ExitProcess(checksum==8887?0:1);
}
