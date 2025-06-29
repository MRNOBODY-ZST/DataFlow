@echo off
cd /d E:\pycode\datasourceminioProject
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890
call E:\anaconda\envs\datasource\Scripts\uvicorn.exe main_v3:app --host 127.0.0.1 --port 8000 --reload --log-level info