# Create a session first
Write-Host "Creating session..." -ForegroundColor Cyan
$sessionResponse = Invoke-RestMethod -Uri "http://localhost:8080/session" -Method POST
$sessionId = $sessionResponse.id
Write-Host "Session created: $sessionId" -ForegroundColor Green

# Test query with pattern application
Write-Host "\nTesting DEL-007 with math query..." -ForegroundColor Cyan
$body = @{
    query = "What is 30 + 70?"
    session_id = $sessionId
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8080/query" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

Write-Host "\nQuery completed!" -ForegroundColor Green
Write-Host "Patterns retrieved: $($response.metadata.patterns_retrieved_count)" -ForegroundColor Yellow
Write-Host "Patterns applied: $($response.metadata.patterns_applied_count)" -ForegroundColor Yellow
Write-Host "Quality score: $($response.metadata.quality_score)" -ForegroundColor Yellow

$response | ConvertTo-Json -Depth 10
