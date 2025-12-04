# Timeout Fix Guide

**Issue:** "Error: timeout of 60000ms exceeded" when submitting queries

**Status:** ✅ FIXED (Commit: f8b4e42)

---

## What Was Fixed

### 1. Increased Timeouts
- **Frontend:** 60 seconds → **5 minutes** (300 seconds)
- **Backend LLM Client:** 2 minutes → **5 minutes**
- Reason: Complex reasoning queries can take 2-3 minutes

### 2. Better Error Messages
Before:
```
Error: timeout of 60000ms exceeded
```

After:
```
Request timeout (5 minutes). This query is taking too long. 
Try a simpler query or check if SIRA is running.
```

Or:
```
No response from server. Is SIRA API running on http://localhost:8080?
```

### 3. Progress Indicator
- Shows elapsed time: `Processing... 0:45`
- Warning after 30 seconds: `(Taking longer than usual)`
- Progress info: `⏳ SIRA is thinking... This may take up to 5 minutes`
- Timer display: `Elapsed: 1:23 / 5:00 max`

---

## How to Apply the Fix

### Option 1: Rebuild Web Interface (Recommended)

```powershell
# Stop current web server (Ctrl+C if running)

# Rebuild web interface
cd web
npm run build
npm run dev

# Or rebuild Docker containers
cd ..
docker-compose down
docker-compose up --build web
```

### Option 2: Browser Hard Refresh

If the web server is already running with the new code:

1. Open http://localhost:3001
2. **Hard refresh:**
   - Windows: `Ctrl + Shift + R` or `Ctrl + F5`
   - Mac: `Cmd + Shift + R`
3. Clear cache if needed (browser settings)

---

## Expected Behavior Now

### When Submitting a Query:

1. **0-5 seconds:** Button shows "Processing... 0:05"
2. **30+ seconds:** Warning appears: "Processing... 0:45 (Taking longer than usual)"
3. **Progress box appears:**
   ```
   ⏳ SIRA is thinking... This may take up to 5 minutes for complex queries.
   Elapsed: 1:23 / 5:00 max
   ```
4. **If it times out (5 min):** Clear error message with suggestions

### Timeout Scenarios:

#### Scenario 1: Actual Timeout (5 minutes passed)
```
Error: Request timeout (5 minutes). This query is taking too long. 
Try a simpler query or check if SIRA is running.
```

**What to do:**
- Try a simpler query
- Check if Ollama is responding slowly (restart it)
- Check if LLM model is loaded: `ollama ps`

#### Scenario 2: Server Not Responding
```
Error: No response from server. Is SIRA API running on http://localhost:8080?
```

**What to do:**
- Check if API is running: `curl.exe http://localhost:8080/health`
- Restart SIRA API: `docker-compose restart api`

#### Scenario 3: Server Error
```
Error: Server error: [specific error message from backend]
```

**What to do:**
- Check API logs: `docker logs sira-api`
- Look for specific error details

---

## Testing the Fix

### Test 1: Simple Query (< 30 seconds)
```
Query: "What is 2 + 2?"
Expected: Fast response, timer shows ~5-10 seconds
```

### Test 2: Complex Query (30-120 seconds)
```
Query: "Explain quantum computing in detail, including how qubits work, 
superposition, entanglement, and provide examples of quantum algorithms."
Expected: 
- Timer shows progress (0:45, 1:15, etc.)
- Warning appears after 30 seconds
- Response arrives within 5 minutes
```

### Test 3: Very Complex Query (might timeout)
```
Query: "Write a complete 5000-word essay on the history of artificial 
intelligence from 1950 to present, including all major breakthroughs, 
key figures, and their contributions."
Expected:
- Progress indicator shows thinking
- May timeout at 5:00 if LLM is too slow
- Clear error message with guidance
```

---

## If Queries Are Still Slow

### Check LLM Performance

```powershell
# Check if model is loaded
ollama ps

# Test LLM directly
ollama run llama3.2:3b "What is 2+2?"

# Check response time (should be < 10 seconds for simple queries)
```

### Check System Resources

```powershell
# Windows Task Manager: Check CPU/RAM/GPU usage
# If Ollama is using 100% CPU constantly, it's working hard
```

### Potential Issues:

1. **LLM Not Loaded:** 
   - First query loads the model (1-2 minutes)
   - Subsequent queries are faster
   - Solution: Keep Ollama running

2. **CPU Too Slow:**
   - LLaMA 3.2 3B requires decent CPU
   - Queries may genuinely take 2-5 minutes
   - Solution: Use GPU acceleration if available

3. **Pattern Retrieval Slow:**
   - ChromaDB with 100K+ patterns
   - Solution: Already optimized with Redis caching

---

## Configuration (If You Want Different Timeouts)

### Frontend Timeout (`web/src/api/client.js`):
```javascript
timeout: 300000, // 5 minutes (in milliseconds)

// To change:
timeout: 600000, // 10 minutes
timeout: 180000, // 3 minutes
```

### Backend LLM Timeout (`src/llm/client.py`):
```python
self.timeout = 300.0  # 5 minutes (in seconds)

# To change:
self.timeout = 600.0  # 10 minutes
self.timeout = 180.0  # 3 minutes
```

**Note:** Frontend timeout should be >= Backend timeout

---

## Summary

### What Changed:
✅ Frontend timeout: 60s → 5 min  
✅ Backend timeout: 2 min → 5 min  
✅ Progress indicator with timer  
✅ Better error messages  
✅ Warnings for slow queries  

### How to Apply:
1. Rebuild web: `cd web && npm run build && npm run dev`
2. Or hard refresh: `Ctrl + Shift + R`

### When to Expect Timeouts:
- Queries > 5 minutes (rare, but possible)
- LLM not responding (restart Ollama)
- API not running (check Docker)

**The 5-minute timeout should handle 99% of queries. If you're hitting it frequently, the issue is likely with the LLM performance, not the timeout setting.**
