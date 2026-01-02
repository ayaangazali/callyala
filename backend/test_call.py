#!/usr/bin/env python3
"""
Test the pickup reminder call endpoint
=======================================
This script tests making a real call to +96550525011
"""

import httpx
import asyncio
import sys
from datetime import datetime


BASE_URL = "http://localhost:8000"


async def test_call():
    """Test making a pickup reminder call."""
    
    print("="*70)
    print("🧪 TESTING PICKUP REMINDER CALL")
    print("="*70)
    print()
    
    # Test data
    call_request = {
        "customer_name": "Ahmed Al-Rashid",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "service_type": "oil change and brake inspection",
        "service_notes": "Service completed successfully. All systems checked and working properly.",
    }
    
    print(f"📞 Initiating call to: +96550525011 (hardcoded demo number)")
    print(f"👤 Customer: {call_request['customer_name']}")
    print(f"🚗 Vehicle: {call_request['vehicle_make']} {call_request['vehicle_model']}")
    print(f"🔧 Service: {call_request['service_type']}")
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Make the call
            print("⏳ Sending request to /api/pickup/call...")
            response = await client.post(
                f"{BASE_URL}/api/pickup/call",
                json=call_request
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Call initiated successfully!")
                print()
                print(f"  📝 Call ID: {data['call_id']}")
                print(f"  📞 Phone: {data['actual_phone_called']}")
                print(f"  ⏰ Started: {data['started_at']}")
                print(f"  💬 Message: {data['message']}")
                print()
                
                call_id = data['call_id']
                
                # Wait a moment
                print("⏳ Waiting 5 seconds before checking status...")
                await asyncio.sleep(5)
                
                # Check status
                print(f"\n📊 Checking call status...")
                status_response = await client.get(
                    f"{BASE_URL}/api/pickup/status/{call_id}"
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print("✅ Status retrieved successfully!")
                    print()
                    print(f"  📊 Status: {status_data['status']}")
                    print(f"  ⏱️  Duration: {status_data.get('duration_seconds', 0)} seconds")
                    print(f"  😊 Sentiment: {status_data.get('sentiment', 'N/A')}")
                    print(f"  📅 Pickup Time: {status_data.get('pickup_time_scheduled', 'Not scheduled yet')}")
                    
                    if status_data.get('transcript'):
                        print(f"\n  📜 Transcript Preview:")
                        transcript = status_data['transcript']
                        preview = transcript[:200] + "..." if len(transcript) > 200 else transcript
                        print(f"     {preview}")
                    
                    if status_data.get('summary'):
                        print(f"\n  📝 AI Summary:")
                        print(f"     {status_data['summary']}")
                    
                else:
                    print(f"❌ Failed to get status: {status_response.status_code}")
                    print(status_response.text)
                
                print()
                print("="*70)
                print("✅ TEST COMPLETE")
                print("="*70)
                print()
                print("💡 Tips:")
                print("  - Check ElevenLabs dashboard for call details")
                print("  - View full status: GET /api/pickup/status/{call_id}")
                print("  - View all calls: GET /api/pickup/calls")
                print("  - API docs: http://localhost:8000/docs")
                print()
                
                return call_id
                
            else:
                print(f"❌ Call failed: HTTP {response.status_code}")
                print(response.text)
                print()
                print("🔧 Troubleshooting:")
                print("  1. Check your .env file has all API keys")
                print("  2. Verify ElevenLabs agent and phone number are configured")
                print("  3. Check backend logs for errors")
                print("  4. See REAL_BACKEND_SETUP.md for full setup guide")
                return None
                
        except httpx.ConnectError:
            print("❌ Connection failed - is the backend running?")
            print()
            print("🚀 Start the backend with:")
            print("   cd backend && python main.py")
            print()
            return None
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return None


async def test_health():
    """Test if backend is running."""
    print("🏥 Checking backend health...")
    
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Backend is running: {data['service']} v{data['version']}")
                print()
                return True
            else:
                print(f"⚠️  Backend responded with status {response.status_code}")
                return False
        except httpx.ConnectError:
            print("❌ Backend is not running on http://localhost:8000")
            print("   Start it with: cd backend && python main.py")
            print()
            return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False


async def main():
    """Run all tests."""
    
    # Check if backend is running
    if not await test_health():
        sys.exit(1)
    
    # Run the call test
    call_id = await test_call()
    
    if call_id:
        print("\n✨ SUCCESS! Check the call details in your dashboard")
        sys.exit(0)
    else:
        print("\n❌ TEST FAILED - see errors above")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
