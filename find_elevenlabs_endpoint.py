#!/usr/bin/env python3
"""Direct test of ElevenLabs API to find correct endpoint"""
import requests
import json

API_KEY = "8bde8c82836ba08e4bcc21e149f5846ddce428274f49a8e3f044f025a0d0d439"
AGENT_ID = "agent_3501kdgfqxhjfx8bs71qmgb30dgj"
PHONE_ID = "phnum_8901kdgfqh0xec1snhwhc7ydyxyj"
PHONE = "+96550525011"

BASE_URL = "https://api.elevenlabs.io/v1"

headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}

# Try different endpoint variations
endpoints_to_try = [
    ("/convai/conversation/initiate_phone_call", {
        "agent_id": AGENT_ID,
        "phone_number_id": PHONE_ID,
        "phone_number": PHONE,
    }),
    ("/convai/conversation", {
        "agent_id": AGENT_ID,
        "phone_number_id": PHONE_ID,
        "phone_number": PHONE,
    }),
    ("/convai/agents/{}/calls".format(AGENT_ID), {
        "phone_number_id": PHONE_ID,
        "to_number": PHONE,
    }),
    ("/convai/phone_numbers/{}/make-outbound-call".format(PHONE_ID), {
        "agent_id": AGENT_ID,
        "to_number": PHONE,
    }),
    ("/convai/conversation/initiate-outbound-call", {
        "agent_id": AGENT_ID,
        "phone_number_id": PHONE_ID,
        "to_number": PHONE,
    }),
]

print("🔍 Testing ElevenLabs API endpoints...")
print(f"API Key: {API_KEY[:20]}...")
print(f"Agent ID: {AGENT_ID}")
print(f"Phone ID: {PHONE_ID}")
print()

for endpoint, payload in endpoints_to_try:
    url = BASE_URL + endpoint
    print(f"\n📍 Testing: POST {endpoint}")
    print(f"   Payload: {json.dumps(payload, indent=6)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ SUCCESS!")
            print(f"   Response: {json.dumps(response.json(), indent=6)}")
            break
        elif response.status_code == 404:
            print(f"   ❌ 404 Not Found")
        elif response.status_code == 400:
            print(f"   ⚠️  400 Bad Request")
            print(f"   Response: {response.text[:200]}")
        elif response.status_code == 401:
            print(f"   🔒 401 Unauthorized - Check API key")
        else:
            print(f"   ⚠️  {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except Exception as e:
        print(f"   💥 Error: {e}")

print("\n" + "="*60)
print("If all failed, the API might have changed or need different auth")
