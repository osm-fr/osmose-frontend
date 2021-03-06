<script>
import Vue from "vue";

export default Vue.extend({
  data() {
    return {
      error: false,
    };
  },
  methods: {
    fetchJson(url, callback = (response) => {}, errorCallback = (error) => {}) {
      fetch(url, {
        headers: new Headers({
          "Accept-Language": this.$route.params.lang,
        }),
      })
        .then((response) => {
          if (!response.ok) {
            Promise.reject(response);
          }
          return response.json();
        })
        .then(callback)
        .catch((error) => {
          this.error = error;
          errorCallback(error);
        });
    },
    fetchJsonProgressAssign(url, callback = (response) => {}) {
      this.$refs.topProgress.start();
      this.fetchJson(
        url,
        (response) => {
          this.$refs.topProgress.done();
          Object.assign(this, response);
          callback(response);
        },
        (error) => {
          this.$refs.topProgress.done();
        }
      );
    },
  },
});
</script>
