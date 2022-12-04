<template>
  <router-view />
</template>

<script>
export default {}
</script>

<style>
body {
  text-align: inherit;
}

th {
  text-align: center;
}

a:visited {
  color: #551a8b;
}

.thead-dark a {
  color: lightgray;
}

.thead-dark a:visited {
  color: gray;
}

/* iframe for josm links */
iframe#hiddenIframe {
  display: none;
  position: absolute;
}

th.country {
  height: 15em;
  vertical-align: bottom;
}
th.country .rotate-90 {
  transform: rotate(-90deg);
  max-width: 1.5em;
}
</style>
