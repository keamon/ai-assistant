# Build context is the repo root; the deployable surface is the frontend + backend, which is
# fully self-contained — the backend's mock data lives in server/mock_data.py.

FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS backend
RUN pip install --no-cache-dir uv

WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen

COPY backend/server ./server
COPY --from=frontend-build /app/frontend/dist ./static

ENV PATH="/app/backend/.venv/bin:${PATH}"
EXPOSE 8080
CMD ["sh", "-c", "uvicorn server.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
