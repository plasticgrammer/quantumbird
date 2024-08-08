const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')

module.exports = defineConfig({
  pages: {
    index: {
      entry: 'src/main.js',
      title: 'sixweeks'
    }
  },
  publicPath: process.env.NODE_ENV === 'production'
    ? '/quantumbird/'  // GitHub リポジトリ名を入力してください
    : '/',
  devServer: {
    port: 3000,
  },
  transpileDependencies: true,
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(process.env.NODE_ENV !== 'production')
      })
    ]
  },
  pluginOptions: {
    vuetify: {
      // https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
    }
  }
})
