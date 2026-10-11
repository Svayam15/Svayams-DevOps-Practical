@echo off
REM Usage: scripts\rolling-update-demo.bat <new-version>      e.g. 1.0.7
REM Shows a zero-downtime rolling update. Run `kubectl get pods -n student -w` in another window.
set V=%1
if "%V%"=="" (echo Usage: %0 ^<version^> & exit /b 1)
kubectl -n student set image deployment/student-app student-app=student-app:%V%
kubectl -n student rollout status deployment/student-app --timeout=120s
kubectl -n student rollout history deployment/student-app
