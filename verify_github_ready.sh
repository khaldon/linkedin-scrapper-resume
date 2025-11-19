#!/bin/bash
# Pre-push verification script

echo "🔍 GitHub Pre-Push Verification"
echo "================================"
echo ""

# Check for sensitive files
echo "1️⃣ Checking for sensitive files..."
SENSITIVE_FILES=0

if git ls-files | grep -q "^\.env$"; then
    echo "❌ ERROR: .env is tracked!"
    SENSITIVE_FILES=1
else
    echo "✅ .env is not tracked"
fi

if git ls-files | grep -q "^data/"; then
    echo "❌ ERROR: data/ directory is tracked!"
    SENSITIVE_FILES=1
else
    echo "✅ data/ directory is not tracked"
fi

if git ls-files | grep -q "\.pdf$"; then
    echo "❌ ERROR: PDF files are tracked!"
    SENSITIVE_FILES=1
else
    echo "✅ No PDF files tracked"
fi

if git ls-files | grep -q "\.db$"; then
    echo "❌ ERROR: Database files are tracked!"
    SENSITIVE_FILES=1
else
    echo "✅ No database files tracked"
fi

if git ls-files | grep -q "^cv\.md$"; then
    echo "❌ WARNING: cv.md (personal CV) is tracked!"
    SENSITIVE_FILES=1
else
    echo "✅ cv.md is not tracked"
fi

echo ""

# Check for required files
echo "2️⃣ Checking for required files..."
MISSING_FILES=0

if [ -f ".env.example" ]; then
    echo "✅ .env.example exists"
else
    echo "❌ ERROR: .env.example missing!"
    MISSING_FILES=1
fi

if [ -f "LICENSE" ]; then
    echo "✅ LICENSE exists"
else
    echo "❌ ERROR: LICENSE missing!"
    MISSING_FILES=1
fi

if [ -f "README.md" ]; then
    echo "✅ README.md exists"
else
    echo "❌ ERROR: README.md missing!"
    MISSING_FILES=1
fi

if [ -f "CONTRIBUTING.md" ]; then
    echo "✅ CONTRIBUTING.md exists"
else
    echo "❌ WARNING: CONTRIBUTING.md missing"
fi

echo ""

# Check for YOUR_USERNAME placeholder
echo "3️⃣ Checking for placeholders..."
if grep -q "YOUR_USERNAME" pyproject.toml README.md 2>/dev/null; then
    echo "⚠️  WARNING: Found 'YOUR_USERNAME' placeholder"
    echo "   Please update with your actual GitHub username"
else
    echo "✅ No placeholders found"
fi

echo ""

# Summary
echo "================================"
if [ $SENSITIVE_FILES -eq 0 ] && [ $MISSING_FILES -eq 0 ]; then
    echo "✅ ALL CHECKS PASSED!"
    echo ""
    echo "You're ready to push to GitHub! 🚀"
    echo ""
    echo "Next steps:"
    echo "1. Update YOUR_USERNAME in pyproject.toml and README.md"
    echo "2. git add ."
    echo "3. git commit -m 'Initial commit'"
    echo "4. git push -u origin main"
else
    echo "❌ SOME CHECKS FAILED!"
    echo ""
    echo "Please fix the issues above before pushing."
    exit 1
fi
