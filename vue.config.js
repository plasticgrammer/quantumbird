const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const path = require('path')

module.exports = defineConfig({
  pages: {
    index: {
      entry: 'src/main.js',
      title: 'Fluxweek'
    }
  },
  publicPath: process.env.NODE_ENV === 'production'
    ? '/quantumbird'  // GitHubActions対応時には リポジトリ名を入力してください
    : '/',
  devServer: {
    port: 3000,
  },
  transpileDependencies: ['vuetify'],
  configureWebpack: {
    optimization: {
      usedExports: true,
      sideEffects: true,
    },
    plugins: [
      new webpack.DefinePlugin({
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(process.env.NODE_ENV !== 'production')
      }),
      new CopyWebpackPlugin({
        patterns: [
          {
            from: path.resolve(__dirname, 'public/404.html'),
            to: path.resolve(__dirname, 'dist/404.html')
          }
        ]
      })
    ]
  },
  pluginOptions: {
    vuetify: {
      // https://github.com/vuetifyjs/vuetify-loader/tree/next/packages/vuetify-loader
    }
  }
})
