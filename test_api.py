#!/usr/bin/env python3
"""
Quick test script for Wan2.2 S2V API with authentication

Usage:
    python test_api.py https://your-app.modal.run your-api-key
"""

import requests
import sys
import json


def test_health(base_url):
    """Test health endpoint (no auth)"""
    print("Testing /health endpoint...")
    response = requests.get(f"{base_url}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_root(base_url):
    """Test root endpoint (no auth)"""
    print("\nTesting / endpoint...")
    response = requests.get(f"{base_url}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200


def test_auth_missing(base_url):
    """Test generate-video without API key (should fail)"""
    print("\nTesting /generate-video without API key (should fail)...")
    response = requests.post(f"{base_url}/generate-video")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 401


def test_auth_invalid(base_url):
    """Test generate-video with invalid API key (should fail)"""
    print("\nTesting /generate-video with invalid API key (should fail)...")
    headers = {"X-API-Key": "invalid-key-12345"}
    response = requests.post(f"{base_url}/generate-video", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 403


def test_auth_valid(base_url, api_key):
    """Test generate-video with valid API key (should get 422 for missing files)"""
    print("\nTesting /generate-video with valid API key...")
    headers = {"X-API-Key": api_key}
    response = requests.post(f"{base_url}/generate-video", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    # Should get 422 (missing required files) not 401/403
    return response.status_code == 422


def main():
    if len(sys.argv) < 3:
        print("Usage: python test_api.py <base_url> <api_key>")
        print("Example: python test_api.py https://your-app.modal.run your-api-key")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    api_key = sys.argv[2]
    
    print("=" * 70)
    print("Wan2.2 S2V API Authentication Test")
    print("=" * 70)
    print(f"Base URL: {base_url}")
    print(f"API Key: {api_key[:8]}..." if len(api_key) > 8 else f"API Key: {api_key}")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health(base_url)))
    results.append(("Root Info", test_root(base_url)))
    results.append(("Auth - Missing Key", test_auth_missing(base_url)))
    results.append(("Auth - Invalid Key", test_auth_invalid(base_url)))
    results.append(("Auth - Valid Key", test_auth_valid(base_url, api_key)))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("=" * 70)
    
    # Overall result
    all_passed = all(result[1] for result in results)
    if all_passed:
        print("✅ All tests passed! API authentication is working correctly.")
    else:
        print("❌ Some tests failed. Check the output above.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
