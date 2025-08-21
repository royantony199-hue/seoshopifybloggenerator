#!/usr/bin/env python3
"""
Quick start script for SEO Blog Automation SaaS Platform
This creates a minimal working setup for testing
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_status(message, status="info"):
    colors = {
        "info": "\033[94m",
        "success": "\033[92m", 
        "warning": "\033[93m",
        "error": "\033[91m",
        "end": "\033[0m"
    }
    print(f"{colors[status]}🚀 {message}{colors['end']}")

def check_requirements():
    """Check if required tools are installed"""
    print_status("Checking requirements...")
    
    # Check Docker
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print_status("✓ Docker found", "success")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_status("❌ Docker not found. Please install Docker first.", "error")
        return False
    
    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], check=True, capture_output=True, text=True)
        print_status(f"✓ Python found: {result.stdout.strip()}", "success")
    except subprocess.CalledProcessError:
        print_status("❌ Python not found", "error")
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], check=True, capture_output=True, text=True)
        print_status(f"✓ Node.js found: {result.stdout.strip()}", "success")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_status("❌ Node.js not found. Please install Node.js first.", "error")
        return False
    
    return True

def start_database():
    """Start PostgreSQL and Redis with Docker"""
    print_status("Starting database services...")
    
    try:
        # Start only db and redis
        subprocess.run([
            "docker-compose", "up", "-d", "db", "redis"
        ], check=True, cwd="/Users/royantony/blue-lotus-seo/saas-platform")
        
        print_status("✓ Database services started", "success")
        
        # Wait for database to be ready
        print_status("Waiting for database to be ready...")
        time.sleep(10)
        
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"❌ Failed to start database: {e}", "error")
        return False

def setup_backend():
    """Set up and start backend"""
    print_status("Setting up backend...")
    
    backend_dir = Path("/Users/royantony/blue-lotus-seo/saas-platform/backend")
    venv_dir = backend_dir / "venv"
    
    try:
        # Create virtual environment
        if not venv_dir.exists():
            print_status("Creating virtual environment...")
            subprocess.run([
                sys.executable, "-m", "venv", str(venv_dir)
            ], check=True, cwd=backend_dir)
        
        # Install dependencies
        print_status("Installing Python dependencies...")
        pip_cmd = str(venv_dir / "bin" / "pip") if os.name != 'nt' else str(venv_dir / "Scripts" / "pip.exe")
        
        subprocess.run([
            pip_cmd, "install", "--upgrade", "pip"
        ], check=True)
        
        subprocess.run([
            pip_cmd, "install", "-r", "requirements.txt"
        ], check=True, cwd=backend_dir)
        
        print_status("✓ Backend dependencies installed", "success")
        return True
        
    except subprocess.CalledProcessError as e:
        print_status(f"❌ Backend setup failed: {e}", "error")
        return False

def setup_frontend():
    """Set up frontend"""
    print_status("Setting up frontend...")
    
    frontend_dir = Path("/Users/royantony/blue-lotus-seo/saas-platform/frontend")
    
    try:
        # Install dependencies
        print_status("Installing Node.js dependencies...")
        subprocess.run([
            "npm", "install"
        ], check=True, cwd=frontend_dir)
        
        print_status("✓ Frontend dependencies installed", "success")
        return True
        
    except subprocess.CalledProcessError as e:
        print_status(f"❌ Frontend setup failed: {e}", "error")
        return False

def create_simple_frontend():
    """Create a simple React app for testing"""
    print_status("Creating simple frontend files...")
    
    # Create minimal components needed
    components = [
        ("src/hooks/useAuth.ts", '''
import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
'''),
        ("src/services/api.ts", '''
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const dashboardApi = {
  getStats: async () => {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${API_BASE}/api/dashboard`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) throw new Error('Failed to fetch dashboard stats');
    return response.json();
  },
};
'''),
        ("src/components/Layout/Layout.tsx", '''
import React from 'react';
import { Outlet } from 'react-router-dom';
import { Box } from '@mui/material';

const Layout: React.FC = () => {
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <Outlet />
    </Box>
  );
};

export default Layout;
'''),
        ("src/pages/Auth/LoginPage.tsx", '''
import React, { useState } from 'react';
import {
  Container,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
} from '@mui/material';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, loading } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Card>
        <CardContent sx={{ p: 4 }}>
          <Typography variant="h4" align="center" gutterBottom>
            SEO Blog Automation
          </Typography>
          <Typography variant="h6" align="center" color="textSecondary" gutterBottom>
            Sign in to your account
          </Typography>
          
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          
          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              disabled={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
};

export default LoginPage;
''')
    ]
    
    frontend_dir = Path("/Users/royantony/blue-lotus-seo/saas-platform/frontend")
    
    for file_path, content in components:
        full_path = frontend_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content.strip())
    
    print_status("✓ Simple frontend files created", "success")

def main():
    """Main setup function"""
    print_status("🌸 SEO Blog Automation SaaS - Quick Start Setup")
    print_status("=" * 60)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Start database
    if not start_database():
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        sys.exit(1)
    
    # Create simple frontend files
    create_simple_frontend()
    
    print_status("=" * 60)
    print_status("🎉 Setup complete!", "success")
    print_status("")
    print_status("Next steps:")
    print_status("1. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload")
    print_status("2. Start frontend: cd frontend && npm run dev")
    print_status("3. Open browser: http://localhost:3000")
    print_status("")
    print_status("📚 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()