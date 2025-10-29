#ifndef JCBL_buck_DBHR2024bV1_1_h_
#define JCBL_buck_DBHR2024bV1_1_h_
#ifndef JCBL_buck_DBHR2024bV1_1_COMMON_INCLUDES_
#define JCBL_buck_DBHR2024bV1_1_COMMON_INCLUDES_
#include <stdio.h>
#include <stdlib.h>
#include "sl_AsyncioQueue/AsyncioQueueCAPI.h"
#include "rtwtypes.h"
#include "sigstream_rtw.h"
#include "simtarget/slSimTgtSigstreamRTW.h"
#include "simtarget/slSimTgtSlioCoreRTW.h"
#include "simtarget/slSimTgtSlioClientsRTW.h"
#include "simtarget/slSimTgtSlioSdiRTW.h"
#include "simstruc.h"
#include "fixedpoint.h"
#include "raccel.h"
#include "slsv_diagnostic_codegen_c_api.h"
#include "rt_logging_simtarget.h"
#include "rt_nonfinite.h"
#include "math.h"
#include "dt_info.h"
#include "ext_work.h"
#endif
#include "JCBL_buck_DBHR2024bV1_1_types.h"
#include <stddef.h>
#include <string.h>
#include "rtw_modelmap_simtarget.h"
#include "rt_defines.h"
#include "rtGetInf.h"
#include "zero_crossing_types.h"
#define MODEL_NAME JCBL_buck_DBHR2024bV1_1
#define NSAMPLE_TIMES (5) 
#define NINPUTS (0)       
#define NOUTPUTS (0)     
#define NBLOCKIO (182) 
#define NUM_ZC_EVENTS (8) 
#ifndef NCSTATES
#define NCSTATES (14)   
#elif NCSTATES != 14
#error Invalid specification of NCSTATES defined in compiler command
#endif
#ifndef rtmGetDataMapInfo
#define rtmGetDataMapInfo(rtm) (*rt_dataMapInfoPtr)
#endif
#ifndef rtmSetDataMapInfo
#define rtmSetDataMapInfo(rtm, val) (rt_dataMapInfoPtr = &val)
#endif
#ifndef IN_RACCEL_MAIN
#endif
typedef struct { real_T kgfafranqp ; } o3a4caclaj ; typedef struct { int8_T
fgqiszwjfb ; } fmhxetgv03 ; typedef struct { real_T ddpcpmdpuq ; } n2k0guofkx
; typedef struct { ZCSigState i4g5kbucmm ; } aobwuw1znn ; typedef struct {
boolean_T di4cc0djtg ; } l5jfeuc324 ; typedef struct { int8_T bl5unxe5qb ; }
cjw4fy44xo ; typedef struct { boolean_T mivsv0p1ga ; } jgy23y0acc ; typedef
struct { int8_T nbq3ifmreh ; } eko01ks4rn ; typedef struct { real_T
jm4yi4zlhr ; real_T kv5myklx1w ; real_T ovel3cjtov ; real_T lftyf30dts ;
real_T akucnpziw4 ; real_T hsac3hu1nf [ 2 ] ; boolean_T ayp0fkjftj ;
boolean_T ku2mk1f0wq ; boolean_T jvwwoyxizw ; jgy23y0acc ke0ovyvkjxg ;
l5jfeuc324 cg52ak5rbj5 ; o3a4caclaj bkqbq1qpitt ; } b3l0z3e3vp ; typedef
struct { real_T hv3r2ijr2x ; int8_T hrt2icxcxe ; boolean_T kt00ipvbzb ;
boolean_T hp013rjhzw ; boolean_T blpvwhdvr0 ; boolean_T pzz3djh1m0 ;
eko01ks4rn ke0ovyvkjxg ; cjw4fy44xo cg52ak5rbj5 ; fmhxetgv03 bkqbq1qpitt ; }
gwxtk5vx5x ; typedef struct { real_T ivqmbo24wj ; real_T pqgveqdbrd ;
n2k0guofkx bkqbq1qpitt ; } kqpoezcndp ; typedef struct { aobwuw1znn
bkqbq1qpitt ; } pr1u4ckp4n ; typedef struct { real_T a2lfbsy4cs ; real_T
ljmanj53r0 ; real_T fjr3lpwqa5 ; real_T c0bgxpqg0v ; real_T bi4luawlp4 ;
real_T m1qr1ecdnb [ 2 ] ; boolean_T jcnq3xzaim ; boolean_T o45o0wsteg ;
boolean_T orstwbmzqt ; jgy23y0acc hdj3wqdohr ; l5jfeuc324 em1ujbr42u ;
o3a4caclaj gg21spqnj5 ; } cjupd0zf1s ; typedef struct { real_T kc0czxlvix ;
int8_T o533iywxmw ; boolean_T gcdjak4xrh ; boolean_T idx1opyf2w ; boolean_T
eduysmhfye ; boolean_T ka3uhwvx5i ; eko01ks4rn hdj3wqdohr ; cjw4fy44xo
em1ujbr42u ; fmhxetgv03 gg21spqnj5 ; } imppluci5l ; typedef struct { real_T
l51fkon0d2 ; real_T niwwhscv31 ; n2k0guofkx gg21spqnj5 ; } cvpny0ayke ;
typedef struct { aobwuw1znn gg21spqnj5 ; } aiiyubqti2 ; typedef struct {
creal_T dnp4xhqtmm ; creal_T anl0tg4iz1 ; creal_T n543rgdc5p ; creal_T
it5skppvd3 ; real_T abpfnsf1za ; real_T lkdwg1e5as [ 16 ] ; real_T hysz5xbpi4
[ 9 ] ; real_T k304e1ffaf ; real_T coe52itnyj ; real_T ofgigatwme ; real_T
ew24g1cq3f ; real_T eg2ebhj1nk ; real_T mtjhreoifs ; real_T m5ryk3hdiv ;
real_T gzp23yd1xv ; real_T cwz10fldst ; real_T bfyozmv3px ; real_T pbyyfznmio
; real_T myg5swu2wb ; real_T ioi1uyv1fn ; real_T nmcbo1u1cf ; real_T
ge4lifbpj5 ; real_T mv4hqtekcz ; real_T mwezxuddk0 ; real_T dietul3zsf ;
real_T by5zad2onw ; real_T cyzbgyotev ; real_T jsczkkzz2y ; real_T di13widl00
; real_T hfzwclvxzm ; real_T fxxy1ey0fk ; real_T oigfmvncad ; real_T
jpsto2dx5g ; real_T ahxbcbdnrs [ 2 ] ; real_T dawhtu05zh [ 2 ] ; real_T
cbzs3aoi33 ; real_T i4ldxcfyv0 ; real_T fem1cpj0o2 ; real_T flbmpvq24q ;
real_T gn2zf0jpxq ; real_T hx5fnaaum0 ; real_T oiwfgog0k1 ; real_T cr5skyilwh
; real_T lgogrse5na ; real_T c5byjgqb1r ; real_T cixybdmuda ; real_T
cg4fkviq31 ; real_T f5ahwbuvym ; real_T ekktospgws [ 2 ] ; real_T jtdtjsfqec
[ 2 ] ; real_T pjqaf5khvb ; real_T ekadme4enf ; real_T py0xumfzpu ; real_T
pp00h1aqqk ; real_T ddt1xyv13a ; real_T f5bpgag2mb ; real_T mkt3ad4pyq [ 2 ]
; real_T ehqzdwrgsf [ 2 ] ; real_T fmwoevyy1z [ 2 ] ; real_T imbxgfc4ak [ 2 ]
; real_T p4tlufthqw [ 2 ] ; real_T nkhwej22z3 [ 2 ] ; real_T lcm31d2cuv [ 2 ]
; real_T jaxbhot51p [ 2 ] ; real_T owyelytkl4 ; real_T nz0veajr34 ; real_T
l0fogrw55g [ 2 ] ; real_T ecwdayciz4 [ 2 ] ; real_T b4m0uyma5n ; real_T
c3wmealgiz ; boolean_T j3xgfsagbd ; boolean_T hbotkeaclm ; boolean_T
iiultfa0yi ; boolean_T gbnlfgyum1 ; boolean_T kv1yw00kog ; boolean_T
fdnho0gvji ; boolean_T oakl0w4pqn ; boolean_T miy12mwpno ; boolean_T
earihymrhz ; boolean_T jua5gapl55 ; boolean_T kzqruazo3h ; boolean_T
d5duzr3tcn ; boolean_T fmf24kznuy ; boolean_T luf4se5thf ; boolean_T
l4mszvm4ey ; boolean_T ek3b525y33 ; cjupd0zf1s onbve342oz ; b3l0z3e3vp
i4guox0dks ; cjupd0zf1s awk1sqt1lf ; b3l0z3e3vp hquvqsfosa ; cjupd0zf1s
hm4diydndl ; b3l0z3e3vp do3rpmepfq ; cjupd0zf1s loki5osupmm ; b3l0z3e3vp
nvd5ofuthxp ; } B ; typedef struct { real_T o0sdw4ga04 [ 3 ] ; real_T
dqzphpqe0m ; struct { real_T modelTStart ; } gvn4ktrc32 ; struct { real_T
modelTStart ; } cllnfwz3tb ; struct { real_T modelTStart ; } mfjk4saosj ;
struct { real_T modelTStart ; } lvbigskvem ; struct { real_T modelTStart ; }
lz3migfs5x ; struct { void * AS ; void * BS ; void * CS ; void * DS ; void *
DX_COL ; void * BD_COL ; void * TMP1 ; void * TMP2 ; void * XTMP ; void *
SWITCH_STATUS ; void * SWITCH_STATUS_INIT ; void * SW_CHG ; void * G_STATE ;
void * USWLAST ; void * XKM12 ; void * XKP12 ; void * XLAST ; void * ULAST ;
void * IDX_SW_CHG ; void * Y_SWITCH ; void * SWITCH_TYPES ; void * IDX_OUT_SW
; void * SWITCH_TOPO_SAVED_IDX ; void * SWITCH_MAP ; } jerqxxmqcs ; struct {
void * LoggedData ; } lesysrk11a ; struct { void * LoggedData ; } ebpteyuskx
; struct { void * LoggedData [ 3 ] ; } aa0w4souqn ; struct { void *
LoggedData ; } a4g4qpnema ; struct { void * LoggedData [ 2 ] ; } ijxmenl5q5 ;
struct { void * LoggedData [ 2 ] ; } iw0piyjyup ; struct { void * LoggedData
[ 2 ] ; } lxd2jdhomv ; struct { void * LoggedData [ 2 ] ; } ov555evyfn ;
struct { void * TUbufferPtrs [ 4 ] ; } mmnltffxgf ; struct { void *
TUbufferPtrs [ 4 ] ; } d12kd2d2y2 ; struct { void * LoggedData ; } mp4ukcqxxq
; struct { void * LoggedData [ 2 ] ; } oabkbijn5b ; struct { void *
LoggedData [ 2 ] ; } cpr30yglxz ; struct { void * LoggedData ; } abvlyepici ;
struct { void * AQHandles ; } pltfns05y4 ; struct { void * AQHandles ; }
ocdwnwqnp5 ; struct { void * AQHandles ; } munpszj1ln ; struct { void *
AQHandles ; } dzbb1jxxpe ; struct { void * TUbufferPtrs [ 2 ] ; } phmvx4tgje
; struct { void * LoggedData ; } nut5kfpzra ; struct { void * LoggedData ; }
j21xxsftse ; struct { void * TUbufferPtrs [ 4 ] ; } bjikh0xvea ; struct {
void * TUbufferPtrs [ 4 ] ; } mpqxasqd4p ; struct { void * LoggedData ; }
ksfkcfldsa ; struct { void * AQHandles ; } bfjshdunpe ; struct { void *
AQHandles ; } o0mgvc0war ; struct { void * LoggedData ; } gzhxp04pko ; int_T
mrbodwon5t [ 11 ] ; struct { int_T Tail [ 2 ] ; int_T Head [ 2 ] ; int_T Last
[ 2 ] ; int_T CircularBufSize [ 2 ] ; int_T MaxNewBufSize ; } gpyrwaevh4 ;
struct { int_T Tail [ 2 ] ; int_T Head [ 2 ] ; int_T Last [ 2 ] ; int_T
CircularBufSize [ 2 ] ; int_T MaxNewBufSize ; } ctgjr0hgl4 ; struct { int_T
Tail ; int_T Head ; int_T Last ; int_T CircularBufSize ; int_T MaxNewBufSize
; } hitcyyh2cc ; struct { int_T Tail [ 2 ] ; int_T Head [ 2 ] ; int_T Last [
2 ] ; int_T CircularBufSize [ 2 ] ; int_T MaxNewBufSize ; } pux4o24isy ;
struct { int_T Tail [ 2 ] ; int_T Head [ 2 ] ; int_T Last [ 2 ] ; int_T
CircularBufSize [ 2 ] ; int_T MaxNewBufSize ; } omh2qyy13y ; int_T lnmpbjbdw2
; int_T evno5delc3 ; int_T cfqgqowmvq ; int_T fdovdthfvs ; int_T incnco1a1f ;
int_T mgkjzknwtu ; int_T hqkbnj2vyw ; int_T l3nrx2fusi ; int_T cfecjurfjc ;
boolean_T gcqjhvst4s ; boolean_T hhs04u0so5 ; imppluci5l onbve342oz ;
gwxtk5vx5x i4guox0dks ; imppluci5l awk1sqt1lf ; gwxtk5vx5x hquvqsfosa ;
imppluci5l hm4diydndl ; gwxtk5vx5x do3rpmepfq ; imppluci5l loki5osupmm ;
gwxtk5vx5x nvd5ofuthxp ; } DW ; typedef struct { real_T ez1ydpwnh3 ; real_T
hfdne0xdqp ; real_T dwpsfqcztx ; real_T pwputugmmu [ 2 ] ; real_T ewehhxpwvs
[ 2 ] ; real_T l2sserro0w ; real_T hvk1eq05kj ; real_T ke4vpucm5w [ 2 ] ;
real_T ks5pzpliln [ 2 ] ; real_T en4tlrj0s0 ; } X ; typedef int_T
PeriodicIndX [ 2 ] ; typedef real_T PeriodicRngX [ 4 ] ; typedef struct {
real_T ez1ydpwnh3 ; real_T hfdne0xdqp ; real_T dwpsfqcztx ; real_T pwputugmmu
[ 2 ] ; real_T ewehhxpwvs [ 2 ] ; real_T l2sserro0w ; real_T hvk1eq05kj ;
real_T ke4vpucm5w [ 2 ] ; real_T ks5pzpliln [ 2 ] ; real_T en4tlrj0s0 ; }
XDot ; typedef struct { boolean_T ez1ydpwnh3 ; boolean_T hfdne0xdqp ;
boolean_T dwpsfqcztx ; boolean_T pwputugmmu [ 2 ] ; boolean_T ewehhxpwvs [ 2
] ; boolean_T l2sserro0w ; boolean_T hvk1eq05kj ; boolean_T ke4vpucm5w [ 2 ]
; boolean_T ks5pzpliln [ 2 ] ; boolean_T en4tlrj0s0 ; } XDis ; typedef struct
{ real_T ez1ydpwnh3 ; real_T hfdne0xdqp ; real_T dwpsfqcztx ; real_T
pwputugmmu [ 2 ] ; real_T ewehhxpwvs [ 2 ] ; real_T l2sserro0w ; real_T
hvk1eq05kj ; real_T ke4vpucm5w [ 2 ] ; real_T ks5pzpliln [ 2 ] ; real_T
en4tlrj0s0 ; } CStateAbsTol ; typedef struct { real_T ez1ydpwnh3 ; real_T
hfdne0xdqp ; real_T dwpsfqcztx ; real_T pwputugmmu [ 2 ] ; real_T ewehhxpwvs
[ 2 ] ; real_T l2sserro0w ; real_T hvk1eq05kj ; real_T ke4vpucm5w [ 2 ] ;
real_T ks5pzpliln [ 2 ] ; real_T en4tlrj0s0 ; } CXPtMin ; typedef struct {
real_T ez1ydpwnh3 ; real_T hfdne0xdqp ; real_T dwpsfqcztx ; real_T pwputugmmu
[ 2 ] ; real_T ewehhxpwvs [ 2 ] ; real_T l2sserro0w ; real_T hvk1eq05kj ;
real_T ke4vpucm5w [ 2 ] ; real_T ks5pzpliln [ 2 ] ; real_T en4tlrj0s0 ; }
CXPtMax ; typedef struct { real_T ouwydbwvat ; real_T pbnj1tfpi1 ; real_T
imcwbryzgq ; real_T nn34pnb1xu ; real_T fyo4g4a1oh ; real_T ksw2hlcmmn ;
real_T oox04nq200 ; real_T ijahzvndn2 ; real_T egzrdtyt3b ; real_T a0r5fkbhft
; real_T nrcafceouq ; real_T glh5cgwebp ; real_T gvaj1eg2to ; real_T
lvi23l0n5t ; real_T ceojn2qhob ; real_T a2bgh152fu ; real_T e0h32riugm ;
cvpny0ayke onbve342oz ; kqpoezcndp i4guox0dks ; cvpny0ayke awk1sqt1lf ;
kqpoezcndp hquvqsfosa ; cvpny0ayke hm4diydndl ; kqpoezcndp do3rpmepfq ;
cvpny0ayke loki5osupmm ; kqpoezcndp nvd5ofuthxp ; } ZCV ; typedef struct {
aiiyubqti2 onbve342oz ; pr1u4ckp4n i4guox0dks ; aiiyubqti2 awk1sqt1lf ;
pr1u4ckp4n hquvqsfosa ; aiiyubqti2 hm4diydndl ; pr1u4ckp4n do3rpmepfq ;
aiiyubqti2 loki5osupmm ; pr1u4ckp4n nvd5ofuthxp ; } PrevZCX ; typedef struct
{ rtwCAPI_ModelMappingInfo mmi ; } DataMapInfo ; struct b1ioo2ua1e_ { real_T
Out1_Y0 ; } ; struct d5pjbmb25h_ { boolean_T OUT_Y0 ; } ; struct h2ldge0e2s_
{ boolean_T OUT_Y0 ; } ; struct o2aeegoppq_ { real_T SampleandHold_ic ;
real_T EdgeDetector_model ; real_T Constant_Value ; real_T posedge_Value [ 2
] ; real_T negedge_Value [ 2 ] ; real_T eitheredge_Value [ 2 ] ; boolean_T
OUT_Y0 ; h2ldge0e2s ke0ovyvkjxg ; d5pjbmb25h cg52ak5rbj5 ; b1ioo2ua1e
bkqbq1qpitt ; } ; struct oogpyowcji_ { real_T SampleandHold_ic ; real_T
EdgeDetector_model ; real_T Constant_Value ; real_T posedge_Value [ 2 ] ;
real_T negedge_Value [ 2 ] ; real_T eitheredge_Value [ 2 ] ; boolean_T OUT_Y0
; h2ldge0e2s hdj3wqdohr ; d5pjbmb25h em1ujbr42u ; b1ioo2ua1e gg21spqnj5 ; } ;
struct P_ { real_T DC_Source_Amplitude ; real_T OnDelay1_DelayType ; real_T
OnDelay2_DelayType ; real_T OnDelay3_DelayType ; real_T OnDelay4_DelayType ;
real_T PowerMeasurement1_F ; real_T PowerMeasurement_F ; real_T
PIDController2_I ; real_T PIDController3_I ; real_T PIDController4_I ; real_T
PIDController3_InitialConditionForIntegrator ; real_T
PIDController2_InitialConditionForIntegrator ; real_T
PIDController4_InitialConditionForIntegrator ; real_T Ramp_InitialOutput ;
real_T PowerMeasurement1_K ; real_T PowerMeasurement_K ; real_T
PIDController3_LowerSaturationLimit ; real_T
PIDController2_LowerSaturationLimit ; real_T
PIDController4_LowerSaturationLimit ; real_T PIDController3_P ; real_T
PIDController2_P ; real_T PIDController4_P ; real_T
PIDController3_UpperSaturationLimit ; real_T
PIDController2_UpperSaturationLimit ; real_T
PIDController4_UpperSaturationLimit ; real_T OnDelay1_delay ; real_T
OnDelay2_delay ; real_T OnDelay3_delay ; real_T OnDelay4_delay ; real_T
RepeatingSequence1_rep_seq_y [ 3 ] ; real_T RepeatingSequence2_rep_seq_y [ 3
] ; real_T Ramp_slope ; real_T Ramp_start ; real_T
IntegratorwithWrappedStateDiscreteorContinuous_x0 ; real_T
IntegratorwithWrappedStateDiscreteorContinuous_x0_ho2g52dycf ; boolean_T
OnDelay2_ic ; boolean_T OnDelay1_ic ; boolean_T OnDelay3_ic ; boolean_T
OnDelay4_ic ; real_T Gain_Gain ; real_T Step_Time ; real_T Step_Y0 ; real_T
Step_YFinal ; real_T StateSpace_AS_param [ 9 ] ; real_T StateSpace_BS_param [
33 ] ; real_T StateSpace_CS_param [ 48 ] ; real_T StateSpace_DS_param [ 176 ]
; real_T StateSpace_X0_param [ 3 ] ; real_T donotdeletethisgain_Gain ; real_T
donotdeletethisgain_Gain_gvfqsabyx1 ; real_T Step_Y0_lxbncpeaoj ; real_T
Saturation4_UpperSat ; real_T Saturation4_LowerSat ; real_T
donotdeletethisgain_Gain_jhwfhqwbws ; real_T
donotdeletethisgain_Gain_nqt4qtawxo ; real_T Saturation1_UpperSat ; real_T
Saturation1_LowerSat ; real_T LookUpTable1_bp01Data [ 3 ] ; real_T
Saturation2_UpperSat ; real_T Saturation2_LowerSat ; real_T
LookUpTable1_bp01Data_b1l1rtt4v4 [ 3 ] ; real_T Integrator_IC ; real_T
TransportDelay_InitOutput ; real_T Integrator1_IC ; real_T
TransportDelay1_InitOutput ; real_T Gain2_Gain ; real_T integrator_IC ;
real_T TransportDelay_Delay ; real_T TransportDelay_InitOutput_kicmfwddcc ;
real_T K1_Value ; real_T Memory_InitialCondition ; real_T
donotdeletethisgain_Gain_j53zpnfq1l ; real_T
donotdeletethisgain_Gain_j1rbetrqjl ; real_T Integrator_IC_pcacovp33f ;
real_T TransportDelay_InitOutput_fombx3et2x ; real_T
Integrator1_IC_djc22nftrb ; real_T TransportDelay1_InitOutput_mtvo3uiixw ;
real_T Gain2_Gain_ofybcmyjpl ; real_T donotdeletethisgain_Gain_h2u25h3cgt ;
real_T Step1_Time ; real_T Step1_Y0 ; real_T Step1_YFinal ; real_T
SwitchCurrents_Value [ 9 ] ; real_T Constant_Value ; real_T
Constant_Value_aafub0ppks ; real_T Constant_Value_bt2nl4rme1 ; real_T
Constant_Value_f3ddoxps25 ; real_T Constant_Value_bkksiov2pm ; real_T
Constant_Value_ld5luqozqd ; oogpyowcji onbve342oz ; o2aeegoppq i4guox0dks ;
oogpyowcji awk1sqt1lf ; o2aeegoppq hquvqsfosa ; oogpyowcji hm4diydndl ;
o2aeegoppq do3rpmepfq ; oogpyowcji loki5osupmm ; o2aeegoppq nvd5ofuthxp ; } ;
extern const char_T * RT_MEMORY_ALLOCATION_ERROR ; extern B rtB ; extern X
rtX ; extern DW rtDW ; extern PrevZCX rtPrevZCX ; extern P rtP ; extern
mxArray * mr_JCBL_buck_DBHR2024bV1_1_GetDWork ( ) ; extern void
mr_JCBL_buck_DBHR2024bV1_1_SetDWork ( const mxArray * ssDW ) ; extern mxArray
* mr_JCBL_buck_DBHR2024bV1_1_GetSimStateDisallowedBlocks ( ) ; extern const
rtwCAPI_ModelMappingStaticInfo * JCBL_buck_DBHR2024bV1_1_GetCAPIStaticMap ( void
) ; extern SimStruct * const rtS ; extern DataMapInfo * rt_dataMapInfoPtr ;
extern rtwCAPI_ModelMappingInfo * rt_modelMapInfoPtr ; void MdlOutputs ( int_T
tid ) ; void MdlOutputsParameterSampleTime ( int_T tid ) ; void MdlUpdate ( int_T tid ) ; void MdlTerminate ( void ) ; void MdlInitializeSizes ( void ) ; void MdlInitializeSampleTimes ( void ) ; SimStruct * raccel_register_model ( ssExecutionInfo * executionInfo ) ;
#endif
