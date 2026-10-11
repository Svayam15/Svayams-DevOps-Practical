# Runbook: set up and demo, step by step (Windows)

Prerequisites on the machine that runs Jenkins: Python 3.12, Git, Docker Desktop, Minikube,
kubectl, Helm, Trivy. Jenkins must run as a user that can run `docker` and `kubectl`.

## 1. Git and branching (Unit I)

```
git init
git add .
git commit -m "Initial commit: Student Management System"
git branch -M main
git remote add origin https://github.com/<you>/student-management-devops.git
git push -u origin main

git checkout -b develop
git push -u origin develop

git checkout -b feature/add-search
:: ...make a change, then:
git commit -am "feat: add course filter"
git checkout develop
git merge feature/add-search
git push
```
Use pull requests from `feature/*` into `develop`, and `develop` into `main`. Take screenshots.

## 2. Run and test locally

```
python -m pytest -v
docker compose up --build
```
App `localhost:5000` · Prometheus `localhost:9090` · Grafana `localhost:3000` (admin/admin)

## 3. Start Minikube

```
minikube start --driver=docker --cpus=4 --memory=6144
minikube addons enable metrics-server
```
Reduce `--memory` if your laptop is short; 4096 is the realistic minimum with monitoring.

## 4. Jenkins job

1. New Item > **Pipeline** > "Pipeline script from SCM" > Git > your repo URL > branch `main` > script path `Jenkinsfile`.
2. Make sure Jenkins' PATH has `python`, `git`, `docker`, `kubectl`, `minikube`, `trivy`.
3. Optional push: Manage Jenkins > Credentials > add *Username with password* with id `dockerhub-creds`
   (use a Docker Hub **access token**, not your password).
4. *Build with Parameters*. Defaults run everything except Dependency-Check and the Docker Hub push.

Each build produces: JUnit results, `dist/student-app-1.0.<N>.zip`, the Trivy report, and image tags
`student-app:1.0.<N>` + `latest`.

## 5. Use the deployed app

```
kubectl -n student get pods,svc,hpa
minikube service student-app -n student --url
```
Keep that terminal open; it prints the URL.

## 6. Rolling update and rollback (Unit III)

```
kubectl get pods -n student -w                 :: window 1
scripts\rolling-update-demo.bat 1.0.<N>        :: window 2: pods replaced one at a time, no downtime
kubectl -n student rollout history deployment/student-app
scripts\rollback-demo.bat                      :: back to previous revision
```
To show an automatic rollback, make a build that fails its probes (e.g. break `/ready`); the
Jenkins Deploy stage runs `kubectl rollout undo` on failure.

## 7. Autoscaling (Unit IV)

```
python scripts\load_test.py http://<url-from-step-5> 120 12
kubectl -n student get hpa -w
```

## 8. Monitoring with Prometheus + Grafana (Unit V)

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace
kubectl apply -f k8s/monitoring/
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
```
Grafana: `localhost:3000`, user `admin`; get the password with
`kubectl -n monitoring get secret monitoring-grafana -o jsonpath="{.data.admin-password}"` and
base64-decode it. Import `monitoring/grafana-dashboard.json` (Dashboards > Import).
Check Prometheus targets: `kubectl -n monitoring port-forward svc/monitoring-kube-prometheus-prometheus 9090`.

## 9. Centralized logging with Loki

```
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
helm install loki grafana/loki-stack -n monitoring --set grafana.enabled=false --set promtail.enabled=true
```
In Grafana: Connections > Data sources > Add > Loki > URL `http://loki:3100`. Then in Explore run
`{namespace="student"}`. The app logs JSON, so you can also use `| json | status >= 500`.
The `loki-stack` chart is the simplest for a demo but is an older chart; if the install fails,
check Grafana's current Loki Helm docs and keep the same Promtail + Loki idea.

## 10. Security checks (DevSecOps)

| Tool | Checks | Where |
|---|---|---|
| pip-audit | Known CVEs in `requirements.txt` | Jenkins stage |
| Trivy | OS + library CVEs in the Docker image | Jenkins stage, report archived |
| OWASP Dependency-Check | Dependency CVEs (experimental Python support) | Optional parameter; first run downloads the NVD database and may need an NVD API key |

Pipeline marks the build **UNSTABLE** (not failed) when a scan finds issues, so the demo keeps flowing.
To enforce a hard gate, change `unstable(...)` to `error(...)` in the Jenkinsfile.

## Demo checklist (practical exam)

- [ ] `git log --oneline --graph` shows branches/merges
- [ ] Push a small change; Jenkins build runs all stages green
- [ ] Artifact zip and Trivy report visible on the build page
- [ ] `kubectl get pods -n student` shows the new version running
- [ ] Rolling update, then rollback
- [ ] Grafana dashboard moving under load; Loki shows request logs
- [ ] Explain one scan finding and what you did about it

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ImagePullBackOff` | Image not loaded in Minikube: `minikube image load student-app:<tag>` |
| Jenkins can't find `docker`/`kubectl` | Add them to the Jenkins service PATH, restart Jenkins |
| `kubectl` talks to the wrong cluster | `kubectl config use-context minikube` |
| HPA shows `<unknown>` | `minikube addons enable metrics-server`, wait a minute |
| No data in Grafana | Prometheus > Status > Targets; ServiceMonitor `release` label must equal the Helm release name (`monitoring`) |
| Pasted `kubectl` flags fail | Retype `--` by hand; word processors turn it into a long dash |
