<template>
  <div>
    <h1><translate>Bug tracker</translate></h1>
    <p>
      <translate-slot>
        <span>
          Bug should be reported on {osmose-frontend} for issues around the
          website, or on {osmose-backend} for issues on the reported issues on
          OSM data, or for suggestion about analyses.
        </span>
        <template v-slot:osmose-frontend>
          <a href="https://github.com/osm-fr/osmose-frontend/issues">
            osmose-frontend
          </a>
        </template>
        <template v-slot:osmose-backend>
          <a href="https://github.com/osm-fr/osmose-backend/issues">
            osmose-backend
          </a>
        </template>
      </translate-slot>
    </p>

    <h1><translate>Providing patches</translate></h1>
    <p>
      <translate>
        Patches can be provided via merge requests on Github. This is the
        preferred way of handling patches.
      </translate>
    </p>
    <ul>
      <li>
        <a href="https://github.com/osm-fr/osmose-backend">backend</a>
      </li>
      <li>
        <a href="https://github.com/osm-fr/osmose-frontend">frontend</a>
      </li>
    </ul>

    <h1><translate>Development</translate></h1>
    <p>
      <translate-slot>
        <span>
          Development of Osmose is made as free software by {volunteers}.
        </span>
        <template v-slot:volunteers>
          <a href="../copyright">volunteers</a>
        </template>
      </translate-slot>
    </p>
    <p>
      <translate>
        Adding new functionality of "Osmose Editor", initial support of mobile
        device and improvement of documentation was funded by region of
        Aquitaine, France; part of the OpenAquiMap project leading by "Les
        Petits Débrouillards d'Aquitaine".
      </translate>
    </p>
    <p>
      <translate>
        The servers analysing data are provided by OpenStreetMap-France and some
        others by contributors around the world. The servers for north-america
        and other areas are funded by Mapbox.
      </translate>
    </p>
    <img
      src="images/logo-aquitaine.png"
      alt="Logo of region of Aquitaine"
      width="340"
      height="100"
    />
    <img
      src="images/logo-mapbox.png"
      alt="Logo of Mapbox"
      width="340"
      height="100"
    />

    <h1><translate>Contacting maintainers</translate></h1>
    <p>
      <translate-slot>
        <span>We can be contacted through a direct email to {email}.</span>
        <template v-slot:email>
          <a href="mailto:osmose-contact@openstreetmap.fr">
            osmose-contact@openstreetmap.fr
          </a>
        </template>
      </translate-slot>
    </p>
    <p>
      <translate-slot>
        <span>Keep in touch by watching at {osmose_qa} on twitter.</span>
        <template v-slot:osmose_qa>
          <a href="https://twitter.com/osmose_qa">@osmose_qa</a>
        </template>
      </translate-slot>
    </p>
  </div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  mounted() {
    document.title = "Osmose - " + this.$t("Contact");
  },
});
</script>
