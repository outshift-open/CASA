FROM python:3.13-slim

WORKDIR /src

RUN apt update && apt install -y gettext

RUN pip install uv

COPY pyproject.toml LICENSE README.md ./
COPY ./src ./src
COPY ./sdk ./sdk
COPY ./demo/workshop/requirements.txt .
COPY ./demo/workshop/llm ./llm
COPY ./deployments/docker/demo/litellm/entrypoint.sh .
COPY pyproject.toml .

RUN uv pip install --system .
RUN uv pip install --system -r ./requirements.txt

WORKDIR /src/llm

RUN cp .env.sample .env
RUN cp config.yaml.sample config.env.yaml

RUN chmod +x ../entrypoint.sh

EXPOSE 4000

ENTRYPOINT ["../entrypoint.sh"]
CMD ["litellm", "--config", "config.yaml"]
