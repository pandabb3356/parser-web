const config = {
    proxyTable: {
        '/api': {
            target: 'http://localhost:5300/api',
            changeOrigin: true,
            pathRewrite: {
                '^/api': ''
            }
        },
    }
}

export {config};