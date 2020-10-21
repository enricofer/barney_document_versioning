<template>
  <div id="ace-diffy" ></div>
</template>

<script>
/* eslint-disable */
  import AceDiffy from 'vue-ace-diffy'

  export default {
    extends: AceDiffy,

    props: {
      left: String,
      right: String,
      lefteditable: Boolean,
      leftcopylinkenabled: Boolean,
      righteditable: Boolean,
      rightcopylinkenabled: Boolean
    },

    data() {
      // Default options
      return {
        leftContent: this.left, // Left pane diff text content
        rightContent: this.right, // Right pane diff text content
        editorId: 'ace-diffy', // AceDiffy element ID
        leftEditable: this.lefteditable, // Left pane diff text editable
        leftCopyLinkEnabled: this.leftcopylinkenabled, // Left pane diff text copy
        rightEditable: this.righteditable, // right pane diff text editable
        rightCopyLinkEnabled: this.rightcopylinkenabled // right pane diff text copy
      }
    },
    mounted () {
      console.log("DIFFER", this)
      require('brace/ext/language_tools') // important prerequisite for syntax highlighting
      require('brace/mode/markdown') // change this to any syntax (mode) that will be set
      require('brace/theme/eclipse') // change if you want to use a different theme

      // Initialize a new Ace Diff editor
      this.createEditor({
        mode: 'ace/mode/markdown',
        theme: 'ace/theme/eclipse',
        diffGranularity: 'specific',
      })
    }
  }
</script>

<style>
@import 'ace-diffy/dist/ace-diffy-light.css';

.acediff__wrap {
  width: 100%;
  height: 600px;
  margin: 0px; /*2rem auto;*/
  position: relative;
}
</style>