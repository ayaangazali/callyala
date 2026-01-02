#!/usr/bin/env python3
"""Quick test script to verify calling works"""
import requests
import json
import sys

API_URL = "http://localhost:8000"

def test_call():
    print("🧪 Testing Call API...")
    print(f"Target: {API_URL}/api/pickup/call")
    print(f"Phone: +96550525011 (hardcoded)")
    print()
    
    payload = {
        "customer_name": "Test Customer",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry"
    }
    
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    print("📞 Making call request...")
    
    try:
        response = requests.post(
            f"{API_URL}/api/pickup/call",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(json.dumps(result, indent=2))
            print()
            print(f"📱 Call ID: {result.get('call_id')}")
            print(f"📞 Phone called: {result.get('actual_phone_called', '+96550525011')}")
            print()
            print("🎉 The call should be going through to +96550525011 right now!")
            return 0
        else:
            print("❌ FAILED!")
            print(f"Response: {response.text}")
            return 1
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend!")
        print("Make sure backend is running: cd backend && python3 main.py")
        return 1
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_call())
