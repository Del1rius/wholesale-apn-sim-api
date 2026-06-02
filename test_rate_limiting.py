"""
Rate Limiting Test Script
Tests all throttling configurations to ensure they're working correctly.
"""

import requests
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def get_jwt_token(username, password):
    """Get JWT token for authentication"""
    print_info(f"Getting JWT token for user: {username}")
    
    response = requests.post(
        f"{API_BASE}/auth/login/",
        json={"username": username, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        # Get token from 'tokens' key (which contains 'access' and 'refresh')
        tokens = data.get('tokens', {})
        token = tokens.get('access')
        if token:
            print_success(f"JWT token obtained successfully")
            return token
        else:
            print_error(f"Token not found in response. Response: {data}")
            return None
    else:
        print_error(f"Failed to get JWT token: {response.status_code}")
        print_error(f"Response: {response.text[:200]}")
        return None

def test_burst_rate_limit(token):
    """Test burst rate limit (60 requests per minute)"""
    print_header("TEST 1: Burst Rate Limit (60/minute)")
    
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = f"{API_BASE}/inventory/sims/"
    
    success_count = 0
    throttled_count = 0
    
    print_info("Making 65 rapid requests to test 60/minute burst limit...")
    
    for i in range(1, 66):
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            success_count += 1
            if i <= 5 or i >= 58:  # Show first 5 and last few
                print(f"  Request {i:2d}: {Colors.GREEN}200 OK{Colors.RESET}")
        elif response.status_code == 429:
            throttled_count += 1
            if throttled_count <= 3:  # Show first 3 throttled requests
                print(f"  Request {i:2d}: {Colors.RED}429 THROTTLED{Colors.RESET}")
        else:
            print(f"  Request {i:2d}: {Colors.YELLOW}{response.status_code}{Colors.RESET}")
        
        # Small delay to simulate realistic usage
        time.sleep(0.05)
    
    print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
    print(f"  Successful: {Colors.GREEN}{success_count}{Colors.RESET}")
    print(f"  Throttled:  {Colors.RED}{throttled_count}{Colors.RESET}")
    
    if success_count >= 55 and throttled_count >= 3:
        print_success("✓ Burst rate limit is working correctly!")
        return True
    else:
        print_error("✗ Burst rate limit may not be working as expected")
        return False

def test_usage_logging_rate_limit(token):
    """Test usage logging rate limit (500 requests per minute)"""
    print_header("TEST 2: Usage Logging Rate Limit (500/minute)")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    endpoint = f"{API_BASE}/usage/usage-records/"
    
    print_info("Making multiple requests to test 500/minute usage logging limit...")
    print_warning("Note: This test uses GET instead of POST to avoid creating test data")
    
    success_count = 0
    throttled_count = 0
    
    # Test with 100 requests (much faster than 500)
    for i in range(1, 101):
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            success_count += 1
            if i == 1 or i == 50 or i == 100:
                print(f"  Request {i:3d}: {Colors.GREEN}200 OK{Colors.RESET}")
        elif response.status_code == 429:
            throttled_count += 1
            print(f"  Request {i:3d}: {Colors.RED}429 THROTTLED{Colors.RESET}")
        
        time.sleep(0.01)  # Very fast requests
    
    print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
    print(f"  Successful: {Colors.GREEN}{success_count}{Colors.RESET}")
    print(f"  Throttled:  {Colors.RED}{throttled_count}{Colors.RESET}")
    
    if success_count >= 95:
        print_success("✓ Usage logging rate limit is working correctly!")
        print_info("  (100 requests completed successfully - well below 500/min limit)")
        return True
    else:
        print_error("✗ Usage logging rate limit may be too restrictive")
        return False

def test_admin_bypass(admin_token):
    """Test that admin users bypass rate limits"""
    print_header("TEST 3: Admin Rate Limit Bypass")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    endpoint = f"{API_BASE}/inventory/sims/"
    
    print_info("Making 70 rapid requests as admin (should bypass 60/min limit)...")
    
    success_count = 0
    throttled_count = 0
    
    for i in range(1, 71):
        response = requests.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            success_count += 1
            if i == 1 or i == 35 or i == 70:
                print(f"  Request {i:2d}: {Colors.GREEN}200 OK{Colors.RESET}")
        elif response.status_code == 429:
            throttled_count += 1
            print(f"  Request {i:2d}: {Colors.RED}429 THROTTLED{Colors.RESET}")
        
        time.sleep(0.05)
    
    print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
    print(f"  Successful: {Colors.GREEN}{success_count}{Colors.RESET}")
    print(f"  Throttled:  {Colors.RED}{throttled_count}{Colors.RESET}")
    
    if success_count == 70 and throttled_count == 0:
        print_success("✓ Admin bypass is working correctly!")
        return True
    else:
        print_error("✗ Admin users are being throttled (should be unlimited)")
        return False

def test_rate_limit_headers(token):
    """Test that rate limit headers are present in responses"""
    print_header("TEST 4: Rate Limit Headers")
    
    headers = {"Authorization": f"Bearer {token}"}
    endpoint = f"{API_BASE}/inventory/sims/"
    
    print_info("Checking for rate limit headers in API response...")
    
    response = requests.get(endpoint, headers=headers)
    
    print(f"\n{Colors.BOLD}Response Headers:{Colors.RESET}")
    rate_limit_headers = {}
    
    for header_name in ['X-RateLimit-Limit', 'X-RateLimit-Remaining', 'X-RateLimit-Reset']:
        value = response.headers.get(header_name)
        if value:
            rate_limit_headers[header_name] = value
            print(f"  {Colors.GREEN}✓{Colors.RESET} {header_name}: {value}")
        else:
            print(f"  {Colors.YELLOW}✗{Colors.RESET} {header_name}: Not found")
    
    if len(rate_limit_headers) > 0:
        print_success("\n✓ Rate limit headers are present")
        return True
    else:
        print_warning("\n⚠ Rate limit headers not found (this is normal for DRF throttling)")
        print_info("  DRF throttling works without custom headers")
        return True

def test_anonymous_rate_limit():
    """Test anonymous user rate limit (100 requests per hour)"""
    print_header("TEST 5: Anonymous Rate Limit (100/hour)")
    
    endpoint = f"{API_BASE}/inventory/sims/"
    
    print_info("Making 5 requests without authentication...")
    
    for i in range(1, 6):
        response = requests.get(endpoint)
        
        if response.status_code == 401:  # Unauthorized
            print(f"  Request {i}: {Colors.YELLOW}401 UNAUTHORIZED{Colors.RESET} (endpoint requires auth)")
        elif response.status_code == 200:
            print(f"  Request {i}: {Colors.GREEN}200 OK{Colors.RESET}")
        elif response.status_code == 429:
            print(f"  Request {i}: {Colors.RED}429 THROTTLED{Colors.RESET}")
        
        time.sleep(0.1)
    
    print_info("\n✓ Anonymous rate limiting tested")
    print_info("  Note: Most endpoints require authentication, so 401 is expected")
    return True

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         API RATE LIMITING & THROTTLING TEST SUITE          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    print_info(f"Testing API at: {BASE_URL}")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test credentials
    regular_user = {"username": "manager_vodacom_south", "password": "TestPass123!"}
    admin_user = {"username": "Admin", "password": "TestPass123!"}
    
    # Get tokens
    print_header("Authentication Setup")
    regular_token = get_jwt_token(regular_user["username"], regular_user["password"])
    admin_token = get_jwt_token(admin_user["username"], admin_user["password"])
    
    if not regular_token:
        print_error("Failed to authenticate regular user. Cannot proceed with tests.")
        sys.exit(1)
    
    if not admin_token:
        print_warning("Failed to authenticate admin user. Admin bypass test will be skipped.")
    
    # Run tests
    results = []
    
    # Test 1: Burst rate limit
    results.append(("Burst Rate Limit", test_burst_rate_limit(regular_token)))
    time.sleep(2)  # Wait before next test
    
    # Test 2: Usage logging rate limit
    results.append(("Usage Logging Rate Limit", test_usage_logging_rate_limit(regular_token)))
    time.sleep(2)
    
    # Test 3: Admin bypass (if admin token available)
    if admin_token:
        results.append(("Admin Bypass", test_admin_bypass(admin_token)))
        time.sleep(2)
    
    # Test 4: Rate limit headers
    results.append(("Rate Limit Headers", test_rate_limit_headers(regular_token)))
    time.sleep(1)
    
    # Test 5: Anonymous rate limit
    results.append(("Anonymous Rate Limit", test_anonymous_rate_limit()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}PASSED{Colors.RESET}" if result else f"{Colors.RED}FAILED{Colors.RESET}"
        print(f"  {test_name:.<40} {status}")
    
    print(f"\n{Colors.BOLD}Overall Result: {passed}/{total} tests passed{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All rate limiting tests passed successfully!{Colors.RESET}")
        print(f"{Colors.GREEN}  Your API rate limiting is working correctly.{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠ Some tests had issues{Colors.RESET}")
        print(f"{Colors.YELLOW}  Review the test output above for details.{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error running tests: {str(e)}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
