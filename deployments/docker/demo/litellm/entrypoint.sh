#!/bin/sh
# shellcheck disable=SC2016 # envsubst requires single quotes not double quotes

envsubst '$OPENAI_GPT4o_API_BASE_URL $OPENAI_GPT4o_API_JWT_TOKEN' < /src/llm/config.env.yaml > /src/llm/config.yaml
exec "$@"
