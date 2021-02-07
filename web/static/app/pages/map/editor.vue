<template>
  <div id="editorTpl" style="display: none">
    <template v-pre>{{={% %}=}}</template>
    <h1><translate>Tags Editor</translate></h1>
    <form>
      {%#elems%}
      <a target="_blank" :href="main_website + '{%type%}/{%id%}'">
        {%type%} {%id%}
      </a>
      <div
        class="tags"
        data-type="{%type%}"
        data-id="{%id%}"
        data-version="{%version%}"
      >
        <div class="del"></div>
        <div class="same"></div>
        <div class="mod"></div>
        <div class="add"></div>
      </div>
      {%/elems%}
      <br />
      <div id="buttons">
        <input
          type="button"
          id="cancel"
          class="btn btn-secondary"
          :value="$t('Cancel')"
        />
        <input
          type="button"
          id="validate"
          class="btn btn-primary"
          :value="$t('Done')"
        />
      </div>
    </form>
  </div>
</template>
