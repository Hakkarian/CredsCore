FROM python:3.11-slim
WORKDIR /app
COPY policy/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared/credscore_shared /app/shared/credscore_shared
COPY shared/pyproject.toml /app/shared/pyproject.toml
RUN pip install --no-cache-dir -e /app/shared
COPY policy/app/ ./app/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]