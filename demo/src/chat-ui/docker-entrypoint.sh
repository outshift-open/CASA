#!/bin/sh
set -e

cat > /usr/share/nginx/html/config.js <<EOF
window.__ENV__ = {
  AGENT_URL: "${AGENT_URL:-/safe-agent}"
};
EOF

exec nginx -g "daemon off;"
