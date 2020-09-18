from django.contrib import admin
from .models import Version
from django import forms
from markymark.widgets import MarkdownTextarea
from markymark.renderer import render_markdown

import sys
import diff_match_patch as dmp_module
from markymark.fields import MarkdownField

dmp = dmp_module.diff_match_patch()

class VersionForm(forms.ModelForm):

    #parent_title = forms.CharField(required=False, initial=parent_title, widget=forms.TextInput(attrs={"style": "width: 600px", "readonly": True}))
    title = forms.CharField(required=True, widget=forms.TextInput(attrs={"style": "width: 600px"}))
    content = forms.CharField(required=False, widget=MarkdownTextarea( attrs={'rows':'20', 'cols': '160', "readonly": True}))
    modify_date = forms.DateField(required=False, input_formats=['%Y-%m-%d','%d/%m/%Y'])
    base = forms.CharField(required=False, widget=forms.HiddenInput())
    patch = forms.CharField(required=False, widget=forms.HiddenInput())
    id = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta(object):
        model = Version
        fields = ( 'parent', 'id', 'base', 'title',  'content', 'patch', )
        readonly_fields = ('modify_date',)
        exclude = ('', )

    def init__(self, *args, **kwargs):
        instance = kwargs.pop('instance', None)
        if instance:
            self.parent_title = instance.parent.title if instance.parent else ""
        super(VersionForm, self).__init__(*args, **kwargs)

@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):

    #fields = ('title', 'content', 'patch', 'pk')
    readonly_fields = ('modify_date',) #, 'rendered_content'
    form = VersionForm
    change_form_template = 'admin/documenti-change_form.html'

    def rendered_content(self, obj):
        return render_markdown(obj.content)
    rendered_content.allow_tags=False

#admin.site.register(Version)