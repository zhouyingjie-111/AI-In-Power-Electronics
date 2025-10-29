#ifndef JCBL_buck_DBHR2024bV1_1_private_h_
#define JCBL_buck_DBHR2024bV1_1_private_h_
#include "rtwtypes.h"
#include "builtin_typeid_types.h"
#include "multiword_types.h"
#include "zero_crossing_types.h"
#include <stddef.h>
#include <float.h>
#include "mwmathutil.h"
#include "JCBL_buck_DBHR2024bV1_1.h"
#include "JCBL_buck_DBHR2024bV1_1_types.h"
#include <math.h>
#include <stdlib.h>
#include <string.h>
#if !defined(rt_VALIDATE_MEMORY)
#define rt_VALIDATE_MEMORY(S, ptr)     if(!(ptr)) {\
    ssSetErrorStatus(rtS, RT_MEMORY_ALLOCATION_ERROR);\
    }
#endif
#if !defined(rt_FREE)
#if !defined(_WIN32)
#define rt_FREE(ptr)     if((ptr) != (NULL)) {\
    free((ptr));\
    (ptr) = (NULL);\
    }
#else
#define rt_FREE(ptr)     if((ptr) != (NULL)) {\
    free((void *)(ptr));\
    (ptr) = (NULL);\
    }
#endif
#endif
#ifndef CodeFormat
#define CodeFormat   S-Function
#else
#undef CodeFormat
#define CodeFormat   S-Function
#endif
#ifndef S_FUNCTION_NAME
#define S_FUNCTION_NAME   simulink_only_sfcn
#else
#undef S_FUNCTION_NAME
#define S_FUNCTION_NAME   simulink_only_sfcn
#endif
#ifndef S_FUNCTION_LEVEL
#define S_FUNCTION_LEVEL  2
#else
#undef S_FUNCTION_LEVEL
#define S_FUNCTION_LEVEL  2
#endif
#ifndef RTW_GENERATED_S_FUNCTION
#define RTW_GENERATED_S_FUNCTION
#endif
#ifndef rtmGetDataMapInfo
#define rtmGetDataMapInfo(rtm)        NULL
#endif
#ifndef rtmSetDataMapInfo
#define rtmSetDataMapInfo(rtm, val)
#endif
#if !defined(RTW_SFUNCTION_DEFINES)
#define RTW_SFUNCTION_DEFINES
#ifndef _RTW_COMMON_DEFINES_
#define _RTW_COMMON_DEFINES_
#endif
#endif
#ifndef __RTW_UTFREE__
extern void * utMalloc ( size_t ) ; extern void utFree ( void * ) ;
#endif
void * rt_TDelayCreateBuf ( int_T numBuffer , int_T bufSz , int_T elemSz ) ;
boolean_T rt_TDelayUpdateTailOrGrowBuf ( int_T * bufSzPtr , int_T * tailPtr ,
int_T * headPtr , int_T * lastPtr , real_T tMinusDelay , real_T * * uBufPtr ,
boolean_T isfixedbuf , boolean_T istransportdelay , int_T * maxNewBufSzPtr )
; real_T rt_TDelayInterpolate ( real_T tMinusDelay , real_T tStart , real_T *
uBuf , int_T bufSz , int_T * lastIdx , int_T oldestIdx , int_T newIdx ,
real_T initOutput , boolean_T discrete , boolean_T
minorStepAndTAtLastMajorOutput ) ; void rt_TDelayFreeBuf ( void * buf ) ;
extern real_T look1_binlxpw ( real_T u0 , const real_T bp0 [ ] , const real_T
table [ ] , uint32_T maxIndex ) ; extern void hp5si4jcaf ( o3a4caclaj *
localB , b1ioo2ua1e * localP ) ; extern void bkqbq1qpit ( SimStruct * rtS_e ,
boolean_T orabwzzeeo , real_T gduwls1m55 , o3a4caclaj * localB , fmhxetgv03 *
localDW , aobwuw1znn * localZCE ) ; extern void pyorh4fsrm ( l5jfeuc324 *
localB , d5pjbmb25h * localP ) ; extern void cg52ak5rbj ( SimStruct * rtS_m ,
real_T kaa20ov0ws , boolean_T duz0mvnn2d , boolean_T n4s53miwhz , l5jfeuc324
* localB , cjw4fy44xo * localDW ) ; extern void h22u5lvjwv ( jgy23y0acc *
localB , h2ldge0e2s * localP ) ; extern void ke0ovyvkjx ( SimStruct * rtS_e ,
real_T hkqga1tndr , boolean_T nnlycgnpdq , boolean_T dqgxkwimo3 , jgy23y0acc
* localB , eko01ks4rn * localDW ) ; extern void bpxra1e05j ( boolean_T
l3nahrezf1 , b3l0z3e3vp * localB , gwxtk5vx5x * localDW , o2aeegoppq * localP
) ; extern void pvgrvjadcc ( SimStruct * rtS_g , gwxtk5vx5x * localDW ) ;
extern void b1h4dxpltx ( real_T eg34xgb2pj , b3l0z3e3vp * localB , gwxtk5vx5x
* localDW , kqpoezcndp * localZCSV ) ; extern void mv1tbvggx5 ( gwxtk5vx5x *
localDW ) ; extern void fb4adn5bw3 ( SimStruct * rtS_m , boolean_T n354o3yszq
, b3l0z3e3vp * localB , gwxtk5vx5x * localDW ) ; extern void nvd5ofuthx ( SimStruct * rtS_j , boolean_T ntl2xislcz , boolean_T n354o3yszq , real_T eg34xgb2pj , real_T llgkhqs1is , b3l0z3e3vp * localB , gwxtk5vx5x * localDW , o2aeegoppq * localP , pr1u4ckp4n * localZCE ) ; extern void nvd5ofuthxTID4 ( SimStruct * rtS_f , b3l0z3e3vp * localB , gwxtk5vx5x * localDW , o2aeegoppq * localP ) ; extern void efm0zvafif ( boolean_T f2vsh3djtd , cjupd0zf1s * localB , imppluci5l * localDW , oogpyowcji * localP ) ; extern void c0y1e3tomy ( SimStruct * rtS_g , imppluci5l * localDW ) ; extern void c1izdeul1a ( real_T i3lvgq2lzs , cjupd0zf1s * localB , imppluci5l * localDW , cvpny0ayke * localZCSV ) ; extern void hwqb4m4zui ( imppluci5l * localDW ) ; extern void pzsedtbl1w ( SimStruct * rtS_l , boolean_T mcj41fqcvs , cjupd0zf1s * localB , imppluci5l * localDW ) ; extern void loki5osupm ( SimStruct * rtS_n , boolean_T ko0j4tp1zq , boolean_T mcj41fqcvs , real_T i3lvgq2lzs , real_T kmabxa2qdx , cjupd0zf1s * localB , imppluci5l * localDW , oogpyowcji * localP , aiiyubqti2 * localZCE ) ; extern void loki5osupmTID4 ( SimStruct * rtS_p , cjupd0zf1s * localB , imppluci5l * localDW , oogpyowcji * localP ) ;
#if defined(MULTITASKING)
#error Models using the variable step solvers cannot define MULTITASKING
#endif
#endif
