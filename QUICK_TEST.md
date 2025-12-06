# Quick Testing Guide

## Before Deploying

Run the test script:
```bash
python3 test_integration.py
```

This validates:
- ✅ Python syntax
- ✅ JSON validity
- ✅ File structure

## Faster Testing Workflow

### Option 1: Direct File Copy (Fastest for local testing)
If your Home Assistant is on the same machine or you have direct file access:

```bash
# Copy files directly (adjust path to your HA custom_components)
cp -r custom_components/scrape_do_cenoteka /path/to/homeassistant/config/custom_components/
# Then restart HA (much faster than HACS reinstall)
```

### Option 2: Check Logs Before Full Restart
After pushing changes and before restarting:

1. In Home Assistant UI: Settings → System → Logs
2. Filter for: `scrape_do_cenoteka` or `error`
3. Look for the actual Python traceback - this will tell you exactly what's wrong

### Option 3: Git + HACS (Current Method)
```bash
git add .
git commit -m "Fix config flow"
git push
# Then in HACS: Reinstall → Restart
```

## Common Issues to Check

1. **500 Error on Config Flow Load:**
   - Check Home Assistant logs for the actual error
   - Common causes: Import errors, syntax issues, missing dependencies

2. **If logs show import errors:**
   - Dependencies not installed? Check `manifest.json` requirements
   - Wrong Python version? Check HA Python version

3. **If config flow doesn't appear:**
   - Check `manifest.json` has `"config_flow": true`
   - Restart Home Assistant completely
   - Clear browser cache

## Quick Debug Checklist

- [ ] All Python files compile: `python3 -m py_compile custom_components/scrape_do_cenoteka/*.py`
- [ ] manifest.json is valid JSON
- [ ] Domain matches in manifest.json and const.py
- [ ] Config flow class name matches domain
- [ ] No syntax errors in any file

