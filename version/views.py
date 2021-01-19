from functools import reduce
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from django.core import serializers
from django.forms.models import model_to_dict
from django.conf import settings
from .models import Version
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
import diff_match_patch as dmp_module
from .diff3 import diff3, merge as merge3, SEPARATORS
from .conflicts import getConflicts
from markdown import markdown
import pypandoc

from django.views.generic import View
from jwt_auth.mixins import JSONWebTokenAuthMixin

from django.core.files.temp import NamedTemporaryFile
from django.core import files

import urllib.parse
import sys
import re
import json
import os
import subprocess
import difflib
import tempfile
import zipfile
from shutil import copyfile

from io import StringIO, BytesIO

dmp = dmp_module.diff_match_patch()

def conta_rami(v):
    rami = Version.objects.filter(parent__pk=v.pk)
    return len(rami)

def versionDetails(v):
    vdict = model_to_dict(v)
    vdict["condiv"] = [{"ftag": item, "fsearch": item} for item in json.loads(v.condiv if v.condiv else '[]')]
    children = Version.objects.filter(parent__pk=v.pk)
    vdict["hasChildren"] = True if children else False
    vdict["mergeReq"] = []
    vdict["hasMergeReq"] = False
    for child in children:
        if child.status == 'Merge_req':
            vdict["mergeReq"].append({
                "id": child.pk,
                "title": child.title
            })
    if vdict["mergeReq"]:
        vdict["hasMergeReq"] = True
    vdict["parentTitle"] = ""
    if v.parent:
        vdict["parentTitle"] = v.parent.title

        if not v.status in ('History', 'Merge_req'):
            print("NO MERGE REQ???", v.status)
            conflicts_check = getConflicts(v, quick=True)
            if conflicts_check != v.conflicts:
                v.conflicts = conflicts_check["conflicts"]
                if conflicts_check["conflicts"] == 0:
                    v.status = 'Version'
                else:
                    v.status = 'Conflicted'
                v.save()
    return vdict

# Create your views here.
def frontend(request, version=None):
    try:
        s = settings.BARNEY_CONFIG.copy()
        if version:
            s['version'] = version
        print ("?init="+json.dumps(s))
        init_param = "?init="+json.dumps(s)
    except Exception as e:
        print (e)
        init_param = ""
    return HttpResponseRedirect("/static/version/frontend/index.html"+init_param)

class new_version_restricted(JSONWebTokenAuthMixin, View):
    def get(self, request, id):
        return new_version(request, id)

# Create your views here.
def new_version(request, master_id):
    documento_master = Version.objects.get(pk=master_id)
    v = Version()
    if v.parent:
        v.status = 'master'
    else:
        v.status = 'version'
    v.owner = request.user
    v.parent = documento_master
    v.title = "ramo-%s" % str(conta_rami(documento_master) + 1)
    v.base = documento_master.content
    v.content = documento_master.content
    v.condiv = '["%s"]' % documento_master.owner.username
    v.save()
    return details(request, v.pk)

class lock_restricted(JSONWebTokenAuthMixin, View):
    def get(self, request, id):
        return toggle_lock(request, id, True)

class unlock_restricted(JSONWebTokenAuthMixin, View):
    def get(self, request, id):
        return toggle_lock(request, id, False)

@csrf_exempt
def toggle_lock(request, id, state):
    if v.owner == request.user:
        v = Version.objects.get(pk=master_id)
        v.locked = state
        v.save()
        return JsonResponse({"action": "lock" if state else "unlock", "result": 'ok', "version_id": v.pk})
    else:
        return JsonResponse({"action": "lock" if state else "unlock", "result": "Error: can't lock/unlock. Current version does not belong to current user", "version_id": v.pk}, status=500 )

class conflicts_restricted(JSONWebTokenAuthMixin, View):
    def get(self, request, id):
        return conflicts(request, id)

@csrf_exempt
def conflicts(request, id):
    v = Version.objects.get(pk=id)
    return JsonResponse(getConflicts(v))

class reset_merge_request_restricted(JSONWebTokenAuthMixin, View):
    def get(self, request, id):
        return reset_merge_request(request, id)

@csrf_exempt
def reset_merge_request(request, id ):
    v = Version.objects.get(pk=id)
    if v.status == 'Merge_req':
            v.status = 'Version'
            v.save()
            return JsonResponse({"action":"reset_merge request","result":"ok", "version_id": v.pk })

class merge_request_restricted(JSONWebTokenAuthMixin, View):
    def get(self, request, id):
        return merge_request(request, id)

@csrf_exempt
def merge_request(request, id ):
    v = Version.objects.get(pk=id)
    if not v.parent:
        return JsonResponse({"action": "merge", "result": "Error: This is master version without merge target. Can't create merge request", "version_id": v.pk}, status=500) 
    if v.conflicts == 0:
        patch = dmp.patch_fromText(v.patch)
        res_patch =  dmp.patch_apply(patch, v.parent.content)
        reconciliable =  reduce(lambda a,b: a and b, res_patch[1], True)
        if reconciliable:
            v.status = 'Merge_req'
            v.condiv = ''
            v.save()
            details = versionDetails(v.parent)
            return JsonResponse({"action":"merge request","version_id": v.pk })

    return JsonResponse({"action": "merge", "result":"ko", "error": "the version has conflicts. Can't create merge request", "version_id": v.pk}, status=500)

class merge_restricted(JSONWebTokenAuthMixin, View):
    def get(self, request, id):
        return merge(request, id)

@csrf_exempt
def merge(request, id ):
    v = Version.objects.get(pk=id)
    if not v.parent:
        return JsonResponse({"action": "merge", "result": "Error: This is master version without merge target. Can't merge", "version_id": v.pk}, status=500) 
    if v.parent.owner != request.user:
        return JsonResponse({"action": "merge", "result": "Parent version does not belong to current user. Can't merge", "version_id": v.pk}, status=500) 
    if v.conflicts == 0:
        patch = dmp.patch_fromText(v.patch)
        res_patch =  dmp.patch_apply(patch, v.parent.content)
        reconciliable =  reduce(lambda a,b: a and b, res_patch[1], True)
        if reconciliable:
            v.parent.content = res_patch[0]
            v.parent.save()
            v.patch = "MERGED"
            v.status = 'Merged'
            v.title = v.title + "__merged"
            v.save()
            details = versionDetails(v.parent)
            return JsonResponse({"action": "merge", "result": "ok", "version_id": v.pk, "parent_id": v.parent.pk })

    return JsonResponse({"result":"ko", "error": "the version has conflicts. Can't merge"}, status=500)

'''
def edit(request, id):
    v = Version.objects.get(pk=id)
    return render(request, 'editor.html', {"version": v, "content_html": markdown(v.content)})
'''

def html2pdf (html):
    with open(page_html_ROOT, 'wb') as html_file:
        html_file.write(bytes(html, 'UTF-8'))

    execute ('iconv -f UTF-8 -t ISO-8859-1 -o %s  %s' % (iso_html_ROOT,page_html_ROOT))
    execute ('htmldoc --bodyfont HELVETICA --size A4 --right 26mm --left 26mm --top 20mm --bottom 20mm --fontsize 13 --fontspacing 1.4 --webpage -f %s %s' % ( page_pdf_ROOT, iso_html_ROOT))
    execute ('rm %s  %s' % (iso_html_ROOT, page_html_ROOT))

# not supported at the moment
# @csrf_exempt
# def docx(request, id):
#     return download(request, 'docx', id)

# supported by javascrtipt module at the moment   
# @csrf_exempt
# def pdf(request, id):
#     return download(request, 'pdf', id)

class odt_restricted(JSONWebTokenAuthMixin, View):
    def get(self, request, id):
        return odt(request, id)

@csrf_exempt
def odt(request, id):
    return download(request, 'odt', id)

class rebase_restricted(JSONWebTokenAuthMixin, View):
    def post(self, request):
        return rebase(request)

@csrf_exempt
def rebase(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        postData = json.loads(body)
        v_current = Version.objects.get(pk=postData["pk"])
        v = Version()
        v.title = v_current.title + "__reconciled"
        v.parent = v_current.parent
        v.owner = request.user
        v.base = postData["new_base"]
        v.content = postData["new_content"]
        check = getConflicts(v)
        if check["conflicts"] == 0:
            v.status = 'Reconciled'
            v.conflicts = 0
            v.save()
            return JsonResponse({"action": "rebase", "result":"ok", "version_id": v.pk})
        else:
            return JsonResponse({"action": "rebase", "result":"Error: can't rebase. Content has merge conflicts with parent", "version_id": v_current.pk}, status=500)
    else:
        return JsonResponse({"action": "rebase", "result":"Error: wrong http method"}, status=500)


@csrf_exempt
def download(request, format, id):
    
    def zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for filename in files:
                ziph.write(os.path.join(root,filename),os.path.join(root,filename)[len(dezipDir):])

    basedir = tempfile.mkdtemp()

    #FASE0 scompattamento del template odt
    template_file = os.path.join(os.path.dirname(__file__), "template.odt")
    templateDezipDir = os.path.join(basedir, "template_odt")
    with zipfile.ZipFile(template_file, 'r') as zip_ref:
        zip_ref.extractall(templateDezipDir)

    #FASE1 scrittura su disco file MD
    md_file_path = os.path.join(basedir, "input.md")
    v = Version.objects.get(pk=id)
    with open(md_file_path,"w") as mdfile:
        mdfile.write(v.content)
    out_file_path_tmp = os.path.join(basedir, "output_tmp." + format)

    #FASE2 generazione del file odt del contenuto corrente
    #pypandoc.convert_text(v.content, format, format='commonmark', outputfile=out_file_path) #
    pypandoc.convert_file(md_file_path, format, outputfile=out_file_path_tmp)

    dezipDir = os.path.join(basedir, "raw_odt")
    with zipfile.ZipFile(out_file_path_tmp, 'r') as zip_ref:
        zip_ref.extractall(dezipDir)

    #FASE3 sostituzione contenuto corrente nella struttura template odt scompattato
    #os.remove(os.path.join(templateDezipDir,"content.xml"))
    copyfile(os.path.join(dezipDir,"content.xml"), os.path.join(templateDezipDir,"content.xml"))
    out_file_path = os.path.join(basedir, "output." + format)
    dezipDir = templateDezipDir

    if v.parent and format == 'odt':

        #FASE4 creazione directory Versions dentro directory zippata
        dezipVersionDir = os.path.join(dezipDir, "Versions")
        os.mkdir(dezipVersionDir)
        #FASE5 scrittura su disco del contenuto master e generazione del file master odt
        master_md = os.path.join(basedir, "parent.md")
        with open(master_md,"w") as mdfile:
            mdfile.write(v.parent.content)
        master_file = os.path.join(dezipVersionDir, "Version1")
        pypandoc.convert_file(master_md, format, outputfile=master_file)
        #pypandoc.convert_text(v.parent.content, format, format='commonmark', outputfile=master_file) # convert_text non converte bene le tables markadown
        #FASE6 creazione file versionsList.xml
        template = """<?xml version="1.0" encoding="UTF-8"?><VL:version-list xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:VL="http://openoffice.org/2001/versions-list"><VL:version-entry VL:title="Version1" VL:comment="%s" VL:creator="user" dc:date-time="%s"/></VL:version-list>"""
        versionListTxt = template % ("user", v.parent.modify_date.strftime("%Y-%m-%dT%H:%M:%S")) #2020-09-28T08:58:50
        versionListFilePath = os.path.join(dezipDir, "VersionList.xml")
        with open(versionListFilePath,'w') as versionListFile:
            versionListFile.write(versionListTxt)
        #FASE7 MODIFICA META-INF/manifest.xml
        manifestFilePath = os.path.join(dezipDir, "META-INF", "manifest.xml")
        with open(manifestFilePath,'r') as manifestFile:
            manifestFileContent = manifestFile.read()
        versionsMetafileEdit = """   <manifest:file-entry manifest:full-path="VersionList.xml" manifest:media-type=""/>\n"""
        versionsMetafileEdit += """   <manifest:file-entry manifest:full-path="Versions/Version1" manifest:media-type=""/>\n"""
        manifestFileNewContent = manifestFileContent[:-20]+versionsMetafileEdit+manifestFileContent[-20:]
        os.remove(manifestFilePath)
        with open(manifestFilePath,'w') as manifestFile:
            manifestFile.write(manifestFileNewContent)

    #FASE9 creazione nuovo odt da compressione directory precedenti
    #os.remove(out_file_path)
    out_file = zipfile.ZipFile(out_file_path, 'w', zipfile.ZIP_STORED)
    zipdir(dezipDir, out_file)
    out_file.close()

    stream = open(out_file_path, "rb")
    response = HttpResponse(stream, content_type="application/vnd.openxmlformats") #application/pdf
    response['Content-Disposition'] = 'attachment; filename=%s.%s' % (v.title,format)
    return response

class upload_restricted(JSONWebTokenAuthMixin, View):
    def post(self, request, id):
        return upload(request, id)

@csrf_exempt
def upload(request, id):
    if request.method == 'POST':
        upload = request.FILES['uploaded_content']
        v = Version()
        v.title = upload.name
        v.owner = request.user
        v.status = 'Master'
        if id:
            pv = Version.objects.get(pk=id)
            v.parent = pv
            v.base = pv.content
            v.status = 'Version'
            #if v.owner != request.user:
            #    return JsonResponse({"action": "rebase", "result":"Error: Can't upload. Current version does not belong to current user", "version_id": v_current.pk}, status=500)

        if upload.content_type in ("text/markdown", "text/plain"):
            md_text = upload.read().decode()
            #md_text = re.sub("(.)\n", "\1 ", md_text)
            #md_text = re.sub("\n", "\n\n", md_text)
            #print ("MDTEXT", md_text)
            v.content = md_text
        elif upload.content_type in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/vnd.oasis.opendocument.text"):
            if upload.content_type == "application/vnd.oasis.opendocument.text":
                ext = 'odt'
            else:
                ext = 'docx'
            basedir = tempfile.mkdtemp()
            md_file = os.path.join(basedir, "input.md")
            in_file = os.path.join(basedir, "output." + ext)
            with open(in_file, 'wb') as dest:
                dest.write(upload.read())
            output = pypandoc.convert(in_file, "md", format=ext, outputfile=md_file)
            with open(md_file,"r") as md:
                v.content = md.read()
        else:
            return JsonResponse({"action": "delete", "result":"Error: Can't upload. document type is not supported"}, status=500)
        v.save()
        return JsonResponse({"action": "upload", "result": "ok", "version_id":v.pk})

def shared_with(v,user):
    json_condiv = v.condiv if v.condiv else "[]"

    if not user:
        return json.loads(json_condiv) != []

    if "@public" in json.loads(json_condiv):
        return True

    user_groups = [tag.name for tag in user.groups.all()]
    group_tags = [tag[1:] for tag in json.loads(json_condiv) if tag[0] == "@" and tag[1:] in user_groups ]
    if group_tags:
        return True
    
    users_tags = [tag for tag in json.loads(json_condiv) if tag[0] != "@" ]
    if user.username in users_tags:
        return True
    
    return False


class details_restricted(JSONWebTokenAuthMixin, View):
    def get(self, request, id):
        return details(request, id)

@csrf_exempt
def details(request, id):
    v = Version.objects.filter(pk=id).first()
    if not v:
        return JsonResponse({"action": "details", "result":"Error: unkwown version. The requested version id is unkwown", "version_id": id}, status=500)
    sharedWithCurrentUser = shared_with(v,request.user)
    if v.owner != request.user and not sharedWithCurrentUser:
        return JsonResponse({"action": "details", "result":"Error: Can't access version. The requested version does not belong to current user and it is not shared", "version_id": v.pk}, status=500)
    det = versionDetails(v)
    det["sharedWithCurrentUser"] = sharedWithCurrentUser
    det["canEdit"] = v.owner == request.user
    if v.parent:
        det["canMerge"] = v.parent.owner == request.user
    else:
        det["canMerge"] = False
    det["ownername"] = v.owner.username
    det["username"] = request.user.username
    return JsonResponse(det)

class delete_restricted(JSONWebTokenAuthMixin, View):
    def get(self, request, id):
        return delete(request, id)

@csrf_exempt
def delete(request, id):
    v = Version.objects.get(pk=id)
    if v.owner != request.user:
        return JsonResponse({"action": "delete", "result":"Error: Can't delete. Current version does not belong to current user", "version_id": v.pk}, status=500)
    deleted = model_to_dict(v)
    v.delete()
    return JsonResponse({"action": "delete", "result": "ok", "deleted_version": deleted })

class vlist_restricted(JSONWebTokenAuthMixin, View):
    def get(self, request, fromId=None):
        return vlist(request, fromId)

@csrf_exempt
def vlist(request, fromId):
    return vtree(request, fromId, asList = True)

def getVersionObject(v):
    return {
        "title": v.title,
        "id": v.pk,
        "status": v.status,
        "path": str(v),
        "parent_name": v.parent.title if v.parent else "",
        "parent_id": v.parent.pk if v.parent else -1,
        "conflicted": v.conflicts > 0,
        "owner": v.owner.username,
        "locked": v.locked,
        "master": False if v.parent else True
    }    

class vtree_restricted(JSONWebTokenAuthMixin, View):
    def get(self, request, fromId=None, asList = False):
        return vtree(request, fromId, asList)

@csrf_exempt
def vtree(request, fromId, asList = False):
    tree = []

    def genealogy(node):
        genealogy = []
        while node.parent:
            genealogy.append[node.parent]
            node = node.parent
        return genealogy

    def allowed(node):
        if q:
            return (node.owner == request.user and q in node.title) or traverse_allowed(node)
        else:
            return  node.owner == request.user or traverse_allowed(node)

    def traverse_allowed(node, allowed_flag=False):
        children = Version.objects.filter(parent__pk=node.pk)
        sharedWithCurrentUser = shared_with(node,request.user)
        if q:
            allowed_flag = allowed_flag or (sharedWithCurrentUser and q in node.title) 
        else:
            allowed_flag = allowed_flag or sharedWithCurrentUser
        if not allowed_flag and children:
            for child in children:
                if q:
                    allowed_flag = allowed(child) or (sharedWithCurrentUser and q in node.title)
                else:
                    allowed_flag = allowed(child) or sharedWithCurrentUser
        return allowed_flag

    def traverse_nodes(node):
        node_content = getVersionObject(node)
        children = Version.objects.filter(parent__pk=node.pk).order_by("title")
        node_content["hasChildren"] = True if children else False
        node_content["sharedWithCurrentUser"] = shared_with(node,request.user)
        node_content["shared"] = shared_with(node,None)
        node_content["text"] = node_content["title"]
        node_content["draggable"] = False
        node_content["droppable"] = False
        node_content["children"] = []

        for child in children:
            if allowed(child):
                if asList:
                    tree.append(traverse_nodes(child))
                else:
                    node_content["children"].append(traverse_nodes(child))
        return node_content
    q = request.GET.get('q', None)
    if fromId and int(fromId) > 0:
        root_nodes = Version.objects.filter(pk=fromId).order_by("title")
    else:
        root_nodes = Version.objects.filter(parent__pk=None).order_by("title")
    for node in root_nodes:
        if allowed(node):
            tree.append(traverse_nodes(node))

    return JsonResponse({"action":"tree", "versions":tree})

class save_restricted(JSONWebTokenAuthMixin, View):
    def post(self, request):
        return save(request)

@csrf_exempt
def save(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        postData = json.loads(body)
        if postData["pk"] > 0:
            v = Version.objects.get(pk=postData["pk"])
            if v.owner != request.user:
                return JsonResponse({ "action":"save", "result":"Error: can't save. Current version does not belong to current user", "version_id": v.pk }, status=500)
        else:
            v = Version()
            v.owner = request.user
        if v.patch == "RECONCILIATED":
            return JsonResponse({ "action":"save", "result":"Error: Reconciliated Versions cannot be modified", "version_id": v.pk }, status=500)
        v.condiv = json.dumps(postData['condiv'])
        v.content = postData['content']
        v.title = postData['title']
        v.save()
        return JsonResponse({"action":"save", "result":"ok", "version_id": v.pk})
    else:
        return JsonResponse({"action":"save", "result":"Error: wrong http method"}, status=500)

class auth_objs_restricted(JSONWebTokenAuthMixin, View):
    def get(self, request):
        return auth_objs(request)

@csrf_exempt
def auth_objs(request):
    u = User.objects.first()
    print ( User.objects.first())
    auth_tags = [ {"ftag": item["username"], "fsearch": "%s %s %s" % (item["username"], item["last_name"], item["first_name"] )} for item in User.objects.all().values() ]
    for item in Group.objects.all().values():
        auth_tags.append({"ftag": "@"+item["name"], "fsearch": "@"+item["name"]})
    print (auth_tags)
    return JsonResponse({"data": auth_tags})
    
