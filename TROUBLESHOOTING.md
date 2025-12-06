# Troubleshooting 500 Error

## Steps to Fix

### 1. Clear All Caches

**In Home Assistant:**
- Settings → System → Storage → Clear cache (if available)
- Or manually delete: `/config/.storage/` (backup first!)

**In your repo:**
```bash
find custom_components/scrape_do_cenoteka -name "*.pyc" -delete
find custom_components/scrape_do_cenoteka -name "__pycache__" -type d -exec rm -r {} +
```

### 2. Complete Reinstall

1. **Remove completely from HACS:**
   - HACS → Integrations → Find "Scrape.do - Cenoteka"
   - Click the 3 dots → Delete
   - Confirm deletion

2. **Restart Home Assistant completely**

3. **Reinstall:**
   - HACS → Integrations → Add Custom Repository
   - Add your repo URL
   - Click Download

4. **Restart Home Assistant again**

### 3. Check Logs for Exact Error

**Critical:** The logs will show the EXACT error. Do this:

1. Open Home Assistant
2. Settings → System → Logs
3. Look for errors related to `scrape_do_cenoteka`
4. Copy the FULL traceback - it will show the exact line and error

### 4. Verify Files

```bash
# From your repo root
python3 -m py_compile custom_components/scrape_do_cenoteka/*.py
python3 test_integration.py
```

### 5. Manual File Check

Make sure `config_flow.py` exists and has the class:
```bash
grep -n "class CenotekaConfigFlow" custom_components/scrape_do_cenoteka/config_flow.py
```

Should show: `87:class CenotekaConfigFlow(ConfigFlow, domain=DOMAIN):`

## Most Likely Causes

1. **Stale cache** - Home Assistant cached the broken version
2. **Incomplete deletion** - Old files still present
3. **Dependencies not installed** - Check if requests/beautifulsoup4 are installed
4. **Python version mismatch** - HA might be using different Python version

## Get the Actual Error

**This is the most important step!** The logs will tell us exactly what's wrong.

In Home Assistant:
- Settings → System → Logs
- Filter for: `scrape_do` or `cenoteka` or `error`
- Copy the full traceback and share it

Without the actual error from logs, we're just guessing!

