#!/usr/bin/env python3
"""
Test Backend Functionality
===========================
Quick test script to verify all backend features work.
"""

import asyncio
import httpx

BASE_URL = "http://localhost:8000"


async def test_health():
    """Test if backend is running."""
    print("\n🔍 Testing backend health...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"✅ Backend is running: {response.json()}")
            return True
        except Exception as e:
            print(f"❌ Backend not running: {e}")
            return False


async def test_ai_health():
    """Test if AI service (Gemini) is configured."""
    print("\n🤖 Testing AI/Gemini integration...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/api/ai/health")
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Service: {data.get('service')}")
            print(f"Mock mode: {data.get('mock_mode')}")
            
            if data.get('status') == 'healthy':
                print("✅ Gemini AI is configured and working")
                return True
            else:
                print(f"⚠️  AI service status: {data.get('status')}")
                print(f"Error: {data.get('error', 'Unknown')}")
                return False
        except Exception as e:
            print(f"❌ AI service test failed: {e}")
            return False


async def test_sentiment_analysis():
    """Test Gemini sentiment analysis."""
    print("\n💭 Testing sentiment analysis...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/ai/sentiment",
                json={"text": "I am very happy with your service!"},
                timeout=30.0
            )
            data = response.json()
            print(f"✅ Sentiment analysis works!")
            print(f"Result: {data}")
            return True
        except Exception as e:
            print(f"❌ Sentiment analysis failed: {e}")
            return False


async def test_pickup_call():
    """Test initiating a pickup reminder call."""
    print("\n📞 Testing pickup call endpoint...")
    print("⚠️  This will attempt to make a REAL call to +96550525011")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/api/pickup/call",
                json={
                    "customer_name": "Test Customer",
                    "vehicle_make": "Toyota",
                    "vehicle_model": "Camry",
                    "service_type": "Oil Change",
                    "service_notes": "Service completed successfully"
                },
                timeout=30.0
            )
            
            data = response.json()
            
            if response.status_code == 200:
                print(f"✅ Call initiated successfully!")
                print(f"Call ID: {data.get('call_id')}")
                print(f"Target: {data.get('actual_phone_called')}")
                print(f"Status: {data.get('message')}")
                return True
            else:
                print(f"⚠️  Call endpoint returned: {response.status_code}")
                print(f"Response: {data}")
                return False
                
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP error: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            return False
        except Exception as e:
            print(f"❌ Pickup call test failed: {e}")
            return False


async def test_env_variables():
    """Check if required environment variables are set."""
    print("\n🔑 Checking environment variables...")
    
    from app.core.config import settings
    
    checks = {
        "GEMINI_API_KEY": settings.gemini_api_key,
        "ELEVENLABS_API_KEY": settings.elevenlabs_api_key,
        "ELEVENLABS_AGENT_ID": settings.elevenlabs_agent_id,
        "ELEVENLABS_PHONE_NUMBER_ID": settings.elevenlabs_phone_number_id,
    }
    
    all_good = True
    for key, value in checks.items():
        if not value or value == "" or "YOUR_" in value:
            print(f"❌ {key}: NOT SET")
            all_good = False
        else:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"✅ {key}: {masked}")
    
    return all_good


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 BACKEND FUNCTIONALITY TEST")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Backend health
    results['backend_health'] = await test_health()
    
    # Test 2: Environment variables (local check)
    try:
        import sys
        sys.path.insert(0, "/Users/ayaangazali/Documents/hackathons/callyala/backend")
        results['env_variables'] = await test_env_variables()
    except:
        print("⚠️  Skipping env check (run from backend directory)")
        results['env_variables'] = None
    
    # Test 3: AI health
    results['ai_health'] = await test_ai_health()
    
    # Test 4: Sentiment analysis
    if results['ai_health']:
        results['sentiment'] = await test_sentiment_analysis()
    else:
        print("\n⏭️  Skipping sentiment test (AI not configured)")
        results['sentiment'] = None
    
    # Test 5: Pickup call (optional - makes real call!)
    user_input = input("\n⚠️  Test actual phone call? (y/n): ").strip().lower()
    if user_input == 'y':
        results['pickup_call'] = await test_pickup_call()
    else:
        print("⏭️  Skipping pickup call test")
        results['pickup_call'] = None
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{status} - {test_name}")
    
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r is True)
    total = sum(1 for r in results.values() if r is not None)
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total and total > 0:
        print("🎉 All tests passed! Backend is working!")
    elif passed > 0:
        print("⚠️  Some tests failed. Check the output above.")
    else:
        print("❌ All tests failed. Backend may not be configured properly.")


if __name__ == "__main__":
    asyncio.run(main())
