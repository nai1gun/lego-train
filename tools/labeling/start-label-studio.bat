@echo off
REM Load Label Studio environment variables from .env.label-studio
setlocal
set LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
REM Document root for local file serving — use project root
set LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=%~dp0..\..

echo Setting Label Studio environment variables...
echo LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=%LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED%
echo LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=%LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT%

REM Start Label Studio with these environment variables
label-studio
