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
import pypandoc

from django.core.files.temp import NamedTemporaryFile
from django.core import files

import sys
import re
import json
import os
import subprocess
import difflib
import tempfile

from io import StringIO, BytesIO

dmp = dmp_module.diff_match_patch()

def conta_rami(versione):
    rami = Version.objects.filter(parent__pk=versione.pk)
    print ('rami:',rami, len(rami), file=sys.stderr)
    return len(rami)

def versionDetails(v):
    vdict = model_to_dict(v)
    children = Version.objects.filter(parent__pk=v.pk)
    vdict["hasChildern"] = True if children else False
    return vdict

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
    return JsonResponse(versionDetails(versione))

    
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
        versione.patch = "RECONCILIATED"
        versione.title = versione.title + "__reconciliated"
        versione.save()
        redirect = versione.parent
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
        redirect = conflicted

    return JsonResponse({"reconciled": reconciled, "details":versionDetails(redirect)})

def edit(request, id):
    versione = Version.objects.get(pk=id)
    return render(request, 'editor.html', {"version": versione, "content_html": markdown(versione.content)})

def html2pdf (html):
    with open(page_html_ROOT, 'wb') as html_file:
        html_file.write(bytes(html, 'UTF-8'))

    execute ('iconv -f UTF-8 -t ISO-8859-1 -o %s  %s' % (iso_html_ROOT,page_html_ROOT))
    execute ('htmldoc --bodyfont HELVETICA --size A4 --right 26mm --left 26mm --top 20mm --bottom 20mm --fontsize 13 --fontspacing 1.4 --webpage -f %s %s' % ( page_pdf_ROOT, iso_html_ROOT))
    execute ('rm %s  %s' % (iso_html_ROOT, page_html_ROOT))

@csrf_exempt
def docx(request, id):
    return download(request, 'docx', id)
    
@csrf_exempt
def pdf(request, id):
    return download(request, 'pdf', id)
    
@csrf_exempt
def odt(request, id):
    return download(request, 'odt', id)

@csrf_exempt
def download(request, format, id):
    basedir = tempfile.mkdtemp()
    md_file = os.path.join(basedir, "input.md")
    out_file = os.path.join(basedir, "output." + format)
    versione = Version.objects.get(pk=id)
    output = pypandoc.convert_text(versione.content, format, format='md', outputfile=out_file)
    print("OUTPUT", output)
    stream = open(out_file, "rb")
    response = HttpResponse(stream, content_type="application/vnd.openxmlformats") #application/pdf
    response['Content-Disposition'] = 'attachment; filename=%s.%s' % (versione.title,format)
    return response

@csrf_exempt
def upload(request, id):
    if request.method == 'POST':
        if id:
            versione = Version.objects.get(pk=id)
        else:
            versione = Version()
        upload = request.FILES['uploaded_content']
        print ("MIMETYPE", upload.content_type)
        if upload.content_type in ("text/markdown", "text/plain"):
            versione.content = upload.read()
        elif upload.content_type in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", ):
            basedir = tempfile.mkdtemp()
            md_file = os.path.join(basedir, "input.md")
            in_file = os.path.join(basedir, "output.docx")
            with open(in_file, 'wb') as dest:
                dest.write(upload.read())
            output = pypandoc.convert(in_file, "md", format='docx', outputfile=md_file)
            with open(md_file,"r") as md:
                versione.content = md.read()
        versione.save()
        return JsonResponse({"result": "OK", "version_id":versione.pk})

@csrf_exempt
def details(request, id):
    versione = Version.objects.get(pk=id)
    return JsonResponse(versionDetails(versione))

@csrf_exempt
def delete(request, id):
    versione = Version.objects.get(pk=id)
    deleted = model_to_dict(versione)
    versione.delete()
    return JsonResponse({"deleted": "ok", "deleted_version": deleted })

@csrf_exempt
def vlist(request, fromId):
    return vtree(request, fromId, asList = True)

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
def vtree(request, fromId, asList = False):
    tree = []

    def traverse_nodes(node):
        node_content = getVersionObject(node)
        children = Version.objects.filter(parent__pk=node.pk)
        node_content["hasChildren"] = True if children else False
        node_content["text"] = node_content["title"]
        node_content["draggable"] = False
        node_content["droppable"] = False
        node_content["children"] = []

        for child in children:
            if asList:
                tree.append(traverse_nodes(child))
            else:
                node_content["children"].append(traverse_nodes(child))
        return node_content
    if fromId:
        root_nodes = Version.objects.filter(pk=fromId)
    else:
        root_nodes = Version.objects.filter(parent__pk=None)
    print ('root_nodes:',root_nodes, file=sys.stderr)
    for node in root_nodes:
        tree.append(traverse_nodes(node))

    return JsonResponse({"versions":tree})
    

@csrf_exempt
def save(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        postData = json.loads(body)
        print ('postData:\n',postData["pk"], file=sys.stderr)
        if postData["pk"] > 0:
            versione = Version.objects.get(pk=postData["pk"])
        else:
            versione = Version()
        if versione.patch == "RECONCILIATED":
            return JsonResponse({"result":"ko", "version_id": versione.pk, "error": "Reconciliated Versions cannot be modified"}, status=500)
        versione.content = postData['content']
        print ('NEW_CONTENT:\n',postData['content'], file=sys.stderr)
        versione.title = postData['title']
        versione.save()
        return JsonResponse({"result":"ok", "version_id": versione.pk, "error": ""})
    else:
        return JsonResponse({"result":"ko", "error": "wrong http method"}, status=500)


