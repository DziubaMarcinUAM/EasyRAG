@echo off
REM Builds the Chroma vector database from documents in the ./docs directory.
docker compose run --rm easyrag python init_db.py
