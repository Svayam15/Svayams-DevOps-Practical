// Student Management System: CI/CD pipeline (Windows agent, so `bat`, same as the practicals)
// Flow: Checkout > Setup > Test > pip-audit > Package > Docker Build > Trivy
//       > (Dependency-Check) > (Push) > Deploy to Minikube > Smoke Test
pipeline {
    agent any

        parameters {
        booleanParam(name: 'RUN_DEPENDENCY_CHECK', defaultValue: false,
                     description: 'OWASP Dependency-Check (slow on first run: downloads the NVD database)')
        booleanParam(name: 'DEPLOY_TO_K8S', defaultValue: true,
                     description: 'Deploy to Minikube')
    }

        environment {
        APP_NAME = 'student-app'
        DOCKERHUB_USER = 'svayam15'
        KUBECONFIG = 'C:\\Users\\svaya\\.kube\\config'
        MINIKUBE_HOME = 'C:\\Users\\svaya'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
                script {
                    // VERSION file holds major.minor (e.g. 1.0); build number makes it unique
                    env.VERSION = "${readFile('VERSION').trim()}.${env.BUILD_NUMBER}"
                }
                echo "Building version ${env.VERSION}"
            }
        }

        stage('Setup') {
            steps {
                bat 'python -m venv venv'
                bat 'venv\\Scripts\\python -m pip install --upgrade pip'
                bat 'venv\\Scripts\\python -m pip install -r requirements-dev.txt'
            }
        }

        stage('Test') {
            steps {
                bat 'if not exist reports mkdir reports'
                bat 'venv\\Scripts\\python -m pytest --junitxml=reports\\junit.xml'
            }
            post {
                always { junit allowEmptyResults: true, testResults: 'reports/junit.xml' }
            }
        }

        stage('Dependency Audit (pip-audit)') {
            steps {
                script {
                    def rc = bat(returnStatus: true, script: 'venv\\Scripts\\pip-audit -r requirements.txt')
                    if (rc != 0) { unstable('pip-audit reported vulnerable Python dependencies') }
                }
            }
        }

        stage('Package') {
            steps {
                bat 'if not exist dist mkdir dist'
                bat 'powershell -Command "Compress-Archive -Path app,run.py,requirements.txt,VERSION -DestinationPath dist\\%APP_NAME%-%VERSION%.zip -Force"'
                archiveArtifacts artifacts: 'dist/*.zip', fingerprint: true
            }
        }

        stage('Docker Build') {
            steps {
                bat 'docker build --build-arg APP_VERSION=%VERSION% -t %APP_NAME%:%VERSION% -t %APP_NAME%:latest .'
            }
        }

                stage('Image Scan (Trivy)') {
            steps {
                script {
                    def rc = bat(returnStatus: true,
                        script: 'docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v trivy-cache:/root/.cache/ aquasec/trivy:latest image --severity HIGH,CRITICAL --exit-code 1 %APP_NAME%:%VERSION% > reports\\trivy-%VERSION%.txt')
                    bat 'type reports\\trivy-%VERSION%.txt'
                    if (rc != 0) { unstable('Trivy found HIGH/CRITICAL vulnerabilities in the image') }
                }
            }
        }

        stage('OWASP Dependency-Check') {
            when { expression { params.RUN_DEPENDENCY_CHECK } }
            steps {
                script {
                    def rc = bat(returnStatus: true,
                        script: 'dependency-check.bat --project %APP_NAME% --scan requirements.txt --enableExperimental --format HTML --out reports\\dependency-check')
                    if (rc != 0) { unstable('Dependency-Check failed or found issues') }
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withEnv(["DOCKER_CONFIG=${env.WORKSPACE}\\.docker"]) {
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                                                      usernameVariable: 'DH_USER',
                                                      passwordVariable: 'DH_PASS')]) {
                        bat '''
                            echo %DH_PASS%| docker login -u %DH_USER% --password-stdin
                            docker tag %APP_NAME%:%VERSION% %DOCKERHUB_USER%/%APP_NAME%:%VERSION%
                            docker push %DOCKERHUB_USER%/%APP_NAME%:%VERSION%
                            docker logout
                        '''
                    }
                }
            }
        }

                stage('Deploy to Minikube') {
            when { expression { params.DEPLOY_TO_K8S } }
            steps {
                bat 'kubectl apply -f k8s/'
                bat 'kubectl -n student set image deployment/student-app student-app=%DOCKERHUB_USER%/%APP_NAME%:%VERSION%'
                bat 'kubectl -n student rollout status deployment/student-app --timeout=180s'
            }
            post {
                failure {
                    echo 'Deployment failed: rolling back to the previous revision'
                    bat 'kubectl -n student rollout undo deployment/student-app'
                }
            }
        }

        stage('Smoke Test') {
            when { expression { params.DEPLOY_TO_K8S } }
            steps {
                bat 'kubectl -n student exec deploy/student-app -- python -c "import urllib.request; print(urllib.request.urlopen(\'http://127.0.0.1:5000/version\').read().decode())"'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
        }
        success { echo "Pipeline succeeded: ${env.APP_NAME}:${env.VERSION}" }
        failure { echo 'Pipeline failed: check the stage logs above' }
    }
}
