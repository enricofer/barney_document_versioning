from django.db import models
from django.contrib.auth.models import User

from markymark.fields import MarkdownField

import diff_match_patch as dmp_module
import sys
import json
from .conflicts import getConflicts
from functools import reduce

# Create your models here.

dmp = dmp_module.diff_match_patch()

class Version(models.Model):

    VERSION_CHOICES = [
        ('Master', 'Master'),
        ('Version', 'Version'),
        ('Conflicted', 'Conflicted'),
        ('History', 'History'),
        ('Reconciled', 'Reconciled'),
        ('Merged', 'Merged'),
        ('Merqe_req', 'Merge Request'),
    ]

    title = models.CharField(max_length=100)
    parent = models.ForeignKey('Version', on_delete=models.CASCADE, blank=True, null=True)
    base = models.TextField(blank=True, null=True)
    modify_date = models.DateTimeField(auto_now=True,blank=True, null=True)
    patch = models.TextField(blank=True, null=True)
    conflicts = models.IntegerField(default=0)
    status = models.CharField(choices=VERSION_CHOICES, default='Master', max_length=12)
    content = MarkdownField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    locked = models.BooleanField(default=False)
    private = models.BooleanField(default=True)
    condiv = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Version'
        verbose_name_plural = 'Versions'

    def save(self, *args, **kwargs):
        if self.status == 'History':
            return
        if self.status in ('Merged', ):
            self.status = 'History'
            
        if self.parent: 
            if not self.base:
                self.base = self.parent.content
            patch_obj = dmp.patch_make(self.base, self.content)
        else:
            patch_obj = dmp.patch_make("", self.content)
            self.status = 'Master'
        self.patch = dmp.patch_toText(patch_obj)
        super(Version, self).save(*args, **kwargs)

    def __str__(self):
        antenati = ""
        parent = self.parent
        while parent:
            antenati += parent.title + "/"
            parent = parent.parent
        if self.status in ('History', ):
            return antenati + self.title + ":" + self.modify_date.strftime("%Y-%m-%dT%H:%M:%S")
        else:
            return antenati + self.title
