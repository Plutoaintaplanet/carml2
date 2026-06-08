# CI/CD Setup for CARML

## Files added
- `Jenkinsfile` - full pipeline with Docker build + Docker Hub push + Vercel deployment.
- `Jenkinsfile.no-docker-push` - same pipeline but without the Docker push stage.
- `Dockerfile` - builds the FastAPI application as a Docker image using the `CARML/` subfolder.
- `requirements.txt` - Python runtime dependencies for the application.

## Jenkins pipeline behavior

Both Jenkinsfiles contain these stages:
1. Checkout source code from GitHub.
2. Install Python dependencies.
3. Run code quality analysis with `flake8`.
4. Perform dependency/vulnerability scanning using `trivy`.
5. Build a Docker image.

`Jenkinsfile` then also:
6. Push the Docker image to Docker Hub.
7. Trigger a Vercel deployment using the Vercel CLI.

`Jenkinsfile.no-docker-push` skips stage 6.

## Required Jenkins credentials

Add these credentials in Jenkins:
- `dockerhub-credentials` - Docker Hub username/password.
- `vercel-token` - Vercel authentication token.
- `vercel-scope` - Vercel scope or team name (for example `plutoaintaplanet`).
- `sonar-token` - SonarCloud authentication token.

### SonarCloud details
- Project Key: `Plutoaintaplanet_carml2`
- Organization Key: `plutoaintaplanet`
- Host URL: `https://sonarcloud.io`

If you use a self-hosted SonarQube instance instead, update `sonar.host.url` in the Jenkinsfiles accordingly.

## GitHub Actions

New GitHub Actions workflows have been added in `.github/workflows/`:
- `ci-cd.yml` — full pipeline with Docker build, Docker Hub push, and Vercel deploy.
- `ci-cd-no-docker-push.yml` — pipeline with Docker build but without pushing the image.

### GitHub Actions secrets
Add the following secrets in your GitHub repository Settings > Secrets:
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_PASSWORD`
- `DOCKERHUB_REPO` — Docker Hub repository name (for example `myuser/carml-app`).
- `SONAR_TOKEN`
- `VERCEL_TOKEN`
- `VERCEL_SCOPE`

## Configuration

Edit `Jenkinsfile` and `Jenkinsfile.no-docker-push` to set:
- `DOCKER_IMAGE` to your Docker Hub repository name, e.g. `myuser/carml-app`
- `IMAGE_TAG` to the desired tag, e.g. `latest`

## Deployment

The Vercel deploy stage uses the Vercel CLI. The repo includes a `vercel.json` file so Vercel can deploy using the `Dockerfile`.

If you prefer another host, replace the deploy stage with your cloud provider's CLI or API command.

## Notes

- The vulnerability scan runs `aquasec/trivy:latest` against the workspace.
- If you want a versioned `requirements-dev.txt`, add linters/test tools there and update the Jenkinsfiles.
- The Docker container exposes port `8000` and runs `uvicorn server:app`.

## Running both Jenkins pipelines from CLI

A helper script is included: `run-jenkins-pipelines.ps1`.

Usage:

```powershell
cd C:\Users\admin\Documents\carml
.\run-jenkins-pipelines.ps1 -JenkinsUrl 'http://localhost:8080/' -CliJar 'C:\Users\admin\Downloads\jenkins-cli (1).jar' -Auth 'admin:YOUR_API_TOKEN'
```

This script will:
- create `carml-full-pipeline` and `carml-no-docker-push` jobs if missing
- trigger both pipelines
- poll and display build progress and final console output
change 1