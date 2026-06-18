@echo off

REM   run_tests.bat              
REM   run_tests.bat --all       
REM   run_tests.bat --fast       
REM   run_tests.bat --indices   
REM   run_tests.bat --file media/test_image_resize.py
REM   run_tests.bat -k resize    


setlocal
cd /d "%~dp0"
cd
set PYTEST=python -m pytest
set IGNORE=^
  --ignore=tests/media/test_image_ocr.py ^
  --ignore=tests/media/test_audio_extract.py ^
  --ignore=tests/media/test_video_extract.py ^
  --ignore=tests/media/test_video_transcode.py

if "%1"=="--all" (
  %PYTEST% tests/ -v --tb=short
) else if "%1"=="--fast" (
  %PYTEST% tests/readers tests/transforms tests/writers tests/utils tests/test_executor.py tests/test_dispatcher.py -v --tb=short
) else if "%1"=="--indices" (
  %PYTEST% tests/droneIndices tests/S2Indices -v --tb=short
) else if "%1"=="" (
  %PYTEST% tests/ -v --tb=short %IGNORE%
) else (
  %PYTEST% tests/ %* --tb=short %IGNORE%
)

exit /b %ERRORLEVEL%
