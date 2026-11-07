#include "winmini.h"
static U32 attached;
EXPORT U32 CompatAttachCount(void){return attached;}
BOOL DllMain(void *module,U32 reason,void *reserved){
 (void)module;(void)reserved;
 if(reason==1){
#if FIXTURE_KIND == 1
  return 0;
#elif FIXTURE_KIND == 2
  volatile U8 *invalid=(volatile U8*)(SIZE)1;
  volatile U8 value=*invalid;(void)value;
#else
  ++attached;
#endif
 }
 return 1;
}
