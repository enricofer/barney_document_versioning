from functools import reduce
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from .models import Version
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
import diff_match_patch as dmp_module
import whatthepatch
from .diff3 import diff3, merge as merge3, SEPARATORS
from markdown import markdown

dmp = dmp_module.diff_match_patch()

import sys
import re
import json
import os
import subprocess
import difflib

def conta_rami(versione):
    rami = Version.objects.filter(parent__pk=versione.pk)
    print ('rami:',rami, len(rami), file=sys.stderr)
    return len(rami)

# Create your views here.
def new_version(request, master_id):
    documento_master = Version.objects.get(pk=master_id)
    versione = Version()
    versione.parent = documento_master
    versione.title = "ramo-%s" % str(conta_rami(documento_master) + 1)
    versione.base = documento_master.content
    versione.content = documento_master.content
    print ('patch:',versione, file=sys.stderr)
    versione.save()
    return JsonResponse({"new_version_id":str(versione.pk)})

    
def reconcile(request, id):
    versione = Version.objects.get(pk=id)

    patch = dmp.patch_fromText(versione.patch)
    print ('PATCH',patch[0], dir(patch[0]), file=sys.stderr)
    res_patch =  dmp.patch_apply(patch, versione.parent.content)
    reconciled =  reduce(lambda a,b: a and b, res_patch[1], True)

    for i,p in enumerate(patch):
        print ('PATCH:',i, p.diffs, p.length1, p.length2, p.start1, p.start2,file=sys.stderr) 

    #print ('VERSION_CANDIDATE:\n',res_patch[0], file=sys.stderr)

    if reconciled:
        versione.parent.content = res_patch[0]
        versione.parent.save()
        redirect = versione.parent.pk
    else:
        res_diff3 = diff3(versione.content,res_patch[0],versione.parent.content)
        res_merge3_obj = merge3(versione.content,res_patch[0],versione.parent.content)
        res_merge3 = "".join(res_merge3_obj["body"])
        keep1 = res_merge3.split(SEPARATORS[3])
        keep2 = keep1[1].split(SEPARATORS[1])
        res_merge2 = keep1[0]+SEPARATORS[1]+keep2[1]
        print ('VERSION_CONFLICT:\n',res_merge2, file=sys.stderr)
        conflicted = Version()
        conflicted.parent = versione.parent
        conflicted.base = versione.parent.content
        conflicted.patch = "CONFLICTED"
        conflicted.content = res_merge2
        conflicted.title = versione.title + "__conflicted"
        conflicted.save()
        redirect = conflicted.pk

    return JsonResponse({"result":res_patch, "reconciled": reconciled, "redirect_id":str(redirect)})

def edit(request, id):
    versione = Version.objects.get(pk=id)
    return render(request, 'editor.html', {"version": versione, "content_html": markdown(versione.content)})

@csrf_exempt
def details(request, id):
    versione = Version.objects.get(pk=id)
    return JsonResponse({"details": model_to_dict(versione)})

@csrf_exempt
def vlist(request):
    vlist = []
    for v in Version.objects.all():
        item = getVersionObject(v)
    vlist.append(item)
    return JsonResponse({"versions_list":vlist})

@csrf_exempt
def getVersionObject(v):
    return {
        "title": v.title,
        "id": v.pk,
        "path": str(v),
        "parent_name": v.parent.title if v.parent else "",
        "parent_id": v.parent.pk if v.parent else -1,
        "conflicted": v.patch == "CONFLICTED",
        "reconciliated": v.patch == "RECONCILIATED",
        "master": False if v.parent else True
    }    

@csrf_exempt
def vtree(request):
    tree = []

    def traverse_nodes(node):
        node_content = getVersionObject(node)
        item = {
            "text": node_content["title"],
            "payload": json.dumps(node_content),
            "draggable":False,
            "droppable": False,
            "children": [],
        }
        children = Version.objects.filter(parent__pk=node.pk)
        print (node,'> children:',children, file=sys.stderr)
        for child in children:
            item["children"].append(traverse_nodes(child))
        return item
    
    root_nodes = Version.objects.filter(parent__pk=None)
    print ('root_nodes:',root_nodes, file=sys.stderr)
    for node in root_nodes:
        tree.append(traverse_nodes(node))

    return JsonResponse({"versions_tree":tree})
    

@csrf_exempt
def save(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        postData = json.loads(body)
        versione = Version.objects.get(pk=postData["pk"])
        versione.content = postData['content']
        print ('NEW_CONTENT:\n',postData['content'], file=sys.stderr)
        versione.title = postData['title']
        versione.save()
        return JsonResponse({"result":"ok","error": ""})
    else:
        return JsonResponse({"result":"ko","error": "wrong http method"})


