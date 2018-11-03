var optimize = false;
var webpack = require('webpack');


module.exports = {
    entry: {
        "static": "./static/webpack.index.js",
        "static/map": "./static/map/webpack.index.js",
    },
    output: {
        path: __dirname,
        filename: "[name]/webpack.bundle-[hash].js"
    },
    devtool: 'source-map',
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
            { test: /\.css$/, use: [
                { loader: "style-loader" },
                { loader: "css-loader" },
                { loader: "sprite-loader", options: { name: "[hash].png", outputPath: "./static/images/", cssImagePath: "/en/images/", padding: 0 } }
            ] },
            { test: /\.png$/, loaders: ["base64-image-loader"] },
            { test: /\.gif$/, loaders: ["base64-image-loader"] },
        ]
    },
    plugins: [
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery",
            Mustache: "mustache",
        }),
        new webpack.LoaderOptionsPlugin({
            minimize: true,
            debug: false
        }),
        new webpack.optimize.UglifyJsPlugin({
            minimize: true,
            output: {
                comments: false
            },
            sourceMap: true
        }),
        function() {
            this.plugin("done", function(stats) {
                require("fs").writeFileSync(
                    __dirname + "/webpack.stats.json",
                    JSON.stringify(stats.toJson().assetsByChunkName));
            });
        }
    ],
};
