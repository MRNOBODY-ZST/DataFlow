@echo off
cd /d E:\pycode\datasourceminioProject

REM 设置代理
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890

REM 启动 uvicorn
call E:\anaconda\envs\datasource\Scripts\uvicorn.exe main:app --host 0.0.0.0 --port 8000 --reload

pause

