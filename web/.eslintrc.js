module.exports = {
  root: true,
  env: {
    browser: true,
    node: true,
  },
  parser: 'vue-eslint-parser',
  parserOptions: {
    parser: '@typescript-eslint/parser',
    sourceType: 'module',
  },
  extends: [
    // '@nuxtjs/eslint-config-typescript',
    'plugin:vue/vue3-recommended',
    'plugin:prettier/recommended',
    'plugin:nuxt/recommended',
    'plugin:import/warnings',
    'plugin:import/typescript',
    // Make sure "prettier" is the last element in this list.
    'prettier',
  ],
  plugins: ['prettier', 'import', '@typescript-eslint', 'vue'],
  // add your custom rules here
  rules: {
    'vue/multi-word-component-names': 'off',
    'vue/require-explicit-emits': 'off',
    'vue/no-deprecated-slot-scope-attribute': 'off',
    'import/order': [
      'error',
      {
        alphabetize: { order: 'asc', caseInsensitive: true },
        groups: [
          ['builtin', 'external'],
          'internal',
          ['parent', 'sibling', 'index'],
          'unknown',
        ],
        'newlines-between': 'always',
      },
    ],
    'vue/no-v-for-template-key-on-child': 'off',
    'vue/no-deprecated-dollar-listeners-api': 'off', // Vue3 rule
  },
  settings: {
    'import/internal-regex': '^@/',
    'import/parsers': {
      '@typescript-eslint/parser': ['.ts', '.js', '.vue'],
    },
  },
}
