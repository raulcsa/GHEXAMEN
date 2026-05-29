#!/bin/bash
# validation script for infrastructure
set -e

echo "🔍 Starting Infrastructure Validation..."

# Locate current directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

# Check if main.tf exists
if [ -f "main.tf" ]; then
  echo "✅ main.tf found."
else
  echo "❌ Error: main.tf not found!"
  exit 1
fi

# Mock terraform syntax checking (e.g. check for brackets)
if grep -q "resource" "main.tf"; then
  echo "✅ Syntax check: resource declaration found."
else
  echo "❌ Error: Invalid Terraform file layout."
  exit 1
fi

echo "✨ Infrastructure Validation Completed Successfully!"
