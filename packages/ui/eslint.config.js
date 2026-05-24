import pluginVue from 'eslint-plugin-vue'
import tseslint from 'typescript-eslint'

export default [
  ...tseslint.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  {
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tseslint.parser,
      },
    },
  },
  {
    rules: {
      // Co* components are intentionally prefixed (Co + noun), not two full words
      'vue/multi-word-component-names': 'off',
      // Optional props in a component library don't need explicit defaults —
      // undefined is the correct implicit default for truly optional props
      'vue/require-default-prop': 'off',
      // We prefer compact inline attribute style for utility components;
      // max-attributes-per-line is a formatting preference, not a correctness rule
      'vue/max-attributes-per-line': 'off',
      // Allow self-closing void elements (<input/>) — Vue templates accept both
      'vue/html-self-closing': 'off',
    },
  },
  { ignores: ['dist/', 'node_modules/'] },
]
