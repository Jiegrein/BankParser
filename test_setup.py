#!/usr/bin/env python3
"""
Test script to verify the bank statement parser setup
"""

import os
import sys


def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")

    try:
        import fastapi

        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import FastAPI: {e}")
        return False

    try:
        import openai

        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import OpenAI: {e}")
        return False

    try:
        import pdfplumber

        print("✅ pdfplumber imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pdfplumber: {e}")
        return False

    try:
        import pdf2image

        print("✅ pdf2image imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pdf2image: {e}")
        return False

    try:
        from app.config import get_settings

        print("✅ App configuration imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import app configuration: {e}")
        return False

    return True


def test_environment():
    """Test environment configuration"""
    print("\nTesting environment...")

    # Check if .env file exists
    if os.path.exists(".env"):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found")

    try:
        from app.config import get_settings

        settings = get_settings()

        if (
            settings.openai_api_key
            and settings.openai_api_key != "your_openai_api_key_here"
        ):
            print("✅ OpenAI API key configured")
        else:
            print("⚠️  OpenAI API key not configured")

        print(f"✅ App name: {settings.app_name}")
        print(f"✅ Host: {settings.host}:{settings.port}")

    except Exception as e:
        print(f"❌ Failed to load settings: {e}")
        return False

    return True


def test_services():
    """Test service initialization"""
    print("\nTesting services...")

    try:
        from app.services.parser_service import BankStatementParserFactory

        parser = BankStatementParserFactory.create_default_parser()
        print("✅ Parser service created successfully")
    except Exception as e:
        print(f"❌ Failed to create parser service: {e}")
        return False

    return True


def main():
    """Run all tests"""
    print("🧪 Bank Statement Parser - Setup Test\n")

    success = True

    # Test imports
    if not test_imports():
        success = False

    # Test environment
    if not test_environment():
        success = False

    # Test services
    if not test_services():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Your setup is ready.")
        print("\nTo start the API server, run:")
        print("  python run.py")
        print("\nThen visit: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\nMake sure to:")
        print("  1. Install requirements: pip install -r requirements.txt")
        print("  2. Configure .env file with your OpenAI API key")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
