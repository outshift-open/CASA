#!/bin/sh
# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

AUTH_SRV_PORT=8778

docker build -t casa-auth-temp -f deployments/docker/Dockerfile .
docker run --rm -d --name casa-auth-temp -p ${AUTH_SRV_PORT}:8000 casa-auth-temp

curl --retry-all-errors --max-time 10 --retry 5 --retry-delay 0 --retry-max-time 40 -o openapi.json http://localhost:${AUTH_SRV_PORT}/openapi.json

docker stop casa-auth-temp
# docker run --rm -v $(PWD):/local openapitools/openapi-generator-cli generate -i /local/openapi.json -g python -o /local/sdk/python --additional-properties=packageName=identity_auth_sdk

rm -rvf "sdk/go" 2>&1 || true
# docker run --rm -v $(PWD):/local openapitools/openapi-generator-cli generate -i /local/openapi.json -g go -o /local/sdk/go --additional-properties=packageName=api --git-user-id outshift-open --git-repo-id CASA/sdk/go --global-property apiTests=false,modelTests=false
docker run --rm \
    -v "$(PWD):/local" \
    openapitools/openapi-generator-cli generate \
    -i /local/openapi.json \
    -g go \
    -o /local/sdk/go \
    --additional-properties=packageName=api \
    --git-user-id outshift-open \
    --git-repo-id CASA/sdk/go \
    --global-property apiTests=false,modelTests=false

docker rmi casa-auth-temp

rm openapi.json
cd sdk/go && go mod tidy
