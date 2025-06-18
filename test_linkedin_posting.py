"""
Test script for LinkedIn posting functionality.
"""

import asyncio
import sys
from datetime import datetime
from models.schema import ContentResponse
from utils.linkedin_client import LinkedInClient


def test_basic_post():
    """Test basic LinkedIn posting without the agent wrapper."""
    print("Testing LinkedIn Basic Post")
    print("=" * 40)
    
    # Create test content
    test_content = ContentResponse(
        content=f"🚀 Testing LinkedIn API integration at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nThis is a test post from my Python automation script. If you see this, the integration is working! #API #Python #Test"
    )
    
    try:
        # Initialize LinkedIn client
        client = LinkedInClient()
        
        # Test user profile access first
        print("1. Testing LinkedIn API authentication...")
        profile = client.get_user_profile()
        print(f"   ✅ Connected as: {profile.get('localizedFirstName', 'Unknown')} {profile.get('localizedLastName', '')}")
        
        # Post the content
        print("2. Posting content to LinkedIn...")
        result = client.post_content(test_content)
        
        # Extract post info
        post_id = result.get("id", "").replace("urn:li:ugcPost:", "")
        post_url = f"https://www.linkedin.com/feed/update/{post_id}/" if post_id else "Unknown"
        
        print(f"   ✅ Post created successfully!")
        print(f"   📱 Post ID: {post_id}")
        print(f"   🔗 Post URL: {post_url}")
        print(f"   📊 API Response: {result}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        
        # Provide specific troubleshooting tips
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            print("   💡 Tip: Check your LINKEDIN_ACCESS_TOKEN in .env file")
        elif "403" in error_str or "forbidden" in error_str:
            print("   💡 Tip: Ensure your LinkedIn app has 'w_member_social' permission")
        elif "429" in error_str:
            print("   💡 Tip: Rate limit exceeded, wait before trying again")
        elif "linkedin_access_token" in error_str:
            print("   💡 Tip: Run 'python utils/linkedin_oauth_helper.py' to get access token")
        
        return False


def test_article_post():
    """Test LinkedIn article posting."""
    print("\nTesting LinkedIn Article Post")
    print("=" * 40)
    
    # Create test article content
    test_article = ContentResponse(
        title="🤖 Testing LinkedIn API Integration",
        content=f"This is a test article posted via LinkedIn API at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n\nKey features being tested:\n• OAuth authentication\n• Article posting with title\n• Error handling\n• Response parsing\n\nIf you're seeing this, the integration is working perfectly! 🎉\n\n#API #LinkedIn #Python #Automation"
    )
    
    try:
        client = LinkedInClient()
        
        print("1. Posting article to LinkedIn...")
        result = client.post_article(test_article)
        
        post_id = result.get("id", "").replace("urn:li:ugcPost:", "")
        post_url = f"https://www.linkedin.com/feed/update/{post_id}/" if post_id else "Unknown"
        
        print(f"   ✅ Article posted successfully!")
        print(f"   📱 Post ID: {post_id}")
        print(f"   🔗 Post URL: {post_url}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


async def test_agent_posting():
    """Test LinkedIn posting through the agent wrapper."""
    print("\nTesting LinkedIn Agent")
    print("=" * 40)
    
    try:
        from agents.linkedin import post_to_linkedin
        
        # Create test content
        test_content = ContentResponse(
            content=f"🎯 Testing LinkedIn Agent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nThis post was created using the LinkedIn Agent wrapper. Features:\n• Async posting\n• Error handling\n• Structured responses\n\n#Agent #LinkedIn #Python"
        )
        
        print("1. Using LinkedIn Agent to post...")
        result = await post_to_linkedin(test_content)
        
        if result.success:
            print(f"   ✅ Agent posted successfully!")
            print(f"   📱 Post ID: {result.post_id}")
            print(f"   🔗 Post URL: {result.post_url}")
        else:
            print(f"   ❌ Agent failed: {result.error_message}")
            
        return result.success
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False


def main():
    """Run all LinkedIn posting tests."""
    print("🔧 LinkedIn Posting Test Suite")
    print("=" * 50)
    
    # Check if access token is configured
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    access_token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    if not access_token or access_token == "your_linkedin_access_token_here":
        print("❌ LinkedIn access token not configured!")
        print("\n📋 Next steps:")
        print("1. Run: python utils/linkedin_oauth_helper.py")
        print("2. Follow the OAuth flow to get your access token")
        print("3. Update LINKEDIN_ACCESS_TOKEN in your .env file")
        print("4. Run this test again")
        return
    
    print(f"✅ Access token configured (ends with: ...{access_token[-10:]})")
    print()
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Basic posting
    if test_basic_post():
        tests_passed += 1
    
    # Test 2: Article posting
    if test_article_post():
        tests_passed += 1
    
    # Test 3: Agent posting
    if asyncio.run(test_agent_posting()):
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! LinkedIn integration is working.")
        print("\n✅ You can now:")
        print("   • Use the LinkedIn agent in your workflow")
        print("   • Post content automatically after generation")
        print("   • Integrate with your main application")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\n🔧 Common fixes:")
        print("   • Verify your access token is valid")
        print("   • Check LinkedIn app permissions")
        print("   • Ensure rate limits aren't exceeded")


if __name__ == "__main__":
    main()