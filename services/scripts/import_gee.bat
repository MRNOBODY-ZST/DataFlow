@echo off
cd /d E:\pycode\datasourceminioProject
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890
call E:\anaconda\envs\datasource\python.exe cli.py --operation import_gee --folder_name test
pause
