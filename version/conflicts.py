
from functools import reduce
from django.forms.models import model_to_dict
import diff_match_patch as dmp_module
from .diff3 import diff3, merge as merge3, SEPARATORS

dmp = dmp_module.diff_match_patch()

def getConflicts (versione, quick=False):
    if versione.status == 'History':
        return {
            "conflicts": 0,
            "failed_patches": [],
            "success_patches": [],
            "source_content": "",
            "target_content": "",
            "conflicted_content": "Historical version " + versione.modify_date.strftime("%Y-%m-%dT%H:%M:%S")
        }

    dmp.Patch_DeleteThreshold = 0.2
    dmp.Match_Threshold = 0
    failed_patches = []
    success_patches = []
    source_content = ""
    conflicted_content = ""
    if versione.parent:
        patch = dmp.patch_fromText(versione.patch)
        res_patch =  dmp.patch_apply(patch, versione.parent.content)
        reconciliable =  reduce(lambda a,b: a and b, res_patch[1], True)
        
        for i,p in enumerate(patch):
            #diffs = [[int(a[0]),a[1]] for a in p.diffs]

            diff = { "id": i }
            for k,d in enumerate(p.diffs):
                if d[0] == 0 and k == 0:
                    diff["before"] = d[1]
                if d[0] == 0 and k > 0:
                    diff["after"] = d[1]
                if d[0] == -1:
                    diff["delete"] = d[1]
                if d[0] == 1:
                    diff["add"] = d[1]
            
            if not res_patch[1][i]:
                failed_patches.append(diff)
            else:
                success_patches.append(diff)
        
        source_content = res_patch[0]
        if len(failed_patches) > 0 and not quick:
            #res_merge3_obj = merge3(versione.content,res_patch[0],versione.parent.content)
            res_merge3_obj = merge3(res_patch[0],versione.parent.content,versione.base)
            res_merge3 = "".join(res_merge3_obj["body"])
            if SEPARATORS[1] in res_merge3:
                keep1 = res_merge3.split(SEPARATORS[3])
                keep2 = keep1[1].split(SEPARATORS[1])
                conflicted_content = keep1[0]+SEPARATORS[1]+keep2[1]
            else:
                conflicted_content = res_merge3

        return {
            "conflicts": len(failed_patches),
            "failed_patches": failed_patches,
            "success_patches": success_patches,
            "source_content": source_content,
            "target_content": versione.parent.content,
            "conflicted_content": conflicted_content
        }
    else:
        return {
            "conflicts": 0,
            "failed_patches": [],
            "success_patches": [],
            "source_content": "",
            "target_content": "",
            "conflicted_content": "Master version " + versione.modify_date.strftime("%Y-%m-%dT%H:%M:%S")
        }
