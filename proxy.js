'use strict';

const http = require('http');
const httpProxy = require('http-proxy');
const fs = require('fs');
const path = require('path');

const proxy = httpProxy.createProxyServer({});
const PORT = process.env.PROXY_PORT || 8000;
const CONFIG_FILE = process.env.CONFIG_FILE || path.join(__dirname, 'config', 'active_env.json');

// Docker mode: when BLUE_TARGET / GREEN_TARGET are set, route by the active
// environment name to a container hostname. Local mode: route by the active
// port to a localhost process. The same config/active_env.json drives both,
// so `deploy.py` / `rollback.py` flipping the file switches traffic instantly
// in either mode without restarting the proxy.
const BLUE_TARGET = process.env.BLUE_TARGET;
const GREEN_TARGET = process.env.GREEN_TARGET;
const DOCKER_MODE = Boolean(BLUE_TARGET && GREEN_TARGET);

function resolveTarget() {
  let config = { port: 8001, env: 'blue' };
  try {
    config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  } catch (err) {
    console.error('Error reading config, falling back to blue/8001:', err.message);
  }

  if (DOCKER_MODE) {
    return config.env === 'green' ? GREEN_TARGET : BLUE_TARGET;
  }
  return `http://127.0.0.1:${config.port || 8001}`;
}

const server = http.createServer((req, res) => {
  const target = resolveTarget();
  proxy.web(req, res, { target }, () => {
    res.writeHead(502);
    res.end('Bad Gateway: Target application is down.');
  });
});

server.listen(PORT, () => {
  console.log(
    `Reverse proxy listening on port ${PORT} ` +
      `(${DOCKER_MODE ? 'docker mode: blue=' + BLUE_TARGET + ' green=' + GREEN_TARGET : 'local mode: localhost ports'})`
  );
});
