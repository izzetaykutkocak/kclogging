#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Endpoints

Test script to verify all Flask blueprint endpoints.
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000/immutable_logs"

def test_stream_endpoint():
    """Test the streaming API endpoint."""
    print("\n=== Testing Stream Endpoint ===")
    url = f"{BASE_URL}/api/stream?start=0&count=5"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total Lines: {data.get('total_lines')}")
            print(f"Lines Returned: {data.get('count')}")
            print(f"Has More: {data.get('has_more')}")
            print(f"First Line: {data['lines'][0] if data.get('lines') else 'No lines'}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_stream_with_validation():
    """Test streaming with validation enabled."""
    print("\n=== Testing Stream with Validation ===")
    url = f"{BASE_URL}/api/stream?start=0&count=3&validate=true"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Lines Returned: {data.get('count')}")
            if data.get('lines'):
                line = data['lines'][0]
                print(f"Line has 'is_valid' field: {'is_valid' in line}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_verify_endpoint():
    """Test the integrity verification endpoint."""
    print("\n=== Testing Verify Endpoint ===")
    url = f"{BASE_URL}/api/verify"
    try:
        response = requests.post(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Valid: {data.get('valid')}")
            print(f"Total Lines: {data.get('total_lines')}")
            print(f"Tampered Lines: {data.get('tampered_lines')}")
            print(f"Check Duration: {data.get('check_duration_ms')} ms")
            print(f"File Size: {data.get('file_size')}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_download_endpoint():
    """Test the download endpoint."""
    print("\n=== Testing Download Endpoint ===")
    url = f"{BASE_URL}/api/download"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            print(f"Content-Disposition: {response.headers.get('Content-Disposition')}")
            print(f"Content Length: {len(response.content)} bytes")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

def test_view_endpoint():
    """Test the view endpoint."""
    print("\n=== Testing View Endpoint ===")
    url = f"{BASE_URL}/view"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            print(f"Response Length: {len(response.text)} bytes")
            print(f"Contains 'log_viewer': {'log_viewer' in response.text.lower()}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

if __name__ == '__main__':
    print("Testing Flask Blueprint Endpoints")
    print("=" * 50)
    
    time.sleep(1)
    
    results = {
        'stream': test_stream_endpoint(),
        'stream_validation': test_stream_with_validation(),
        'verify': test_verify_endpoint(),
        'download': test_download_endpoint(),
        'view': test_view_endpoint()
    }
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:20s}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("All tests passed!" if all_passed else "Some tests failed!"))
