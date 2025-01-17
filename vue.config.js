const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')
const CopyWebpackPlugin = require('copy-webpack-plugin')
const path = require('path')
const fs = require('fs')
const dotenv = require('dotenv')
const TerserPlugin = require('terser-webpack-plugin')
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin')

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
      if (err.code !== 'ENOENT') {
        console.error(err)
      }
    }
  };

  load(basePath)
  load(localPath)
}

// NODE_ENVに基づいて環境変数を読み込む
loadEnv(process.env.NODE_ENV)

module.exports = defineConfig({
  pages: {
    index: {
      entry: 'src/main.js',
      title: 'fluxweek - 週次報告システム'
    }
  },
  publicPath: process.env.NODE_ENV === 'production' ? '/' : '/',
  devServer: {
    port: 3000,
  },
  transpileDependencies: ['vuetify'],
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    },
    optimization: {
      usedExports: true,
      sideEffects: false,
      minimize: process.env.NODE_ENV === 'production', // 本番環境でのみミニファイを有効に
      minimizer: [
        new TerserPlugin({
          // Terserの設定（必要に応じてカスタマイズ）
          terserOptions: {
            compress: {
              drop_console: true, // console.logを削除
            },
          },
        }),
        new CssMinimizerPlugin(), // CSSのミニファイ
      ],
    },
    plugins: [
      new webpack.DefinePlugin({
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(process.env.NODE_ENV !== 'production'),
      }),
      new CopyWebpackPlugin({
        patterns: [
          {
            from: path.resolve(__dirname, 'public'),
            to: path.resolve(__dirname, 'dist'),
            globOptions: {
              ignore: [
                '**/index.html',      // index.htmlは別途処理されるため除外
                '**/.*',              // 隠しファイルを除外
              ]
            }
          }
        ]
      })
    ]
  },
  pluginOptions: {
    vuetify: {
      // Vuetifyの設定
    }
  }
});
