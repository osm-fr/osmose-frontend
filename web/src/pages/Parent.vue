<script>
import Vue from 'vue'

export default Vue.extend({
  data() {
    return {
      error: false,
    }
  },
  methods: {
    fetchJson(url, callback = () => {}, errorCallback = () => {}) {
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
    fetchJsonProgress(url, callback = () => {}) {
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
    fetchJsonProgressAssign(url, callback = () => {}) {
      this.fetchJsonProgress(url, (response) => {
        Object.assign(this, response)
        callback(response)
      })
    },
    fetchJsonAssign(url, callback = () => {}) {
      this.fetchJson(url, (response) => {
        Object.assign(this, response)
        callback(response)
      })
    },
  },
})
</script>
