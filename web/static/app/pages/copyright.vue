<template>
  <div>
    <h1><translate>License</translate></h1>
    <p>
      This program is free software: you can redistribute it and/or modify it
      under the terms of the GNU General Public License as published by the Free
      Software Foundation, either version 3 of the License, or (at your option)
      any later version.
    </p>
    <p>
      This program is distributed in the hope that it will be useful, but
      WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
      or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
      for more details.
    </p>
    <p>
      You should have received a copy of the GNU General Public License along
      with this program. If not, see http://www.gnu.org/licenses/.
    </p>

    <h1><translate>Authors</translate></h1>
    <ul>
      <li>Etienne Chové 2009-2010</li>
      <li>Jocelyn Jaubert 2011-2021</li>
      <li>Frédéric Rodrigo 2011-2021</li>
      <li><translate>And contributors</translate></li>
    </ul>
  </div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  created() {
    document.title = "Osmose - " + this.$t("Copyright information");
  },
});
</script>
