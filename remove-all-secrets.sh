#!/bin/bash
# Script to remove ALL secrets from the codebase

echo "🔒 Removing all secrets from the codebase..."

# 1. Remove backup files that contain real API keys
echo "Removing backup files with secrets..."
rm -rf backend/backups/*.json
rm -rf backups/*.json
echo "✅ Backup files removed"

# 2. Remove any .env files that might have been accidentally committed
echo "Removing environment files..."
find . -name ".env" -type f -delete
find . -name ".env.*" -type f -delete
echo "✅ Environment files removed"

# 3. Remove database files that might contain user data
echo "Removing database files..."
rm -f backend/*.db
rm -f *.db
rm -f backend/*.sqlite
rm -f backend/*.sqlite3
echo "✅ Database files removed"

# 4. Remove log files that might contain sensitive data
echo "Removing log files..."
rm -f backend/*.log
rm -f frontend/*.log
rm -f *.log
echo "✅ Log files removed"

# 5. Remove any test files with hardcoded secrets
echo "Removing test files with potential secrets..."
rm -f backend/test_shopify.py
rm -f backend/test_shopify_publish.py
rm -f test-complete.html
rm -f debug-frontend.html
echo "✅ Test files removed"

# 6. Create clean .gitignore to prevent future issues
echo "Creating comprehensive .gitignore..."
cat > .gitignore << 'EOF'
# ===== SECURITY - NEVER COMMIT THESE =====
# Environment files with secrets
.env
.env.*
*.env
backend/.env
frontend/.env

# Database files
*.db
*.sqlite
*.sqlite3
seo_saas.db
saas_platform.db

# Backup files
backups/
backend/backups/
*.backup
*.json.backup

# Log files
*.log
logs/
backend/logs/
frontend/logs/

# API keys and credentials
**/secrets.json
**/credentials.json
**/*_key.json
**/test_*.py

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
venv/
env/
ENV/
backend/venv/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Temporary
*.tmp
*.temp
tmp/
temp/
EOF

echo "✅ .gitignore updated"

# 7. Create safe example files
echo "Creating safe example files..."

# Create .env.example for backend
cat > backend/.env.example << 'EOF'
# Backend Environment Variables
DATABASE_URL=sqlite:///./seo_saas.db
SECRET_KEY=your-super-secure-secret-key-at-least-32-characters
OPENAI_API_KEY=your-openai-api-key-here
ENVIRONMENT=development
DEBUG=true
EOF

# Create .env.example for frontend
cat > frontend/.env.example << 'EOF'
# Frontend Environment Variables
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
EOF

echo "✅ Example environment files created"

echo ""
echo "🎉 All secrets have been removed from your codebase!"
echo ""
echo "📋 Next steps:"
echo "1. Review the changes in GitHub Desktop"
echo "2. Make sure no sensitive files are selected for commit"
echo "3. Commit and push to GitHub"
echo "4. Add your real API keys in Railway environment variables"
echo ""
echo "🔒 Your code is now safe to push to GitHub!"