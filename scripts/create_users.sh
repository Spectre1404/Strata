#!/usr/bin/env bash
# Create the six Strata database users with generated passwords and write their URIs into .env.
# Usage: bash scripts/create_users.sh <PROJECT_ID> <CLUSTER_HOST>
set -euo pipefail
PID="$1"
HOST="$2"
ENV_FILE=".env"

for role in researcher auditor strategist grouper worker app; do
  user="strata-$role"
  pass="$(openssl rand -hex 16)"
  atlas dbusers create --username "$user" --password "$pass" --role "$role" --projectId "$PID" >/dev/null
  var="MONGODB_URI_$(echo "$role" | tr '[:lower:]' '[:upper:]')"
  line="$var=mongodb+srv://$user:$pass@$HOST/?appName=Cluster0"
  if grep -q "^$var=" "$ENV_FILE"; then
    sed -i '' "s#^$var=.*#$line#" "$ENV_FILE"
  else
    echo "$line" >> "$ENV_FILE"
  fi
  echo "created $user and set $var"
done
