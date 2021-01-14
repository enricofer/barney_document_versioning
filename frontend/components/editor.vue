<template>
  <section class="section">

      <b-field>
          <b-input v-model="title" expanded :placeholder="$t('Untitled document')" rounded @input="contentChanged()"></b-input>
          <p class="control">
              <b-button v-if="version.status == 'Merge_req'" rounded class="button is-warning">{{ $t('Merging')}}</b-button>
          </p>
          <p class="control">
              <b-button v-if="version.status == 'History'" rounded class="button is-success">{{ $t('Merged')}}</b-button>
          </p>
          <p class="control">
              <b-button v-if="version.status == 'Master'" rounded class="button is-dark">{{ $t('Master')}}</b-button>
          </p>
          <p class="control">
              <b-button v-if="version.conflicts > 0" rounded class="button is-danger">{{ $t('Conflicted')}}</b-button>
          </p>
          <p class="control">
              <b-button v-if="version.status == 'Version'" rounded class="button is-info">{{ $t('Version')}}</b-button>
          </p>
          <p class="control">
              <b-button type="is-primary" rounded :disabled="version.id == -1" @click="permalink()">
                <b-icon
                    icon="link"
                    size="is-small">
                </b-icon>
                <span>{{ $t('Permalink') }}</span>
              </b-button>
          </p>
          <p class="control">
              <b-button rounded class="button is-link is-light">
                <b-icon
                    icon="account"
                    size="is-small">
                </b-icon>
                <span>{{ ownername ? ownername : 'Undefined' }}</span>
              </b-button>
          </p>
      </b-field>
    <b-field grouped>
      <div class="buttons">
          <b-button type="is-info" rounded :disabled="version.id == -1" @click="close()">{{ $t('Close') }}</b-button>
          <b-button type="is-info" v-show="!version.hasChildren" rounded :disabled="!dirty || !title" @click="save()">{{ $t('Save') }}</b-button>
          <b-button type="is-info" rounded :disabled="version.id == -1" @click="newVersion()">{{ $t('New version')}}</b-button>
          <b-button type="is-info" rounded :disabled="version.id == -1" @click="compare()">{{ $t('Compare') }}</b-button>
          <b-button type="is-danger" v-show="!version.hasChildren" rounded :disabled="version.id == -1" @click="confirmDelete()">{{ $t('Delete') }}</b-button>

          <b-dropdown aria-role="list">
            <b-button type="is-info" rounded slot="trigger" slot-scope="{ active }">
                <span>{{ $t('Import') }}</span>
                <b-icon :icon="active ? 'menu-up' : 'menu-down'"></b-icon>
            </b-button>
            <b-dropdown-item :disabled="version.id == -1" aria-role="listitem">
              <b-upload v-model="import_file" @input="importAsFile(false)" type="is-info" class="file-label">
                    <span class="file-label smallitem">{{ $t('as new Version') }}</span>
              </b-upload>
            </b-dropdown-item>
            <b-dropdown-item aria-role="listitem">
              <b-upload v-model="import_file" @input="importAsFile(true)" type="is-info" class="file-label">
                    <span class="file-label smallitem">{{ $t('as new Document') }}</span>
              </b-upload>
            </b-dropdown-item>
          </b-dropdown>

          <b-dropdown aria-role="list">
            <b-button type="is-info" rounded slot="trigger" slot-scope="{ active }">
                <span>{{ $t('Export') }}</span>
                <b-icon :icon="active ? 'menu-up' : 'menu-down'"></b-icon>
            </b-button>
            <b-dropdown-item @click="exportAsMarkdown()" aria-role="listitem">Markdown</b-dropdown-item>
            <b-dropdown-item @click="exportAsPDF()" aria-role="listitem">Pdf (sperimentale)</b-dropdown-item>
            <b-dropdown-item @click="exportAsFile()" aria-role="listitem">Odt</b-dropdown-item>
          </b-dropdown>
          &nbsp;&nbsp;
          <div class="field" v-show="!version.hasChildren">
              <b-switch v-model="autosave" :disabled="version.id == -1 || !!version.hasChildren" type="is-info">{{ $t('Autosave') }}</b-switch>
          </div>
          <div class="field" v-show="!!version.canEdit">
              <b-switch v-model="version.private" v-if="version.status != 'History'" :disabled="version.id == -1" @input="save()" type="is-info">{{ version.private ? $t('Private') : $t('Public') }}</b-switch>
          </div>
      </div>
    </b-field>
    <editor
      :initialValue="editorText"
      :options="editorOptions"
      height="650px"
      initialEditType="wysiwyg"
      previewStyle="vertical"
      placeholder= 'Please enter text.'
      ref="toastuiEditor"
      :language="$t('en-EN')"
      v-show="!showComparePanel && !showReconcilePanel && !version.hasChildren && !!version.canEdit && version.status != 'History'"
    >
    </editor>

    <viewer
      :initialValue="editorText"
      placeholder= 'Please enter text.'
      height="700px"
      ref="toastuiViewer"
      v-if="!showComparePanel && !showReconcilePanel && (!!version.hasChildren || !version.canEdit || version.status == 'History')"
    >
    </viewer>

    <div id="diff_container" v-if="!!showComparePanel">
        <b-field grouped>
          <div class="buttons">
            <b-field v-show="version.conflicts == 0">
                <b-select v-model="againstVersionSelected" @input="againstVersionChanged()" rounded>
                  <option :value="99999999" selected>[BASE MASTER]</option>
                  <option v-for="item in againstVersions" :key="item.id" :value="item.id">
                    {{ item.title }}
                  </option>
                </b-select>
            </b-field>
            <b-button type="is-info" rounded v-if="!!version.canMerge" v-show="version.conflicts == 0"  @click="merge()">{{ $t('Merge version to parent') }}</b-button>
            <b-button type="is-info" rounded v-if="!version.canMerge" v-show="version.conflicts == 0"  @click="mergeRequest()">{{ $t('Create Merge Request') }}</b-button>
            <b-button type="is-info" rounded v-show="version.conflicts > 0"   @click="applyReconcile()">{{ $t('Reconcile conflicts') }}</b-button>
            <b-button type="is-info" rounded v-show="version.conflicts > 0"   @click="vConflicts()">{{ $t('View conflicts') }}</b-button>

            <b-field v-if="!!version.hasMergeReq">
                <b-select v-model="version.mergeReq" @input="moveToMergeRequest()" rounded>
                  <option v-for="item in version.mergeReq" :key="item.id" :value="item.id">
                    {{ item.title }}
                  </option>
                </b-select>
            </b-field>

            <b-button type="is-info" rounded @click="closeCompare()">{{ $t('Close compare panel') }}</b-button>
          </div>
        </b-field>

        <code-diff
          v-if="version.conflicts == 0"
          :old-string="parentText"
          :new-string="currentText"
          :context="10"
          :drawFileList="false"
          outputFormat="side-by-side"
        >
        </code-diff>

        <div v-if="version.conflicts > 0">
          <div class="columns">
            <div class="column">
              <h2>{{ $t('Reconciled Version') }}: ({{version.title}})</h2>
            </div>
            <div class="column">
              <h2>{{ $t('Parent Version with conflicts') }}: ({{version.parentTitle}})</h2>
            </div>
          </div>
          <differ
              :left="reconcileSource"
              :right="reconcileTarget"
              :lefteditable="true"
              :leftcopylinkenabled="false"
              :righteditable="false"
              :rightcopylinkenabled="true"
              ref="differ"
          >
          </differ>
        </div>

    </div>

    <b-modal v-model="deleteConfirmActive" :width="420" scroll="keep">
      <div class="card">
        <header class="card-header">
          <p class="card-header-title">
            {{ $t('Confirm Document delete') }}
          </p>
        </header>

        <div class="card-content">
          <div class="content">
            {{ $t('Do you really want to remove') }}<br/>{{ title }} ?
          </div>
        </div>

        <footer class="card-footer">
          <a href="#" type="is-danger" class="card-footer-item" @click="doDelete()">{{ $t('Delete') }}</a>
          <a href="#" class="card-footer-item" @click="closeConfirm()">{{ $t('Close') }}</a>
        </footer>

      </div>
    </b-modal>

    <b-modal v-model="dirtySaveConfirm" :width="420" scroll="keep">
      <div class="card">
        <header class="card-header">
          <p class="card-header-title">
            {{ $t('Document not saved') }}
          </p>
        </header>

        <div class="card-content">
          <div class="content">
            {{ $t('Current document contains') }}
          </div>
        </div>

        <footer class="card-footer">
          <a href="#" type="is-danger" class="card-footer-item" @click="confirmSave()">Save</a>
          <a href="#" class="card-footer-item" @click="discard()">{{ $t('Discard') }}</a>
          <a href="#" class="card-footer-item" @click="cancel()">{{ $t('Cancel') }}</a>
        </footer>
      </div>
    </b-modal>

    <b-modal v-model="conflictsPanel" :width="920" :height="550" scroll="keep">
      <div class="card">
        <header class="card-header">
          <p class="card-header-title">
            {{ $t('Current conflicts') }}
          </p>
        </header>

        <div class="card-content">
          <b-table paginated per-page="5" :data="conflictsData" :columns="conflictsColumns"></b-table>
        </div>

        <footer class="card-footer">
          <a href="#" class="card-footer-item" @click="conflictsPanel=false">Cancel</a>
        </footer>
      </div>
    </b-modal>

  </section>
</template>

<style scoped>
.smallitem {
  font-size: 0.875rem;
  line-height: 1;
  padding: 0rem 0rem;
}
</style>
<style>
.tui-editor-contents {
  font-size: 16px !important;
}

.tui-editor-contents h6 {
  font-size: 16px !important;
}
.tui-editor-contents h5 {
  font-size: 18px !important;
}
.tui-editor-contents h4 {
  font-size: 20px !important;
}
.tui-editor-contents h3 {
  font-size: 22px !important;
}
.tui-editor-contents h2 {
  font-size: 25px !important;
}
.tui-editor-contents h1 {
  font-size: 28px !important;
}
</style>

<script>
/* eslint-disable */
import Card from '~/components/Card'
import 'codemirror/lib/codemirror.css';
import '@toast-ui/editor/dist/toastui-editor.css';
import { Editor } from '@toast-ui/vue-editor';
import { Viewer } from '@toast-ui/vue-editor';
import '@toast-ui/editor/dist/i18n/it-it.js';
import CodeDiff from 'vue-code-diff';
import differ from '../components/differ';
import VueI18n from 'vue-i18n';
import { jsPDF } from "jspdf";

var html2pdf = require('html2pdf.js')
var toc = require('markdown-toc-unlazy');

export default {
  name: 'HomePage',

  components: {
    Card,
    editor: Editor,
    viewer: Viewer,
    CodeDiff,
    differ,
    VueI18n,
  },

  data() {
    return {
      editorText: "",
      editorOptions: {
        hideModeSwitch: false
      },
      version: {
        id:-1,
        title:undefined,
        hasChildren: false,
        hasMergeReq: false,
        canEdit: true,
        canMerge: false,
        private: true,
        parent: -1,
        base: undefined,
        conflicts: undefined,
        status: undefined,
        ownername: undefined,
      },
      title: "",
      //version_id: -1,
      //parent: -1,
      autosave: false,
      autosaving: false,
      reconciliable: false,
      import_file: null,
      dirty: false,
      deleteConfirmActive: false,
      //hasChildren: false,
      showComparePanel: false,
      showReconcilePanel: false,
      dirtySaveConfirm: false,
      parentText: undefined,
      //base: undefined,
      againstVersions: [],
      againstVersionSelected: undefined,
      opening: false,
      //conflicts: undefined,
      //conflicted: undefined,
      conflictsPanel: false,
      conflictsData: undefined,
      conflictsColumns: undefined,
      reconcileTarget: "target",
      reconcileSource: "source",
      username: undefined,
      ownername: undefined,
      //owner: "",
      //currentUserCanEdit: false,
      //privateVersion: true
    };
  },

  mounted () {
    this.$nuxt.$on('versionOpened', this.openInEditor)
    this.$nuxt.$on('Authenticated', this.authenticated)
    this.$refs.toastuiEditor.$on('change', this.contentChanged)
    this.addEditorTool()
  },

   methods: {

     addEditorTool() {
        console.log (this.$refs.toastuiEditor)
        const component = this.$refs.toastuiEditor
        const editorObj = component.editor
        const toolbar = editorObj.getUI().getToolbar()
        editorObj.eventManager.addEventType('clickCustomButton');
        editorObj.eventManager.listen('clickCustomButton', function() {
          const toc_txt = toc( component.invoke('getMarkdown') ).content
          console.log("getRange", component.invoke('getRange'))
          console.log("editorObj", editorObj)

          component.invoke('insertText', toc_txt)
        });
        toolbar.insertItem(toolbar.getItems().length, {
          type: 'button',
          options: {
            className: 'first',
            event: 'clickCustomButton',
            tooltip: 'TOC',
            text: '', //
            style: 'background: url("https://icons-for-free.com/download-icon-idea-131964784861012300_16.png") !important;  background-position: center !important;background-repeat: no-repeat !important;border-color:#ffffff;'
          }
        });
     },

     toggleCurrentTreeItem(id,state) {
       const elem = document.getElementById("item_"+id.toString()).parentNode
       console.log(elem)
       if (state){
         elem.classList.add('current')
       } else {
         elem.classList.remove('current')
       }
       
     },

     authenticated(currentUser) {
       if (!currentUser) this.close()
       this.username = currentUser
     },

     openInEditor(version) {
       if (this.close()) {
          this.version = version
          this.title = version.title
          this.editorText = version.content.replace('[TOC]', toc( version.content ).content)
          this.showComparePanel = false
          this.$refs.toastuiEditor.invoke('setMarkdown', this.editorText) 
          this.$refs.toastuiEditor.invoke('scrollTop',0)
          this.ownername = version.ownername
          if (version.status == "Reconciliated" || this.version.parent < 0) {
            this.reconciliable = false
          } else {
            this.reconciliable = true
          }
          this.dirty = false
          this.opening = true
       }
     },

     close() {
       console.log("close")
       if (!this.dirty) {
          this.$refs.toastuiEditor.invoke('setMarkdown', "") 
          this.dirtySaveConfirm = false
          //if (this.version.id) this.toggleCurrentTreeItem(this.version.id,false)
          this.version = {
              id:-1,
              title:undefined,
              hasChildren: false,
              hasMergeReq: false,
              canEdit: true,
              canMerge: false,
              private: true,
              parent: -1,
              base: undefined,
              conflicts: undefined,
              ownername: undefined,
              status: undefined,
          }
          parentText: undefined,
          this.ownername = undefined
          this.title = ""
          //this.version_id = -1
          this.editorText = ""
          this.showComparePanel = false
          this.autosave = false
          this.reconciliable = false
          //this.hasChildren = false
          self.$nuxt.$emit('refreshTree')
          return true
       } else {
          this.dirtySaveConfirm = true
          return false
       }
     },

     cancel() {
       this.dirtySaveConfirm = false
     },

     discard() {
       this.dirty = false
       this.close()
     },

     confirmSave() {
       this.save()
       this.dirty = false
       this.close()
     },

     contentChanged(content) {
       if (this.opening) {
         this.opening = false
         return
       }
       if (this.title == "") return
       console.log("changed", this.dirty)
       this.dirty = true
       if (this.autosave && ! this.autosaving) {
          this.autosaving = true
          setTimeout( this.save, 30000 );
       }
     },

     async newVersion() {
       this.save()
       await this.$axios.$get('/version/new/' + this.version.id.toString() + "/").then(res => {
          self.$nuxt.$emit('refreshTree', res.id)
          //self.$nuxt.$emit('openVersion', res.id)
          this.openInEditor(res)
       });
     },

     async merge() {
       if (this.version.conflicts == 0) {
         await this.$axios.$get('/version/merge/' + this.version.id.toString() + "/").then(res => {
           self.$nuxt.$emit('openVersion', this.version.parent)
         })
       }
     },

     async mergeRequest() {
       if (this.version.conflicts == 0) {
         await this.$axios.$get('/version/mergereq/' + this.version.id.toString() + "/").then(res => {
           this.version.status = "Merge_req"
           this.$nuxt.$emit('refreshTree', res.id)
         })
       }
     },

     async applyReconcile() {
        const differ = this.$refs.differ.editor.getEditors()
        const payload = {
          pk: this.version.id,
          new_base: differ.right.getValue(),
          new_content: differ.left.getValue()
        }
        await this.$axios.$post('/version/rebase/', payload).then(res => { //await
            self.$nuxt.$emit('refreshTree', res.version_id)
            self.$nuxt.$emit('openVersion', res.version_id)
            this.showComparePanel = false
            this.showReconcilePanel = false
        });
     },

     closeReconcile() {
            this.showReconcilePanel = false
            this.showComparePanel = false
     },
    
     async vConflicts () {
        this.conflictsColumns = [
          { field: 'id', label: '#', width: '10' },
          { field: 'after', label: this.$t('after:'), width: '100' },
          { field: 'delete', label: this.$t('delete:'), width: '100' },
          { field: 'add', label: this.$t('add:'), width: '100' },
          { field: 'before', label: this.$t('before:'), width: '100' }
        ]
        this.conflictsPanel = true
        /*
        this.$axios.$get('/version/details/' + this.parent.toString() + "/").then(res_det => {
            this.parentText = res_det.content

            this.showComparePanel = false
            this.showConflictsPanel = true
        });
        */
     },
  

     async importAsFile(asDocument) {
        console.log(this.import_file, this.import_file.type)
        this.showComparePanel = false
        var formData = new FormData();
        formData.append("uploaded_content", this.import_file);
        const file_comp = this.import_file.name.split(".")
        const extension = file_comp[file_comp.length - 1]

        /*if ( extension.toUpperCase() == 'MD' || this.import_file.type == "text/markdown") {
          const reader = new FileReader();
          reader.onload = e =>  {
              const text = e.target.result
              if (asDocument) {
                this.save()
                  this.$axios.$get('/version/new/' + this.version.id.toString() + "/").then(res => {
                    self.$nuxt.$emit('refreshTree', res.id)
                    this.openInEditor(res)
                    this.$refs.toastuiEditor.invoke('setMarkdown', text)
                    this.$refs.toastuiEditor.invoke('scrollTop',0)
                    this.save()
                  });
              } else {
                this.close()
              }
              console.log(text)
              this.title = this.import_file.name
              this.$refs.toastuiEditor.invoke('setMarkdown', text)
              this.$refs.toastuiEditor.invoke('scrollTop',0)
              this.save()
            }
          reader.readAsText(this.import_file); "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/vnd.oasis.opendocument.text"
          } else */
          if (
              this.import_file.type == "text/markdown" ||
              this.import_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" ||
              this.import_file.type == "application/vnd.oasis.opendocument.text"
            ){
              var formData = new FormData();
              formData.append("uploaded_content", this.import_file);
              formData.append("title", this.import_file.name);
              let url_id
              if (this.version.id < 0 || asDocument) {
                url_id = ""
              } else {
                url_id = this.version.id.toString()
              }
              this.$axios.$post('/version/upload/'+url_id+'/', formData, {
                  headers: {
                    'Content-Type': 'multipart/form-data'
                  }
              }).then(res => {
                  this.version.id = res.version_id
                  this.dirty = false
                  this.autosaving = false
                  self.$nuxt.$emit('refreshTree', this.version.id)
                  self.$nuxt.$emit('openVersion', this.version.id)
              });
          }
     },

     exportAsPDF() {
        var opt = {
          margin:       1.5,
          filename:     this.version.title+'.pdf',
          pagebreak:    {mode:['css','legacy']},
          image:        { type: 'jpeg', quality: 0.98 },
          html2canvas:  { scale: 2 },
          jsPDF:        { unit: 'cm', format: 'a4', orientation: 'portrait' }
        };
        const html_head = '<html><head><link href="https://gist.githubusercontent.com/eirikbakke/1059266/raw/d81dba46c76169c2b253de0baed790677883c221/gistfile1.css" rel="stylesheet" type="text/css"/><style type="text/scss>">ul { li { color: black; }}</style></head><body>'
        const html = html_head + this.$refs.toastuiEditor.invoke('getHtml') + '</body></html>'
        var worker = html2pdf().set(opt).from( html ).save();
     },

     async exportAsMarkdown() {
        const url = window.URL.createObjectURL(new Blob([this.$refs.toastuiEditor.invoke('getMarkdown')], { type: 'text/markdown' }),);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', this.version.title+'.md');
        document.body.appendChild(link);
        link.click();
     },

     async exportAsFile() {
        this.save()
        await this.$axios.$get('/version/odt/' + this.version.id.toString() + "/", {responseType: 'blob'}).then(res => {
            console.log("blob", res.data, res)
            const url = window.URL.createObjectURL(new Blob([res]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', this.version.title+'.odt');
            document.body.appendChild(link);
            link.click();
       });
     },

     async save() { //async 
        this.showComparePanel = false
        this.ownername = this.username
        const payload = {
          pk: this.version.id,
          title: this.title,
          content: this.$refs.toastuiEditor.invoke('getMarkdown'),
          private: this.version.private
        }
        await this.$axios.$post('/version/save/', payload).then(res => { //await
            console.log("SAVE.RES",res)
            this.version.id = res.version_id
            self.$nuxt.$emit('refreshTree', res.version_id)
            this.dirty = false
            this.autosaving = false
       });
     },

     async compare() {
        
        await this.$axios.$get('/version/conflicts/' + this.version.id.toString() + "/").then(res_conflicts => {
          this.conflictsDetails = res_conflicts
          this.conflictsData = res_conflicts.failed_patches

          if (res_conflicts.conflicts == 0) {
            this.$axios.$get('/version/list/' + this.version.parent.toString() + "/").then(res_list => {
                this.againstVersions = res_list.versions
                this.againstVersionSelected = 99999999
                this.againstVersionChanged()
            })
          } else {
              this.reconcileSource = this.$refs.toastuiEditor.invoke('getMarkdown') //this.editorText //res_conflicts.source_content
              this.reconcileTarget = res_conflicts.target_content
              this.showComparePanel = true
            }
          })
     },

     async againstVersionChanged() {
        console.log(this.againstVersionSelected)
        this.autosaving = false
        this.currentText = this.$refs.toastuiEditor.invoke('getMarkdown')
        if ( this.againstVersionSelected == 99999999 ) {
                this.parentText = this.version.base
                this.showComparePanel = true
        } else {
            await this.$axios.$get('/version/details/' + this.againstVersionSelected.toString() + "/").then(res_det => {
                this.parentText = res_det.content
                this.showComparePanel = true
            });
        }
     },

    copyToClipboard (str) {
      const el = document.createElement('textarea');
      el.value = str;
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
    },

     permalink () {
       let new_url = window.location.protocol + "//" + window.location.hostname + "/version/" + this.version.id.toString() + "/"
       this.copyToClipboard(new_url)
       this.$buefy.snackbar.open( this.$t('Permanent link to the current document version copied to clipboard') + ": " + new_url)
     },

     closeCompare () {
       this.showComparePanel = false
     },

     confirmDelete () {
       this.deleteConfirmActive = true
     },

     closeConfirm () {
       this.deleteConfirmActive = false
     },

     async doDelete () {
       this.deleteConfirmActive = false
       await this.$axios.$get('/version/delete/' + this.version.id.toString() + "/").then(res => {
          this.dirty = false
          this.close()
       });

     },


   }
}
</script>
