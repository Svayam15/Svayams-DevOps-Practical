# Student Management System: End-to-End DevOps

MSc IT Sem I · DevOps \& CI/CD Engineering (26PMIT102) · Project 1 · Roll No. 41

A small Student CRUD application (Flask + SQLite) built to be taken through a complete DevOps
lifecycle: Git, automated tests, a Jenkins CI/CD pipeline, versioned artifacts, Docker,
Kubernetes (Minikube), Prometheus + Grafana monitoring, Loki logging and security scanning.

The app is intentionally simple. The pipeline around it is the project.

## Flow

```
Developer ──git push──▶ GitHub ──▶ Jenkins pipeline
                                     │ 1 Checkout + version (1.0.<build>)
                                     │ 2 Setup venv, install deps
                                     │ 3 pytest (JUnit report)
                                     │ 4 pip-audit            ┐
                                     │ 5 Package → versioned  │ security
                                     │   zip artifact         │ (DevSecOps)
                                     │ 6 docker build         │
                                     │ 7 Trivy image scan     ┘
                                     │ 8 (optional) Dependency-Check, Docker Hub push
                                     ▼
                        Minikube: rolling update ─ health probes ─ HPA ─ auto rollback on failure
                                     │
                        Prometheus ◀─ /metrics        Loki ◀─ JSON logs (Promtail)
                                     └────── Grafana dashboard ──────┘
```

## Project layout

|Path|Purpose|
|-|-|
|`app/`|Flask app: REST API, UI, `/health`, `/ready`, `/version`, `/metrics`, JSON logging|
|`tests/`|pytest suite (20 tests: CRUD, validation, error cases, ops endpoints)|
|`Jenkinsfile`|The CI/CD pipeline (Windows `bat`, same style as the practicals)|
|`Dockerfile`, `docker-compose.yml`|Image (non-root, healthcheck) and local stack with Prometheus + Grafana|
|`k8s/`|Namespace, ConfigMap, Secret, Deployment, Service, HPA|
|`k8s/monitoring/`|ServiceMonitor and alert rules (applied after Prometheus is installed)|
|`monitoring/`|Prometheus config for Compose, importable Grafana dashboard|
|`scripts/`|Rolling-update and rollback demos, load generator|
|`.github/workflows/ci.yml`|Small second CI (tests only) so GitHub Actions is also shown|
|`docs/RUNBOOK.md`|**Step-by-step commands**: start here to set everything up|
|`docs/REPORT\_OUTLINE.md`|Skeleton for the written report|

## Quick start (no Docker needed)

```
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements-dev.txt
python -m pytest
python run.py            # http://localhost:5000
```

API: `GET/POST /api/students` · `GET/PUT/DELETE /api/students/<id>` · `GET /api/students?course=MSc IT`

## Syllabus mapping

|Unit|Where it appears|
|-|-|
|I: Fundamentals, Git, build automation|Branching workflow (RUNBOOK §1); pip + pytest as the build (stands in for Maven/Gradle)|
|II: CI, Jenkins, artifacts|`Jenkinsfile` stages; versioned `student-app-1.0.N.zip` archived per build|
|III: CD, strategies, environments|Rolling update with `maxUnavailable: 0`, rollback, local vs Minikube environments, manifests as IaC|
|IV: Containers, Kubernetes, scaling|`Dockerfile`, Compose, Deployment/Service, HPA|
|V: Monitoring, logging, DevSecOps|Prometheus + Grafana, alerts, Loki, pip-audit, Trivy, Dependency-Check|

## Known limits (state these honestly in the report)

* **SQLite inside Kubernetes**: each pod has its own database file (`emptyDir`), so with 2+ replicas
data differs per pod and is lost on restart. Acceptable for a pipeline demo; production would use
PostgreSQL or a shared volume. The demo works best with the UI hitting one pod, or scaled to 1 replica.
* **Build tool**: Flask has no Maven/Gradle; the build stage is `pip install` + `pytest` + zip packaging.
* **- \*\*Registry\*\*: images are loaded straight into Minikube; Docker Hub push is an optional pipeline parameter.**
* **Not yet done**: blue-green deployment and SonarQube (planned as optional extensions).

