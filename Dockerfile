# Build context is the repo root: server/seed.py loads daily_briefing/app/mock_data.py by a
# path relative to its own file (three levels up), so that relative layout must be preserved
# inside the image alongside webapp/.

FROM node:20-slim AS frontend-build
WORKDIR /app/webapp/frontend
COPY webapp/frontend/package*.json ./
RUN npm ci
COPY webapp/frontend/ ./
RUN npm run build

FROM python:3.12-slim AS backend
RUN pip install --no-cache-dir uv

WORKDIR /app/webapp/backend
COPY webapp/backend/pyproject.toml webapp/backend/uv.lock ./
RUN uv sync --frozen

COPY webapp/backend/server ./server
COPY daily_briefing/app/mock_data.py /app/daily_briefing/app/mock_data.py
COPY --from=frontend-build /app/webapp/frontend/dist ./static

ENV PATH="/app/webapp/backend/.venv/bin:${PATH}"
EXPOSE 8080
CMD ["sh", "-c", "uvicorn server.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
