<template>
  <div :class="`line ${action}`">
    <span v-if="action == 'same'">=</span><span v-if="action == 'del'">-</span
    ><span v-if="action == 'add'">+</span><span v-if="action == 'mod'">~</span
    ><input
      type="text"
      :value="key_value"
      :readonly="action == 'del'"
      @input="split($event.target.value)"
      @keydown.enter="focusNext($event, 1)"
      @keydown.arrow-down="focusNext($event, 1)"
      @keydown.arrow-up="focusNext($event, -1)"
      @keydown.ctrl.backspace="
        if (tag_key != '' || tag_value != '') $emit('delete')
      "
    /><a
      v-if="tag_key != '' || tag_value != ''"
      href="#"
      @click.stop.prevent="$emit('delete')"
      ><template v-if="action == 'del'">↶</template
      ><template v-else>×</template></a
    >
  </div>
</template>

<script lang="ts">
import Vue, { PropType } from 'vue'

export default Vue.extend({
  props: {
    tag_key: {
      type: String,
      required: true,
    },
    tag_value: {
      type: String,
      required: true,
    },
    leading_equal: {
      type: Boolean,
      required: undefined,
    },
    action: {
      type: String as PropType<'same' | 'del' | 'mod' | 'add'>,
      required: true,
    },
  },

  computed: {
    key_value(): string {
      return (
        (this.tag_key || '') +
        (this.leading_equal ? '=' : this.tag_value ? `=${this.tag_value}` : '')
      )
    },
  },

  methods: {
    split(key_value: string): void {
      const index = key_value.indexOf('=')
      const key =
        index >= 0 ? key_value.substring(0, index).trim() : key_value.trim()
      const value = index >= 0 ? key_value.substring(index + 1).trim() : ''

      if (key == '' && value == '') {
        this.$emit('delete')
      } else {
        this.$emit('update_tag_key', key)
        this.$emit('update_tag_value', value)
        this.$emit('update_leading_equal', index == key_value.length - 1)
      }
    },

    focusNext(event: KeyboardEvent, shift: number): void {
      const inputs = Array.from(
        event.target.form.querySelectorAll('input[type="text"]')
      )
      const index = inputs.indexOf(event.target)
      if (index + shift >= 0 && index + shift < inputs.length) {
        inputs[index + shift].focus()
      }
    },
  },
})
</script>

<style scoped>
span {
  display: inline-block;
  background: black;
  font-weight: bold;
  width: 5%;
  text-align: center;
}

.same span {
  color: white;
}
.add,
.add input[type='text'] {
  color: green;
}
.mod,
.mod input[type='text'] {
  color: darkorange;
}
.del,
.del input[type='text'] {
  text-decoration: line-through;
  color: red;
}

input[type='text'] {
  font-family: monospace;
  background: #e7e7e7;
  border: none;
  width: 90%;
  padding-left: 5px;
  margin: 0px;
}
input[type='text']:focus {
  background: #f7f7f7;
}
input[type='text']:focus-visible {
  border: none;
}

a {
  display: inline-block;
  width: 5%;
  text-decoration: none;
  text-align: center;
  border-radius: 50%;
  background: #fbb;
}
</style>
