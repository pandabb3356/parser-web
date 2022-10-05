const path = require("path");
const CopyPlugin = require('copy-webpack-plugin')


module.exports = {
    lintOnSave: false,
    runtimeCompiler: true,
    configureWebpack: {
        //Necessary to run npm link https://webpack.js.org/configuration/resolve/#resolve-symlinks
        resolve: {
            symlinks: false,
        },
        plugins: [
            new CopyPlugin()
        ]
    },
    chainWebpack: config => {
        config.plugin('copy')
            .tap(args => {
                args[0].push({
                    from: path.resolve(__dirname, 'src/config.js'),
                    to: path.resolve(__dirname, 'dist/config.js'),
                    toType: 'file'
                })
                return args
            })
    },
    transpileDependencies: [
        '@coreui/utils',
        '@coreui/vue',
    ],
    devServer: {
        disableHostCheck: true,
        proxy: {
            '/api': {
                target: 'http://localhost:5300/api',
                changeOrigin: true,
                pathRewrite: {
                    '^/api': ''
                }
            }
        }
    }
}
