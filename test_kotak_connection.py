#!/usr/bin/env python
"""
Test script to check Kotak Neo API connection
"""

import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_kotak_api_connection():
    """Test connection to Kotak Neo API"""
    print("=" * 60)
    print("Testing Kotak Neo API Connection")
    print("=" * 60)
    
    # API credentials
    user_id = 'client26349'
    api_key = 'L3oHgffw2uTUcyIvAiPhvjJlVWUa'
    api_secret = 'VOmGP3ofzWSBzmeAOFSgJXL1SVYa'
    
    # Test different endpoints
    base_url = "https://tradeapi.kotaksecurities.com"
    
    # Test 1: Simple GET request to check if server is reachable
    print("\n1. Testing basic connectivity...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"✓ Server reachable: {response.status_code}")
        print(f"✓ Response headers: {dict(response.headers)}")
    except Exception as e:
        print(f"✗ Server not reachable: {e}")
    
    # Test 2: Try authentication endpoint
    print("\n2. Testing authentication endpoint...")
    try:
        auth_data = {
            'userId': user_id,
            'apiKey': api_key,
            'apiSecret': api_secret
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'KotakNeoAPI/1.0'
        }
        
        response = requests.post(f"{base_url}/auth/login", json=auth_data, headers=headers, timeout=10)
        print(f"✓ Auth endpoint reachable: {response.status_code}")
        print(f"✓ Response headers: {dict(response.headers)}")
        
        # Try to parse response
        try:
            response_json = response.json()
            print(f"✓ JSON response: {response_json}")
        except:
            print(f"✓ Non-JSON response (first 200 chars): {response.text[:200]}")
            
    except Exception as e:
        print(f"✗ Auth endpoint failed: {e}")
    
    # Test 3: Try market status endpoint
    print("\n3. Testing market status endpoint...")
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'KotakNeoAPI/1.0'
        }
        
        response = requests.get(f"{base_url}/market/status", headers=headers, timeout=10)
        print(f"✓ Market status endpoint: {response.status_code}")
        print(f"✓ Response headers: {dict(response.headers)}")
        
        # Try to parse response
        try:
            response_json = response.json()
            print(f"✓ JSON response: {response_json}")
        except:
            print(f"✓ Non-JSON response (first 200 chars): {response.text[:200]}")
            
    except Exception as e:
        print(f"✗ Market status failed: {e}")
    
    # Test 4: Try with different headers
    print("\n4. Testing with API key headers...")
    try:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'KotakNeoAPI/1.0',
            'X-KS-APIKey': api_key,
            'X-KS-APISecret': api_secret,
            'X-KS-UserID': user_id
        }
        
        response = requests.get(f"{base_url}/market/status", headers=headers, timeout=10)
        print(f"✓ With API headers: {response.status_code}")
        print(f"✓ Response headers: {dict(response.headers)}")
        
        # Try to parse response
        try:
            response_json = response.json()
            print(f"✓ JSON response: {response_json}")
        except:
            print(f"✓ Non-JSON response (first 200 chars): {response.text[:200]}")
            
    except Exception as e:
        print(f"✗ With API headers failed: {e}")
    
    print("\n" + "=" * 60)
    print("Connection test completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_kotak_api_connection() 