#include "JCBL_buck_DBHR2024bV1_1_capi_host.h"
static JCBL_buck_DBHR2024bV1_1_host_DataMapInfo_T root;
static int initialized = 0;
__declspec( dllexport ) rtwCAPI_ModelMappingInfo *getRootMappingInfo()
{
    if (initialized == 0) {
        initialized = 1;
        JCBL_buck_DBHR2024bV1_1_host_InitializeDataMapInfo(&(root), "JCBL_buck_DBHR2024bV1_1");
    }
    return &root.mmi;
}

rtwCAPI_ModelMappingInfo *mexFunction(){return(getRootMappingInfo());}
