# General Knowledge: What is basic dockerfile: and how does it work in Docker?

## Context
Technical knowledge and best practices.

## Response
FROM python:3.9-slim WORKDIR /app COPY requirements.txt . RUN pip install -r requirements.txt COPY . . EXPOSE 8000 CMD ["python", "app.py"]

## Metadata
- **Domain**: general
- **Source**: unknown
- **Quality Score**: 0.50
- **Created**: 2025-10-28T06:31:09.492473