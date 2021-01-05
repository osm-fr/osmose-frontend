<template>
  <div>
    <h1>{{ $t("How to help translation") }}</h1>
    <p>
      {{
        $t(
          "Osmose tool is mainly developped by french people, and we aim to add more languages."
        )
      }}
    </p>
    <p>
      {{
        $t(
          "To make Osmose a real multi-lingual tool, we need your help to improve current translations, and add new translations"
        )
      }}
    </p>

    <h2>{{ $t("Pages to translate") }}</h2>
    <h3>{{ $t("Osmose pages") }}</h3>
    <ul>
      <i18n tag="li" path="Translation is done on {Transifex}.">
        <template v-slot:Transifex>
          <a href="http://www.transifex.com/projects/p/osmose/">Transifex</a>
        </template>
      </i18n>
    </ul>
    <div style="transifex-chart">
      <a
        target="_blank"
        style="text-decoration: none; color: black; font-size: 66%"
        href="https://www.transifex.com/projects/p/osmose"
        title="See more information on Transifex.com"
        >{{ $t("Translation progress: osmose") }}</a
      ><br />
      <a target="_blank" href="https://www.transifex.com/projects/p/osmose/"
        ><img
          border="0"
          src="https://www.transifex.com/projects/p/osmose/chart/image_png" /></a
      ><br />
      <a target="_blank" href="https://www.transifex.com/projects/p/osmose/"
        ><img
          border="0"
          src="https://ds0k0en9abmn1.cloudfront.net/static/charts/images/tx-logo-micro.646b0065fce6.png"
      /></a>
    </div>

    <h3>{{ $t("Wiki pages") }}</h3>
    <ul>
      <li>
        <a :href="$t('http://wiki.openstreetmap.org/wiki/Osmose')">{{
          $t("Osmose QA main page")
        }}</a>
      </li>
      <li>
        <a :href="$t('http://wiki.openstreetmap.org/wiki/Osmose/errors')">{{
          $t("Documentation on reported issues")
        }}</a>
      </li>
    </ul>

    <h2>{{ $t("For new language or countries") }}</h2>
    <ul>
      <i18n
        tag="li"
        path="You can create a new language directly on {Transifex}."
      >
        <template v-slot:Transifex>
          <a href="http://www.transifex.com/projects/p/osmose/">Transifex.</a>
        </template>
      </i18n>
      <i18n
        tag="li"
        path="For new countries, we can be contacted through a direct email to {email}."
      >
        <template v-slot:email>
          <a href="mailto:osmose-contact@openstreetmap.fr"
            >osmose-contact@openstreetmap.fr</a
          >
        </template>
      </i18n>
    </ul>

    <h2>{{ $t("Bug tracking system") }}</h2>
    <ul>
      <i18n
        tag="li"
        path="{osmose-frontend} can be used to report any issue with translations."
      >
        <template v-slot:osmose-frontend>
          <a href="https://github.com/osm-fr/osmose-frontend/issues"
            >osmose-frontend</a
          >
        </template>
      </i18n>
    </ul>
  </div>
</template>

<script>
import Vue from "vue";

export default Vue.extend({
  created() {
    document.title = "Osmose - " + this.$t("How to help translation");
  },
});
</script>
