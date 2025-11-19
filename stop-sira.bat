@echo off
echo Stopping SIRA...
cd ops\docker
docker compose down
cd ..\..
echo.
echo SIRA stopped.
