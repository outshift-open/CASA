#!/bin/sh

AUTH_SRV_PORT=8778

docker build -t casa-auth-temp -f deployments/docker/Dockerfile .
docker run --rm -d --name casa-auth-temp -p ${AUTH_SRV_PORT}:8000 casa-auth-temp

curl --retry-all-errors --max-time 10 --retry 5 --retry-delay 0 --retry-max-time 40 -o openapi.json http://localhost:${AUTH_SRV_PORT}/openapi.json

docker stop casa-auth-temp
# docker run --rm -v $(PWD):/local openapitools/openapi-generator-cli generate -i /local/openapi.json -g python -o /local/sdk/python --additional-properties=packageName=identity_auth_sdk

rm -rvf "sdk/go" 2>&1 || true
# docker run --rm -v $(PWD):/local openapitools/openapi-generator-cli generate -i /local/openapi.json -g go -o /local/sdk/go --additional-properties=packageName=api --git-user-id cisco-eti --git-repo-id identity-auth-server/sdk/go --global-property apiTests=false,modelTests=false
docker run --rm \
  -v "$(PWD):/local" \
  openapitools/openapi-generator-cli generate \
  -i /local/openapi.json \
  -g go \
  -o /local/sdk/go \
  --additional-properties=packageName=api \
  --git-user-id cisco-eti \
  --git-repo-id identity-auth-server/sdk/go \
  --global-property apiTests=false,modelTests=false

docker rmi casa-auth-temp

rm openapi.json
cd sdk/go && go mod tidy
