@echo off
REM Rolls the deployment back to the previous revision.
kubectl -n student rollout undo deployment/student-app
kubectl -n student rollout status deployment/student-app --timeout=120s
kubectl -n student get deployment student-app -o jsonpath="{.spec.template.spec.containers[0].image}"
echo.
