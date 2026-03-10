FROM python:3.12-slim

WORKDIR /app

RUN pip install uv

COPY . .
RUN uv pip install --system -r requirements.txt

EXPOSE 3000

CMD ["python", "main.py"]
