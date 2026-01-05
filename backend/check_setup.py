#!/usr/bin/env python3
"""
Quick Test Script for Backend Setup
====================================
Run this to verify your backend is configured correctly.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings


def check_env_vars():
    """Check if all required environment variables are set."""
    print("🔍 Checking environment variables...\n")
    
    checks = {
        "GEMINI_API_KEY": settings.gemini_api_key,
        "ELEVENLABS_API_KEY": settings.elevenlabs_api_key,
        "ELEVENLABS_AGENT_ID": settings.elevenlabs_agent_id,
        "ELEVENLABS_PHONE_NUMBER_ID": settings.elevenlabs_phone_number_id,
        "MOCK_MODE": settings.mock_mode,
    }
    
    all_good = True
    
    for key, value in checks.items():
        if key == "MOCK_MODE":
            if value:
                print(f"  ⚠️  {key}: {value} (Should be False for real calls)")
                all_good = False
            else:
                print(f"  ✅ {key}: {value} (Good - real API calls enabled)")
        elif not value or value == "":
            print(f"  ❌ {key}: NOT SET")
            all_good = False
        else:
            # Mask the key for security
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"  ✅ {key}: {masked}")
    
    print()
    return all_good


def check_data_directory():
    """Check if data directory exists."""
    print("📁 Checking data directory...\n")
    
    if settings.data_dir.exists():
        print(f"  ✅ Data directory exists: {settings.data_dir}")
        
        # Check for data files
        files = list(settings.data_dir.glob("*.json"))
        print(f"  📄 Found {len(files)} JSON files")
        
        return True
    else:
        print(f"  ⚠️  Data directory doesn't exist (will be created on first run)")
        return True


def check_imports():
    """Check if required packages are installed."""
    print("📦 Checking required packages...\n")
    
    required = [
        ("fastapi", "FastAPI"),
        ("httpx", "HTTP client for Gemini"),
        ("httpx", "HTTP client for ElevenLabs"),
        ("pydantic", "Data validation"),
    ]
    
    all_good = True
    
    for package, name in required:
        try:
            __import__(package)
            print(f"  ✅ {name} ({package})")
        except ImportError:
            print(f"  ❌ {name} ({package}) - NOT INSTALLED")
            all_good = False
    
    print()
    return all_good


def print_summary():
    """Print summary and next steps."""
    print("\n" + "="*70)
    print("📋 SETUP SUMMARY")
    print("="*70)
    
    env_ok = check_env_vars()
    dir_ok = check_data_directory()
    pkg_ok = check_imports()
    
    print("\n" + "="*70)
    
    if env_ok and dir_ok and pkg_ok:
        print("✅ ALL CHECKS PASSED! Your backend is ready to run.\n")
        print("🚀 Next Steps:")
        print("   1. Start the server:")
        print("      cd backend && python main.py")
        print()
        print("   2. Test the API:")
        print("      curl http://localhost:8000/")
        print()
        print("   3. View API docs:")
        print("      http://localhost:8000/docs")
        print()
        print("   4. Make your first call:")
        print("      POST http://localhost:8000/api/pickup/call")
        print()
        print("   📖 Full setup guide: backend/REAL_BACKEND_SETUP.md")
    else:
        print("❌ SETUP INCOMPLETE - Fix the issues above\n")
        
        if not env_ok:
            print("⚠️  Missing API keys in .env file")
            print("   → Edit backend/.env and add your keys")
            print("   → See backend/REAL_BACKEND_SETUP.md for instructions")
            print()
        
        if not pkg_ok:
            print("⚠️  Missing Python packages")
            print("   → Run: pip install -r requirements.txt")
            print()
    
    print("="*70 + "\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔧 BACKEND CONFIGURATION CHECK")
    print("="*70 + "\n")
    
    print_summary()
