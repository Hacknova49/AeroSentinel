FROM python:3.12-slim
WORKDIR /app
COPY packages/schemas packages/schemas
COPY python python
RUN pip install --no-cache-dir -e packages/schemas -e python
CMD ["uvicorn", "aerosentinel.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
