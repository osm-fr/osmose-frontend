<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  data(): {
    error?: string
  } {
    return {
      error: undefined,
    }
  },

  methods: {
    fetchJson(
      url: string,
      callback = (json: Object) => {},
      errorCallback = (error) => {}
    ) {
      fetch(url, {
        headers: new Headers({
          'Accept-Language': this.$route.params.lang,
        }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(response.status + ' ' + response.statusText)
          }
          return response.json()
        })
        .then(callback)
        .catch((error) => {
          this.error = error
          errorCallback(error)
        })
    },

    fetchJsonProgress(url, callback = (response: Object) => {}) {
      this.$refs.topProgress.start()
      this.fetchJson(
        url,
        (response) => {
          this.$refs.topProgress.done()
          callback(response)
        },
        () => {
          this.$refs.topProgress.done()
        }
      )
    },

    fetchJsonProgressAssign(url, callback = (response: Object) => {}) {
      this.fetchJsonProgress(url, (response) => {
        Object.assign(this, response)
        callback(response)
      })
    },

    fetchJsonAssign(url, callback = (response: Object) => {}) {
      this.fetchJson(url, (response) => {
        Object.assign(this, response)
        callback(response)
      })
    },
  },
})
</script>
