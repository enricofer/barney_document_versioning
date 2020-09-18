from django.db import models

from markymark.fields import MarkdownField

#from computedfields.models import ComputedFieldsModel, computed

#from computed_property import ComputedTextField

import diff_match_patch as dmp_module
import sys
import json
from .diff3 import diff3, merge, SEPARATORS
from functools import reduce

# Create your models here.

dmp = dmp_module.diff_match_patch()

class Version(models.Model):
    title = models.CharField(max_length=100)
    parent = models.ForeignKey('Version', on_delete=models.CASCADE, blank=True, null=True)
    base = models.TextField(blank=True, null=True)
    modify_date = models.DateTimeField(auto_now=True,blank=True, null=True)
    patch = models.TextField(blank=True, null=True)
    content = MarkdownField(blank=True, null=True)

    class Meta:
        verbose_name = 'Versions'
        verbose_name_plural = 'Version'

    def save(self, *args, **kwargs):
        conflicted = not reduce(lambda a,b: a and not b in self.content, SEPARATORS, True)
        print ('conflicted:', conflicted, file=sys.stderr)
        if not conflicted:
            if self.parent: 
                patch_obj = dmp.patch_make(self.base, self.content)
            else:
                patch_obj = dmp.patch_make("", self.content)
            print ('patch:',dmp.patch_toText(patch_obj), file=sys.stderr)
            self.patch = dmp.patch_toText(patch_obj)
        else:
            self.patch = "CONFLICTED"
        super(Version, self).save(*args, **kwargs)

    def __str__(self):
        antenati = ""
        parent = self.parent
        while parent:
            antenati += parent.title + "/"
            parent = parent.parent

        return antenati + self.title

"""
    @property
    def calculation():
        patch = dmp.patch_fromText(self.patch)
        if self.parent:
            return dmp.patch_apply(patch, parent.content)[0]
        else:
            return dmp.patch_apply(patch, "")[0]

    def __getattr__(self, name):
        print ('__getattr__:',name, file=sys.stderr)
        if name == "content":
            patch = dmp.patch_fromText(self.patch)
            if self.parent:
                return dmp.patch_apply(patch, parent.content)[0]
            else:
                return dmp.patch_apply(patch, "")[0]
        #super(Version, self).__getattr__(name)

    def __setattr__(self, name, value):
        print ('__setattr__:',name, value, file=sys.stderr)
        if name == "content":
            self.content_txt = value
        super(Version, self).__setattr__(name, value)

    @property
    def contentTTT(self):
        if self.parent:
            patch = dmp.patch_fromText(self.patch)
            return dmp.patch_apply(patch, parent.content)[0]
        else:
            return dmp.patch_apply(patch, "")[0]

    class Meta:
        verbose_name = 'Versions'
        verbose_name_plural = 'Version'

    def init__(self, *args, **kwargs):
        content = kwargs.get('content', {})
        patch_obj = dmp.patch_make("", content)
        self.patch = dmp.patch_toText(patch_obj)
        super(__init__, self).save(*args, **kwargs)

    def new__(self,title):
        new_version = self()
        new_version.parent = self
        new_version.title = title
        patch_obj = dmp.patch_make("", "")
        new_version.patch = dmp.patch_toText(patch_obj)
        new_version.save()
        return new_version
"""