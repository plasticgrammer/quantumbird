module.exports = {
    root: true,
    env: {
      node: true,
      browser: true,
      es6: true
    },
    extends: [
      'plugin:vue/vue3-essential',
      'eslint:recommended'
    ],
    parserOptions: {
      parser: '@babel/eslint-parser',
      requireConfigFile: false,
      ecmaVersion: 2021
    },
    rules: {
      'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
      'vue/multi-word-component-names': 'off' // このルールを無効にします
    }
  }