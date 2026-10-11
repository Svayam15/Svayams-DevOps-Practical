# Report outline: Student Management System (End-to-End DevOps)

1. **Introduction**: problem, objectives, why DevOps (Unit I: culture, Dev vs Ops gap)
2. **Architecture**: diagram: Developer > GitHub > Jenkins > Docker image > Minikube > Prometheus/Grafana/Loki
3. **Application**: Flask + SQLite, REST API table, UI screenshot, health/metrics endpoints
4. **Version control** (Unit I): branching model (`main`, `develop`, `feature/*`), PR/merge screenshot, commit history
5. **Build and CI** (Unit II): Jenkinsfile stage-by-stage explanation, pytest results, versioned artifact `student-app-1.0.N.zip`
6. **Containerization** (Unit IV): Dockerfile choices (non-root, layer caching, healthcheck), image tags, Compose
7. **Deployment** (Unit III/IV): Kubernetes objects, rolling update + rollback demo, HPA, environments (local vs Minikube)
8. **Monitoring and logging** (Unit V): Prometheus metrics, Grafana dashboard, alert rules, Loki logs
9. **DevSecOps** (Unit V): pip-audit, Trivy, Dependency-Check results and what was fixed
10. **Challenges and limitations**: SQLite per pod, Maven > pip/pytest substitution, local registry
11. **Conclusion and future work**: blue-green, SonarQube, PostgreSQL, Terraform
12. **Appendix**: screenshots checklist
