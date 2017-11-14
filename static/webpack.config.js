var optimize = false;
var webpack = require('webpack');


module.exports = {
    entry: "./webpack.index.js",
    output: {
        path: __dirname,
        filename: "webpack.bundle.js"
    },
    devtool: 'source-map',
    module: {
        rules: [
            { test: /\.css$/, loaders: ["style-loader", "css-loader"] },
            { test: /\.png$/, loaders: ["base64-image-loader"] },
            { test: /\.gif$/, loaders: ["base64-image-loader"] },
        ]
    },
    plugins: [
        new webpack.optimize.UglifyJsPlugin({ minimize: true, sourceMap: true }),
    ],
};
