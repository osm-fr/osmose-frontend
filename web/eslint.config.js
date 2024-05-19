const pluginVue = require('eslint-plugin-vue');
const eslint = require('@eslint/js');
const tseslint = require('typescript-eslint');
const eslintConfigPrettier = require('eslint-config-prettier');
const eslintImportX = require('eslint-plugin-import-x');

module.exports = tseslint.config(
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    languageOptions: {
      globals: {
        API_URL: "readonly"
      }
    },
  },
  {
    plugins: {
      'typescript-eslint': tseslint.plugin,
      'import-x': eslintImportX,
    },
    languageOptions: {
      parserOptions: {
        parser: tseslint.parser,
        extraFileExtensions: ['.vue'],
        sourceType: 'module',
      },
    },
    rules: {
      '@typescript-eslint/no-unused-vars': 'off',
      '@typescript-eslint/ban-types': 'off',
      'vue/multi-word-component-names': 'off',
      'vue/require-explicit-emits': 'off',
      'vue/no-deprecated-slot-scope-attribute': 'off',
      'vue/valid-template-root': 'off',
      'vue/no-deprecated-filter': 'off',
      'vue/require-slots-as-functions': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
      'import-x/order': [
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
  },
  eslintConfigPrettier
);
