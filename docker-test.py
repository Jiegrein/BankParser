"""
Docker test script to verify the containerized application works correctly
"""

import requests
import json
import time
import sys
from pathlib import Path


def test_docker_deployment():
    """Test the Docker deployment"""
    
    print("🐳 Testing Bank Statement Parser Docker Deployment")
    print("="*60)
    
    # Test configurations
    configs = [
        {"name": "Production", "url": "http://localhost:8000"},
        {"name": "Development", "url": "http://localhost:8001"}
    ]
    
    for config in configs:
        print(f"\n🧪 Testing {config['name']} deployment...")
        test_deployment(config["url"], config["name"])


def test_deployment(base_url: str, deployment_name: str):
    """Test a specific deployment"""
    
    try:
        # Test 1: Health Check
        print(f"   1. Health check...")
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
        
        # Test 2: Root endpoint
        print(f"   2. Root endpoint...")
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Root endpoint accessible")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
        
        # Test 3: API Documentation
        print(f"   3. API documentation...")
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ API docs accessible")
        else:
            print(f"   ❌ API docs failed: {response.status_code}")
        
        # Test 4: Supported formats endpoint
        print(f"   4. Supported formats...")
        response = requests.get(f"{base_url}/api/v1/supported-formats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Supported formats: {data.get('supported_formats', [])}")
            print(f"   📊 LLM providers: {list(data.get('llm_providers', {}).keys())}")
        else:
            print(f"   ❌ Supported formats failed: {response.status_code}")
        
        # Test 5: File upload endpoint (without actual file)
        print(f"   5. File upload endpoint structure...")
        response = requests.post(f"{base_url}/api/v1/parse-statement", timeout=10)
        if response.status_code == 422:  # Expected validation error
            print(f"   ✅ File upload endpoint properly validates input")
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
        
        print(f"   🎉 {deployment_name} deployment test completed!")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Could not connect to {deployment_name} at {base_url}")
        print(f"   💡 Make sure the container is running with: docker-run.sh {deployment_name.lower()}")
        return False
    except requests.exceptions.Timeout:
        print(f"   ❌ {deployment_name} request timed out")
        return False
    except Exception as e:
        print(f"   ❌ {deployment_name} test failed: {str(e)}")
        return False


def show_deployment_info():
    """Show deployment information"""
    print("\n📋 Deployment Information")
    print("="*50)
    print("🚀 Production:")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    print("   Start: docker-run.sh run")
    print()
    print("🛠️  Development:")
    print("   URL: http://localhost:8001") 
    print("   Docs: http://localhost:8001/docs")
    print("   Start: docker-run.sh dev")
    print("   Features: Hot reload, dev tools")
    print()
    print("🐚 Container Commands:")
    print("   Logs: docker-run.sh logs")
    print("   Shell: docker-run.sh shell")
    print("   Stop: docker-run.sh stop")


def create_sample_curl_commands():
    """Show sample curl commands for testing"""
    print("\n📝 Sample API Test Commands")
    print("="*50)
    
    commands = [
        {
            "name": "Health Check",
            "command": "curl -X GET 'http://localhost:8000/api/v1/health'"
        },
        {
            "name": "Supported Formats",
            "command": "curl -X GET 'http://localhost:8000/api/v1/supported-formats'"
        },
        {
            "name": "Parse Statement (with file)",
            "command": "curl -X POST 'http://localhost:8000/api/v1/parse-statement?use_vision=true&llm_provider=openai' \\\n     -H 'Content-Type: multipart/form-data' \\\n     -F 'file=@your_bank_statement.pdf'"
        }
    ]
    
    for cmd in commands:
        print(f"\n{cmd['name']}:")
        print(f"   {cmd['command']}")


def main():
    """Main test function"""
    
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("Usage: python docker-test.py")
        print("\nThis script tests the Docker deployment of the Bank Statement Parser")
        return
    
    # Run tests
    test_docker_deployment()
    
    # Show deployment info
    show_deployment_info()
    
    # Show sample commands
    create_sample_curl_commands()
    
    print(f"\n✨ Docker testing completed!")


if __name__ == "__main__":
    main()