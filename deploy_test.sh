#!/bin/bash
# Quick deployment script for testing
# Assumes you have SSH access to your Home Assistant instance

set -e

echo "🔍 Validating integration..."
python3 -m py_compile custom_components/scrape_do_cenoteka/*.py
echo "✅ Syntax OK"

echo ""
echo "📦 Files to deploy:"
find custom_components/scrape_do_cenoteka -type f -name "*.py" -o -name "*.json" -o -name "*.webp" | sort

echo ""
read -p "Ready to test? Make sure you've committed changes to git first. (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "📝 Next steps:"
echo "1. git add ."
echo "2. git commit -m 'Your message'"
echo "3. git push"
echo "4. In HACS: Click the 3 dots → Reinstall → Select version (or Update if available)"
echo "5. Restart Home Assistant"
echo ""
echo "Or if using manual installation, copy files to Home Assistant custom_components directory"

