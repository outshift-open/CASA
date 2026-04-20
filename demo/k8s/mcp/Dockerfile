FROM python:3.14@sha256:7aea6827c8787754f99339ffed8cfc41fb09421f9c7d0e77a198b08422a3455e

WORKDIR /app

RUN pip install uv

COPY . .
RUN uv pip install --system -r requirements.txt

EXPOSE 3000

CMD ["python", "main.py"]
