#!/usr/bin/env python3
"""
Setup script for Bank Statement Parser
"""

import os
import subprocess
import sys


def run_command(command, description):
    """Run a command and return success status"""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    major, minor = sys.version_info[:2]

    if major >= 3 and minor >= 8:
        print(f"✅ Python {major}.{minor} is compatible")
        return True
    else:
        print(f"❌ Python {major}.{minor} is not compatible. Requires Python 3.8+")
        return False


def install_dependencies():
    """Install Python dependencies"""
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies",
    )


def check_env_file():
    """Check and setup .env file"""
    print("🔧 Checking environment configuration...")

    if not os.path.exists(".env"):
        print("❌ .env file not found")
        return False

    # Read .env file
    with open(".env", "r") as f:
        content = f.read()

    if "your_openai_api_key_here" in content:
        print("⚠️  OpenAI API key not configured in .env file")
        print("   Please edit .env and add your OpenAI API key")
        return False
    else:
        print("✅ Environment configuration looks good")
        return True


def run_tests():
    """Run setup tests"""
    return run_command(f"{sys.executable} test_setup.py", "Running setup tests")


def main():
    """Main setup function"""
    print("🚀 Bank Statement Parser - Setup Script\n")

    success = True

    # Check Python version
    if not check_python_version():
        success = False

    # Install dependencies
    if success and not install_dependencies():
        success = False

    # Check environment
    env_ok = check_env_file()

    # Run tests if dependencies are installed
    if success:
        test_ok = run_command(f"{sys.executable} test_setup.py", "Running setup tests")
        if not test_ok:
            success = False

    print("\n" + "=" * 60)

    if success and env_ok:
        print("🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("  1. Start the API server: python run.py")
        print("  2. Visit: http://localhost:8000/docs")
        print("  3. Upload a bank statement PDF to test")
    elif success and not env_ok:
        print("⚠️  Setup completed with warnings!")
        print("\n📋 Next steps:")
        print("  1. Edit .env file and add your OpenAI API key")
        print("  2. Start the API server: python run.py")
        print("  3. Visit: http://localhost:8000/docs")
    else:
        print("❌ Setup failed!")
        print("\n🔧 Troubleshooting:")
        print("  1. Make sure Python 3.8+ is installed")
        print("  2. Check your internet connection")
        print("  3. Try running: pip install -r requirements.txt")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
