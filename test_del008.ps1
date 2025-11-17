# Test script for DEL-008: Iterative Refinement System
Write-Host "=== DEL-008: Iterative Refinement System Test ===" -ForegroundColor Cyan

$query = "What's the capital?"
$body = @{ query = $query } | ConvertTo-Json

Write-Host "Sending vague query: '$query'" -ForegroundColor Yellow

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8080/query" -Method POST -Body $body -ContentType "application/json"
    
    $refinement = $response.metadata.refinement
    $quality = $response.metadata.quality_score
    
    Write-Host "Quality: $quality" -ForegroundColor Gray
    Write-Host "Refinement: $($refinement.performed)" -ForegroundColor Gray
    
    if ($refinement.performed) {
        Write-Host "AC-022 PASS: Refinement triggered" -ForegroundColor Green
        Write-Host "  Iterations: $($refinement.iterations)" -ForegroundColor Gray
        Write-Host "  Initial: $($refinement.initial_quality)" -ForegroundColor Gray  
        Write-Host "  Final: $($refinement.final_quality)" -ForegroundColor Gray
        Write-Host "  Convergence: $($refinement.convergence_reason)" -ForegroundColor Gray
        
        $progression = $refinement.quality_progression
        Write-Host "AC-023: Quality progression: $($progression -join ' -> ')" -ForegroundColor Gray
        
        if ($refinement.final_quality -gt $refinement.initial_quality) {
            Write-Host "AC-023 PASS: Quality improved" -ForegroundColor Green
        }
        
        if ($refinement.iterations -and $refinement.quality_progression -and $refinement.convergence_reason) {
            Write-Host "AC-024 PASS: All metadata present" -ForegroundColor Green
        }
    } else {
        Write-Host "Refinement not triggered (quality above threshold)" -ForegroundColor Yellow
    }
    
    Write-Host "Test complete" -ForegroundColor Cyan
} catch {
    Write-Host "Test failed: $($_.Exception.Message)" -ForegroundColor Red
}
