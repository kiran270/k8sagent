# Kubernetes Cluster Monitor

A lightweight monitoring application that collects cluster information and displays issues in a web UI.

## Features

- Real-time cluster monitoring
- Node status tracking
- Pod health checks
- Deployment status
- Issue detection and alerts
- Auto-refresh every 30 seconds

## Build and Deploy

### 1. Setup GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### 2. Push to GitHub

The GitHub Actions workflow will automatically:
- Build the Docker image
- Push to ECR when you push to main/master branch

### 3. Deploy to Kubernetes

```bash
kubectl apply -f k8s-deployment.yaml
```

### 3. Access the UI

Get the service URL:
```bash
kubectl get svc cluster-monitor
```

For local testing with port-forward:
```bash
kubectl port-forward svc/cluster-monitor 8080:80
```

Then visit: http://localhost:8080

## Issues Detected

- Node NotReady status
- Pods not in Running/Succeeded state
- High pod restart counts (>5)
- Deployment replicas mismatch

## Local Development

```bash
pip install -r requirements.txt
python app.py
```

Make sure you have kubectl configured to access your cluster.
