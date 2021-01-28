var webpack = require('webpack');
const TerserPlugin = require('terser-webpack-plugin');
const VueLoaderPlugin = require('vue-loader/lib/plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const HtmlWebpackRootPlugin = require('html-webpack-root-plugin');
const path = require('path');


module.exports = (env, argv) => {
    return {
        entry: {
            "map": "./static/map/webpack.index.js",
            "app": "./static/app/webpack.index.js",
        },
        output: {
            path: path.resolve(__dirname, 'static/dist'),
            filename: "[name]/webpack.bundle-[hash].js",
            publicPath: argv.mode === 'development' ? "/" : "/en/dist/",
        },
        devtool: argv.mode === 'development' ? 'source-map' : void 0,
        resolve: {
            alias: {
                vue: 'vue/dist/vue.js'
            },
        },
        module: {
            rules: [
/*
                {
                    enforce: "pre",
                    test: /\.js$/,
                    exclude: [
                        /node_modules/,
                        /geobuf-.*\.js/,
                        /sorttable\.js/,
                        /webpack.bundle.*\.js/
                    ],
                    loader: 'eslint-loader',
                    options: {
                        cache: true,
                    }
                },
*/
                { test: /\.js$/,
                    exclude: /node_modules/,
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env']
                    }
                },
                {
                    test: /\.vue$/,
                    loader: 'vue-loader',
                    options: {
                        hotReload: argv.mode === 'development'
                    }
                },
                {
                    test: /\.css$/,
                    use: [
                        { loader: "style-loader" },
                        { loader: "css-loader" },
                        { loader: "sprite-loader", options: { name: "[hash].png", outputPath: "images/", cssImagePath: "/en/dist/images/", padding: 0 } }
                    ]
                },
                { test: /\.png$/, loaders: ["base64-image-loader"] },
                { test: /\.gif$/, loaders: ["base64-image-loader"] },
                {
                    test: /\.po$/,
                    type: "json",
                    use: [{
                        loader: "po-loader",
                        options: {
                            format: "mf"
                        }
                    }]
                },
            ]
        },
        optimization: {
            minimizer: [
                new TerserPlugin({
                    parallel: true,
                    terserOptions: {
                        ecma: 6,
                    },
                }),
            ]
        },
        plugins: (function () {
            const plugins = []
            if (argv.mode === 'development') {
                plugins.push(new HtmlWebpackPlugin({
                    title: "app",
                    chunks: ["app"],
                    inject: "body", // Inject all scripts into the body
                    filename: "index.html"
                    }))
                plugins.push(new HtmlWebpackRootPlugin("app"))
            }
            return plugins.concat([
                new webpack.ProvidePlugin({
                    $: "jquery",
                    jQuery: "jquery",
                    Mustache: "mustache",
                }),
                new VueLoaderPlugin(),
                function() {
                    this.plugin("done", function(stats) {
                        require("fs").writeFileSync(
                            __dirname + "/webpack.stats.json",
                            JSON.stringify(stats.toJson().assetsByChunkName));
                    });
                }
            ])
        })(),
        devServer: {
            contentBase: "./static/dist/",
            historyApiFallback: true,
            open: true,
            openPage: "en/",
            compress: true,
            host: "0.0.0.0"
        },
    }
};
