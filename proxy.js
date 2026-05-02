const http = require('http');
const httpProxy = require('http-proxy');
const fs = require('fs');
const path = require('path');

const proxy = httpProxy.createProxyServer({});
const PORT = 8000;
const CONFIG_FILE = path.join(__dirname, 'config', 'active_env.json');

const server = http.createServer((req, res) => {
    let targetPort = 8001; // default fallback
    try {
        const configData = fs.readFileSync(CONFIG_FILE, 'utf8');
        const config = JSON.parse(configData);
        if (config && config.port) {
            targetPort = config.port;
        }
    } catch (err) {
        console.error("Error reading config, falling back to 8001", err);
    }
    
    proxy.web(req, res, { target: `http://127.0.0.1:${targetPort}` }, (e) => {
        res.writeHead(502);
        res.end("Bad Gateway: Target application is down.");
    });
});

server.listen(PORT, () => {
    console.log(`Reverse proxy listening on port ${PORT}`);
});
