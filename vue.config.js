const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const path = require('path')
const fs = require('fs')
const dotenv = require('dotenv')

// 環境変数を読み込む関数
function loadEnv(mode) {
  const basePath = path.resolve(__dirname, `.env${mode ? `.${mode}` : ``}`)
  const localPath = `${basePath}.local`

  const load = (envPath) => {
    try {
      const env = dotenv.parse(fs.readFileSync(envPath))
      Object.keys(env).forEach((key) => {
        if (!process.env[key]) {
          process.env[key] = env[key]
        }
      })
      console.log(`Loaded env file: ${envPath}`)
    } catch (err) {
      // ファイルが存在しない場合はスキップ
      if (err.code !== 'ENOENT') {
        console.error(err)
      }
    }
  }

  load(basePath)
  load(localPath)
}

// NODE_ENVに基づいて環境変数を読み込む
loadEnv(process.env.NODE_ENV)

module.exports = defineConfig({
  pages: {
    index: {
      entry: 'src/main.js',
      title: 'Fluxweek'
    }
  },
  publicPath: process.env.NODE_ENV === 'production'
    ? '/quantumbird'
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
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(process.env.NODE_ENV !== 'production'),
        // 環境変数をクライアントサイドで利用可能にする
        //'process.env': JSON.stringify(process.env)
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
  },
  // 環境変数をコンソールに出力（デバッグ用）
  // chainWebpack: config => {
  //   config.plugin('define').tap(args => {
  //     console.log('Current NODE_ENV:', process.env.NODE_ENV)
  //     console.log('Environment Variables:', process.env)
  //     return args
  //   })
  // }
})