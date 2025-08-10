#!/usr/bin/env python3
"""
Setup script for Browser-Voice project
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd, 
                              capture_output=True, text=True)
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def create_env_file():
    """Create .env file from template"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    env_content = """# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret

# AI Service APIs
CARTESIA_API_KEY=your_cartesia_api_key
CHATBOT_API_URL=https://api.openai.com/v1/chat/completions
CHATBOT_API_KEY=your_openai_api_key

# Twilio Configuration (for phone calls)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file - please update with your API keys")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def setup_virtual_environment():
    """Set up virtual environment for the agent"""
    venv_path = Path("Vagent/venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("Creating virtual environment...")
    if not run_command("python -m venv venv", cwd="Vagent"):
        return False
    
    # Install requirements
    if sys.platform == "win32":
        pip_path = "Vagent/venv/Scripts/pip"
    else:
        pip_path = "Vagent/venv/bin/pip"
    
    if not run_command(f"{pip_path} install -r requirements.txt", cwd="Vagent"):
        return False
    
    return True

def install_dependencies():
    """Install all project dependencies"""
    print("Installing dependencies...")
    
    # Install main requirements
    if not run_command("pip install -r requirements.txt"):
        return False
    
    # Install proxy requirements
    if not run_command("pip install -r proxy-requirements.txt"):
        return False
    
    # Install Twilio requirements
    if not run_command("pip install -r requirements.txt", cwd="twilio"):
        return False
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Browser-Voice project...")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Set up virtual environment
    if not setup_virtual_environment():
        print("❌ Failed to set up virtual environment")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update the .env file with your API keys")
    print("2. Read the README.md for detailed instructions")
    print("3. Run the proxy server: python proxy-server.py")
    print("4. Start the AI agent: cd Vagent && source venv/bin/activate && livekit-agents start-agent")
    print("5. Open public/index.html in your browser")
    print("\n🎉 Happy coding!")

if __name__ == "__main__":
    main()
