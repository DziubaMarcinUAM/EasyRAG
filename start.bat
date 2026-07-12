@echo off
REM Starts the bot in interactive conversation mode.
docker compose run --rm --service-ports easyrag python app.py
