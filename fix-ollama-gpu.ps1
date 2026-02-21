# Fix Ollama GPU Access
# This script restarts Ollama with proper NVIDIA GPU configuration

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Fixing Ollama GPU Access" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location -Path "C:\Users\steve\local-ai-packaged"

Write-Host "[1/3] Stopping Ollama container..." -ForegroundColor Yellow
docker stop ollama

Write-Host ""
Write-Host "[2/3] Removing Ollama container..." -ForegroundColor Yellow
docker rm ollama

Write-Host ""
Write-Host "[3/3] Starting Ollama with GPU support..." -ForegroundColor Yellow
docker compose -p localai --profile gpu-nvidia -f docker-compose.yml -f docker-compose.override.private.yml -f docker-compose.gpu-fix.yml up -d ollama-gpu

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host " GPU Fix Applied!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Verifying GPU access..." -ForegroundColor Cyan
Start-Sleep -Seconds 3
docker exec ollama nvidia-smi

Write-Host ""
Write-Host "If you see GPU information above, Ollama now has GPU access!" -ForegroundColor Green
