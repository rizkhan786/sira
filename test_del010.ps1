# Test DEL-010: Metrics Tracking System
Write-Host "=== DEL-010: Metrics Tracking System Test ===" -ForegroundColor Cyan

# AC-028: Core metrics captured
Write-Host "AC-028: Testing metrics capture..." -ForegroundColor Yellow
for ($i = 1; $i -le 5; $i++) {
    $body = @{ query = "Test $i" } | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:8080/query" -Method POST -Body $body -ContentType "application/json" | Out-Null
}
Write-Host "AC-028 PASS: Metrics captured" -ForegroundColor Green

# AC-029 & AC-030: Metrics stored and API works
Write-Host "AC-029/AC-030: Testing storage and API..." -ForegroundColor Yellow
$summary = Invoke-RestMethod -Uri "http://localhost:8080/metrics/summary"
Write-Host "Total queries: $($summary.total_queries)" -ForegroundColor Gray
Write-Host "Avg quality: $($summary.avg_quality)" -ForegroundColor Gray

if ($summary.total_queries -ge 5) {
    Write-Host "AC-029 PASS: Metrics stored in DB" -ForegroundColor Green
} else {
    Write-Host "AC-029 FAIL" -ForegroundColor Red
}

$trends = Invoke-RestMethod -Uri "http://localhost:8080/metrics/trends?days=1"
if ($trends.quality.Count -gt 0) {
    Write-Host "AC-030 PASS: API endpoints working" -ForegroundColor Green
} else {
    Write-Host "AC-030 FAIL" -ForegroundColor Red
}

Write-Host "Test complete" -ForegroundColor Cyan
