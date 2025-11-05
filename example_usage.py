#!/usr/bin/env python3
"""
Example usage of the Bank Statement Parser API
"""

import json
import sys
from pathlib import Path

import requests

# API Configuration
API_BASE_URL = "http://localhost:8000"
PARSE_ENDPOINT = f"{API_BASE_URL}/api/v1/parse-statement"


def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/health")
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the server is running.")
        return False


def parse_statement(pdf_path: str, use_vision: bool = True):
    """
    Parse a bank statement PDF file

    Args:
        pdf_path: Path to the PDF file
        use_vision: Whether to use vision model (True) or text extraction (False)
    """

    # Check if file exists
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        return None

    print(f"📄 Parsing: {pdf_path}")
    print(f"🔧 Method: {'Vision (GPT-4V)' if use_vision else 'Text Extraction'}")

    try:
        # Prepare the request
        with open(pdf_path, "rb") as file:
            files = {"file": (Path(pdf_path).name, file, "application/pdf")}
            params = {"use_vision": use_vision}

            # Make the request
            print("⏳ Processing...")
            response = requests.post(
                PARSE_ENDPOINT,
                files=files,
                params=params,
                timeout=60,  # 60 second timeout
            )

        # Check response
        if response.status_code == 200:
            result = response.json()

            if result.get("success"):
                print("✅ Successfully parsed!")
                print(f"⏱️  Processing time: {result.get('processing_time', 0):.2f}s")

                # Display summary
                data = result.get("data", {})
                print("\n📊 Summary:")
                print(f"   Account Holder: {data.get('account_holder', 'N/A')}")
                print(f"   Bank: {data.get('bank_name', 'N/A')}")
                print(f"   Account: {data.get('account_number', 'N/A')}")
                print(
                    f"   Period: {
                        data.get('statement_period', {}).get('start_date', 'N/A')
                    } to {data.get('statement_period', {}).get('end_date', 'N/A')}"
                )
                print(f"   Opening Balance: ${data.get('opening_balance', 0):,.2f}")
                print(f"   Closing Balance: ${data.get('closing_balance', 0):,.2f}")
                print(f"   Transactions: {len(data.get('transactions', []))}")

                return result
            else:
                print(f"❌ Parsing failed: {result.get('error', 'Unknown error')}")
                return None
        else:
            print(f"❌ API request failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print("❌ Request timed out. The file might be too large or complex.")
        return None
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def save_result(result: dict, output_path: str):
    """Save parsing result to JSON file"""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"💾 Result saved to: {output_path}")
    except Exception as e:
        print(f"❌ Failed to save result: {str(e)}")


def main():
    """Main function"""
    print("🏦 Bank Statement Parser - Example Usage\n")

    # Check API health
    if not test_api_health():
        print("\n💡 To start the API server, run:")
        print("   python run.py")
        return 1

    # Example usage
    if len(sys.argv) < 2:
        print("Usage: python example_usage.py <path_to_pdf> [--text]")
        print("\nExample:")
        print("  python example_usage.py bank_statement.pdf")
        print("  python example_usage.py bank_statement.pdf --text")
        return 1

    pdf_path = sys.argv[1]
    use_vision = "--text" not in sys.argv

    # Parse the statement
    result = parse_statement(pdf_path, use_vision)

    if result:
        # Save result
        output_path = Path(pdf_path).stem + "_parsed.json"
        save_result(result, output_path)

        print(f"\n🎉 Done! Check {output_path} for the full result.")

    return 0 if result else 1


if __name__ == "__main__":
    sys.exit(main())

if __name__ == "__main__":
    sys.exit(main())
