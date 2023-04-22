<script lang="ts">
import Vue from 'vue'

export default {
  methods: {
    confirmeFalsePositive(uuid: string): boolean {
      const message = this.$t(
        `Report the issue as improper.

Only use this if the issue reported by Osmose is in fact not an issue in the OSM data.

Warning: the issue will also no longer be displayed to other contributors. If you are unsure, let this Osmose issue open.

If Osmose reports lots of issues similar to this one and you disagree with this, please fill a Github issue and let us try to fix it.`
      )
      if (confirm(message)) {
        return true
      }
    },
  },
}
</script>
