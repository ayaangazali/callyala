#!/usr/bin/env python3
"""
Make a test call to +96550525011
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("="*70)
print("🚀 MAKING TEST CALL TO +96550525011")
print("="*70)
print()

# Test call data
call_data = {
    "customer_name": "Ahmed Al-Rashid",
    "vehicle_make": "Toyota",
    "vehicle_model": "Camry",
    "service_type": "oil change and brake inspection",
    "service_notes": "Service completed successfully. All systems checked."
}

print(f"📞 Calling: +96550525011")
print(f"👤 Customer: {call_data['customer_name']}")
print(f"🚗 Vehicle: {call_data['vehicle_make']} {call_data['vehicle_model']}")
print(f"🔧 Service: {call_data['service_type']}")
print()
print("⏳ Initiating call...")
print()

try:
    # Make the call
    response = requests.post(
        f"{BASE_URL}/api/pickup/call",
        json=call_data,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ CALL INITIATED SUCCESSFULLY!")
        print()
        print(f"  📝 Call ID: {result['call_id']}")
        print(f"  📞 Phone: {result['actual_phone_called']}")
        print(f"  💬 Message: {result['message']}")
        print()
        
        call_id = result['call_id']
        
        print("="*70)
        print("✨ Your call is being placed to +96550525011!")
        print("="*70)
        print()
        print("📊 To check call status:")
        print(f"   curl http://localhost:8000/api/pickup/status/{call_id}")
        print()
        print("📜 To get transcript:")
        print(f"   curl http://localhost:8000/api/pickup/transcript/{call_id}")
        print()
        print("📋 To list all calls:")
        print(f"   curl http://localhost:8000/api/pickup/calls")
        print()
        print("🌐 View in browser:")
        print(f"   http://localhost:8000/docs")
        print()
        
        # Wait a bit and check status
        print("⏳ Waiting 5 seconds before checking status...")
        time.sleep(5)
        
        status_response = requests.get(f"{BASE_URL}/api/pickup/status/{call_id}")
        if status_response.status_code == 200:
            status = status_response.json()
            print()
            print("📊 CALL STATUS:")
            print(f"   Status: {status['status']}")
            print(f"   Duration: {status.get('duration_seconds', 0)} seconds")
            print()
            
            if status['status'] == 'completed' and status.get('transcript'):
                print("   📜 Transcript available!")
                print(f"   Check it at: http://localhost:8000/api/pickup/transcript/{call_id}")
        
    else:
        print(f"❌ CALL FAILED: HTTP {response.status_code}")
        print(response.text)
        print()
        print("🔧 Troubleshooting:")
        print("  1. Check your .env file has all API keys")
        print("  2. Verify ElevenLabs agent ID is correct")
        print("  3. Check ElevenLabs account has calling credits")

except requests.exceptions.ConnectionError:
    print("❌ CONNECTION FAILED")
    print("   Backend is not running!")
    print()
    print("🚀 Start it with:")
    print("   cd backend && python3 main.py")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*70)
