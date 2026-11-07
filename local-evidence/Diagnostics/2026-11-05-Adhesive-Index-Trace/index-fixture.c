#include "../2026-11-05-Compatibility-Fix/winmini.h"
static volatile U64 checksum;
__declspec(dllexport) __declspec(noinline) void IndexBoundary(U32 index){checksum+=index;}
void mainCRTStartup(void){IndexBoundary(0);IndexBoundary(1);IndexBoundary(9);IndexBoundary(1467);IndexBoundary(1477);ExitProcess(checksum==2954?0:1);}
