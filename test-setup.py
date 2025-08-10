#!/usr/bin/env python3
"""
Test script to verify Browser-Voice setup
"""
import sys
import os
from pathlib import Path

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    try:
        import dotenv
        print("✅ python-dotenv")
    except ImportError:
        print("❌ python-dotenv - run: pip install python-dotenv")
        return False
    
    try:
        import aiohttp
        print("✅ aiohttp")
    except ImportError:
        print("❌ aiohttp - run: pip install aiohttp")
        return False
    
    try:
        import flask
        print("✅ flask")
    except ImportError:
        print("❌ flask - run: pip install flask")
        return False
    
    try:
        import flask_cors
        print("✅ flask-cors")
    except ImportError:
        print("❌ flask-cors - run: pip install flask-cors")
        return False
    
    try:
        import requests
        print("✅ requests")
    except ImportError:
        print("❌ requests - run: pip install requests")
        return False
    
    try:
        import websockets
        print("✅ websockets")
    except ImportError:
        print("❌ websockets - run: pip install websockets")
        return False
    
    try:
        import numpy
        print("✅ numpy")
    except ImportError:
        print("❌ numpy - run: pip install numpy")
        return False
    
    # Test LiveKit imports (these might not be installed by default)
    try:
        import livekit
        print("✅ livekit")
    except ImportError:
        print("⚠️  livekit - install with: pip install livekit-agents[deepgram,openai,cartesia,silero,turn-detector]")
    
    return True

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "README.md",
        "requirements.txt",
        "proxy-requirements.txt",
        "proxy-server.py",
        "setup.py",
        "quick-start.sh",
        ".gitignore",
        "Vagent/agent.py",
        "Vagent/requirements.txt",
        "twilio/app.py",
        "twilio/bridge.py",
        "twilio/requirements.txt",
        "public/index.html",
        "public/browser-client.js"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def test_env_file():
    """Test if .env file exists and has required variables"""
    print("\n🔐 Testing environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("   Run: python setup.py or ./quick-start.sh to create it")
        return False
    
    print("✅ .env file exists")
    
    # Load and check environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY", 
        "LIVEKIT_API_SECRET",
        "CARTESIA_API_KEY",
        "CHATBOT_API_URL",
        "CHATBOT_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}":
            print(f"✅ {var}")
        else:
            print(f"⚠️  {var} - needs to be set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Please update these variables in your .env file:")
        for var in missing_vars:
            print(f"   {var}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🧪 Browser-Voice Setup Test")
    print("=" * 40)
    
    # Test imports
    imports_ok = test_imports()
    
    # Test file structure
    structure_ok = test_file_structure()
    
    # Test environment
    env_ok = test_env_file()
    
    print("\n" + "=" * 40)
    if imports_ok and structure_ok and env_ok:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n📋 Next steps:")
        print("1. Start proxy server: python proxy-server.py")
        print("2. Start AI agent: cd Vagent && source venv/bin/activate && livekit-agents start-agent")
        print("3. Open public/index.html in your browser")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        if not imports_ok:
            print("\n💡 To install missing packages: pip install -r requirements.txt")
        if not env_ok:
            print("\n💡 To set up environment: python setup.py")
    
    print("\n📖 For detailed instructions, see README.md")

if __name__ == "__main__":
    main()
