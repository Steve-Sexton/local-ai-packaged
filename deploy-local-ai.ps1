# Local AI Stack Deployment Script
# Auto-generated deployment script for local-ai-packaged

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Local AI Stack Deployment with NVIDIA GPU" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Set location to local-ai-packaged directory
Set-Location -Path "C:\Users\steve\local-ai-packaged"

Write-Host "[1/3] Pulling latest images..." -ForegroundColor Yellow
docker compose -p localai --profile gpu-nvidia -f docker-compose.yml -f docker-compose.override.private.yml pull

Write-Host ""
Write-Host "[2/3] Starting services..." -ForegroundColor Yellow
docker compose -p localai --profile gpu-nvidia -f docker-compose.yml -f docker-compose.override.private.yml up -d

Write-Host ""
Write-Host "[3/3] Checking service status..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
docker compose -p localai ps

Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host " Deployment Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Primary Services:" -ForegroundColor Cyan
Write-Host "  Open WebUI (Chat):     http://localhost:8080" -ForegroundColor White
Write-Host "  n8n (Workflows):       http://localhost:5678" -ForegroundColor White
Write-Host "  Flowise (AI Flows):    http://localhost:3001" -ForegroundColor White
Write-Host ""
Write-Host "Supporting Services:" -ForegroundColor Cyan
Write-Host "  Langfuse (Observ):     http://localhost:3000" -ForegroundColor White
Write-Host "  SearXNG (Search):      http://localhost:8081" -ForegroundColor White
Write-Host "  Neo4j Browser:         http://localhost:7474" -ForegroundColor White
Write-Host "  Qdrant (Vector DB):    http://localhost:6333" -ForegroundColor White
Write-Host "  Ollama API:            http://localhost:11434" -ForegroundColor White
Write-Host "  MinIO Console:         http://localhost:9011" -ForegroundColor White
Write-Host ""
Write-Host "Run 'docker compose -p localai logs -f' to view logs" -ForegroundColor Gray
