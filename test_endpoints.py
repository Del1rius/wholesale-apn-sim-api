"""
Comprehensive API Endpoint Testing Suite
Tests all major endpoints across the APN & SIM Management API
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Optional

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
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

def print_subheader(text):
    print(f"\n{Colors.BOLD}{Colors.MAGENTA}{text}{Colors.RESET}")
    print(f"{Colors.MAGENTA}{'-'*len(text)}{Colors.RESET}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_response(method, endpoint, status_code, success=True):
    """Print formatted API response"""
    color = Colors.GREEN if success else Colors.RED
    symbol = "✓" if success else "✗"
    print(f"{color}{symbol} {method:6s} {endpoint:50s} [{status_code}]{Colors.RESET}")

class APITester:
    def __init__(self):
        self.tokens = {}
        self.test_results = []
        self.created_resources = {
            'apns': [],
            'sims': [],
            'usage_records': [],
            'billing_cycles': []
        }
    
    def login(self, username: str, password: str, role: str = "user") -> Optional[str]:
        """Authenticate and get JWT token"""
        print_info(f"Authenticating as {username} ({role})...")
        
        response = requests.post(
            f"{API_BASE}/auth/login/",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('tokens', {}).get('access')
            if token:
                self.tokens[role] = token
                print_success(f"Authenticated successfully as {role}")
                return token
            else:
                print_error(f"Token not found in response")
                return None
        else:
            print_error(f"Authentication failed: {response.status_code}")
            print_error(f"Response: {response.text[:200]}")
            return None
    
    def get_headers(self, role: str = "user") -> Dict[str, str]:
        """Get authorization headers for requests"""
        token = self.tokens.get(role)
        if not token:
            raise ValueError(f"No token available for role: {role}")
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def test_endpoint(self, method: str, endpoint: str, expected_status: int, 
                     role: str = "user", data: dict = None, description: str = ""):
        """Generic endpoint test helper"""
        url = f"{API_BASE}{endpoint}"
        headers = self.get_headers(role)
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = response.status_code == expected_status
            print_response(method, endpoint, response.status_code, success)
            
            if description and not success:
                print_info(f"  Description: {description}")
                print_info(f"  Expected: {expected_status}, Got: {response.status_code}")
                if response.status_code >= 400:
                    print_info(f"  Error: {response.text[:200]}")
            
            self.test_results.append({
                'method': method,
                'endpoint': endpoint,
                'expected': expected_status,
                'actual': response.status_code,
                'success': success,
                'description': description
            })
            
            return response
        
        except Exception as e:
            print_error(f"{method} {endpoint} - Exception: {str(e)}")
            self.test_results.append({
                'method': method,
                'endpoint': endpoint,
                'expected': expected_status,
                'actual': 'ERROR',
                'success': False,
                'description': description
            })
            return None
    
    # ============================================================================
    # AUTHENTICATION TESTS
    # ============================================================================
    
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print_header("AUTHENTICATION ENDPOINTS")
        
        # Test current user endpoint
        self.test_endpoint(
            "GET", "/auth/me/", 200, role="user",
            description="Get current user info"
        )
        
        # Test token refresh
        refresh_token = requests.post(
            f"{API_BASE}/auth/login/",
            json={"username": "manager_vodacom_south", "password": "TestPass123!"}
        ).json().get('tokens', {}).get('refresh')
        
        if refresh_token:
            response = requests.post(
                f"{API_BASE}/auth/token/refresh/",
                json={"refresh": refresh_token}
            )
            success = response.status_code == 200
            print_response("POST", "/auth/token/refresh/", response.status_code, success)
    
    # ============================================================================
    # APN ENDPOINTS
    # ============================================================================
    
    def test_apn_endpoints(self):
        """Test APN management endpoints"""
        print_header("APN ENDPOINTS")
        
        print_subheader("Read Operations")
        
        # List all APNs
        response = self.test_endpoint(
            "GET", "/inventory/apns/", 200, role="user",
            description="List all APNs"
        )
        
        apn_id = None
        if response and response.status_code == 200:
            apns = response.json()
            # Handle both list and paginated responses
            if isinstance(apns, dict) and 'results' in apns:
                apns = apns['results']
            if apns and len(apns) > 0:
                apn_id = apns[0].get('apn_id')
                print_info(f"  Found {len(apns)} APNs")
        
        # Get specific APN
        if apn_id:
            self.test_endpoint(
                "GET", f"/inventory/apns/{apn_id}/", 200, role="user",
                description="Get specific APN details"
            )
        
        # Test filtering
        self.test_endpoint(
            "GET", "/inventory/apns/?search=vodacom", 200, role="user",
            description="Search APNs by name"
        )
        
        print_subheader("Write Operations (Admin)")
        
        # Create new APN (admin only)
        new_apn = {
            "name": f"test_apn_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "apn_string": f"test.apn.{datetime.now().strftime('%H%M%S')}",
            "description": "Test APN created by endpoint test suite",
            "is_active": True
        }
        
        response = self.test_endpoint(
            "POST", "/inventory/apns/", 201, role="admin",
            data=new_apn,
            description="Create new APN"
        )
        
        if response and response.status_code == 201:
            created_apn = response.json()
            created_apn_id = created_apn.get('apn_id')
            self.created_resources['apns'].append(created_apn_id)
            print_info(f"  Created APN: {created_apn_id}")
            
            # Update APN
            update_data = {
                "description": "Updated description by test suite",
                "is_active": False
            }
            self.test_endpoint(
                "PATCH", f"/inventory/apns/{created_apn_id}/", 200, role="admin",
                data=update_data,
                description="Update APN"
            )
    
    # ============================================================================
    # SIM CARD ENDPOINTS
    # ============================================================================
    
    def test_sim_endpoints(self):
        """Test SIM card management endpoints"""
        print_header("SIM CARD ENDPOINTS")
        
        print_subheader("Read Operations")
        
        # List all SIMs
        response = self.test_endpoint(
            "GET", "/inventory/sims/", 200, role="user",
            description="List all SIM cards"
        )
        
        sim_id = None
        if response and response.status_code == 200:
            sims = response.json()
            # Handle both list and paginated responses
            if isinstance(sims, dict) and 'results' in sims:
                sims = sims['results']
            if sims and len(sims) > 0:
                sim_id = sims[0].get('sim_id')
                print_info(f"  Found {len(sims)} SIM cards")
        
        # Get specific SIM
        if sim_id:
            self.test_endpoint(
                "GET", f"/inventory/sims/{sim_id}/", 200, role="user",
                description="Get specific SIM details"
            )
        
        # Test filtering
        self.test_endpoint(
            "GET", "/inventory/sims/?status=assigned", 200, role="user",
            description="Filter SIMs by status"
        )
        
        # Test custom actions
        self.test_endpoint(
            "GET", "/inventory/sims/available/", 200, role="user",
            description="Get available SIMs"
        )
        
        print_subheader("Write Operations (Admin)")
        
        # Create new SIM (admin only)
        timestamp = datetime.now().strftime('%H%M%S')
        new_sim = {
            "iccid": f"89270{timestamp}000000000",  # 19 digits total
            "phone_number": f"+2781{timestamp}",
            "carrier": "Vodacom",
            "status": "available",
            "data_limit_mb": 5000
        }
        
        response = self.test_endpoint(
            "POST", "/inventory/sims/", 201, role="admin",
            data=new_sim,
            description="Create new SIM card"
        )
        
        if response and response.status_code == 201:
            created_sim = response.json()
            created_sim_id = created_sim.get('sim_id')
            self.created_resources['sims'].append(created_sim_id)
            print_info(f"  Created SIM: {created_sim_id}")
            
            # Update SIM
            update_data = {
                "status": "assigned",
                "data_limit_mb": 10000
            }
            self.test_endpoint(
                "PATCH", f"/inventory/sims/{created_sim_id}/", 200, role="admin",
                data=update_data,
                description="Update SIM card"
            )
    
    # ============================================================================
    # BILLING CYCLE ENDPOINTS
    # ============================================================================
    
    def test_billing_cycle_endpoints(self):
        """Test billing cycle endpoints"""
        print_header("BILLING CYCLE ENDPOINTS")
        
        print_subheader("Read Operations")
        
        # List billing cycles
        response = self.test_endpoint(
            "GET", "/usage/billing-cycles/", 200, role="user",
            description="List billing cycles"
        )
        
        cycle_id = None
        if response and response.status_code == 200:
            cycles = response.json()
            # Handle both list and paginated responses
            if isinstance(cycles, dict) and 'results' in cycles:
                cycles = cycles['results']
            if cycles and len(cycles) > 0:
                cycle_id = cycles[0].get('cycle_id')
                print_info(f"  Found {len(cycles)} billing cycles")
        
        # Get specific cycle
        if cycle_id:
            self.test_endpoint(
                "GET", f"/usage/billing-cycles/{cycle_id}/", 200, role="user",
                description="Get specific billing cycle"
            )
            
            # Get usage summary for cycle
            self.test_endpoint(
                "GET", f"/usage/billing-cycles/{cycle_id}/usage_summary/", 200, role="user",
                description="Get billing cycle usage summary"
            )
        
        # Get active cycles
        self.test_endpoint(
            "GET", "/usage/billing-cycles/active/", 200, role="user",
            description="Get active billing cycles"
        )
    
    # ============================================================================
    # USAGE RECORD ENDPOINTS
    # ============================================================================
    
    def test_usage_record_endpoints(self):
        """Test data usage record endpoints"""
        print_header("USAGE RECORD ENDPOINTS")
        
        print_subheader("Read Operations")
        
        # List usage records
        response = self.test_endpoint(
            "GET", "/usage/usage-records/", 200, role="user",
            description="List usage records"
        )
        
        if response and response.status_code == 200:
            records = response.json()
            # Handle both list and paginated responses
            if isinstance(records, dict) and 'results' in records:
                records = records['results']
            print_info(f"  Found {len(records)} usage records")
        
        # Get recent usage
        self.test_endpoint(
            "GET", "/usage/usage-records/recent/", 200, role="user",
            description="Get recent usage records"
        )
        
        # Get usage summary
        self.test_endpoint(
            "GET", "/usage/usage-records/summary/", 200, role="user",
            description="Get usage summary"
        )
        
        # Test filtering by date
        self.test_endpoint(
            "GET", "/usage/usage-records/?start_date=2024-01-01", 200, role="user",
            description="Filter usage records by date"
        )
        
        print_subheader("Write Operations")
        
        # Create usage record (if we have a SIM)
        response = requests.get(
            f"{API_BASE}/inventory/sims/?status=assigned",
            headers=self.get_headers("user")
        )
        
        if response.status_code == 200:
            sims = response.json()
            # Handle both list and paginated responses
            if isinstance(sims, dict) and 'results' in sims:
                sims = sims['results']
            if sims and len(sims) > 0:
                sim_id = sims[0].get('sim_id')
                
                # Get active billing cycle
                response = requests.get(
                    f"{API_BASE}/usage/billing-cycles/active/",
                    headers=self.get_headers("user")
                )
                
                if response.status_code == 200:
                    cycles = response.json()
                    # Handle both list and paginated responses
                    if isinstance(cycles, dict) and 'results' in cycles:
                        cycles = cycles['results']
                    if cycles and len(cycles) > 0:
                        cycle_id = cycles[0].get('cycle_id')
                        
                        new_usage = {
                            "sim_card": sim_id,
                            "billing_cycle": cycle_id,
                            "data_consumed_mb": 100,
                            "recorded_at": datetime.now().isoformat(),
                            "source": "api_test",
                            "notes": "Test usage record from endpoint test suite"
                        }
                        
                        response = self.test_endpoint(
                            "POST", "/usage/usage-records/", 201, role="user",
                            data=new_usage,
                            description="Create usage record"
                        )
                        
                        if response and response.status_code == 201:
                            created_record = response.json()
                            record_id = created_record.get('record_id')
                            self.created_resources['usage_records'].append(record_id)
                            print_info(f"  Created usage record: {record_id}")
    
    # ============================================================================
    # PERMISSION TESTS
    # ============================================================================
    
    def test_permissions(self):
        """Test role-based access control"""
        print_header("PERMISSION & AUTHORIZATION TESTS")
        
        # Regular user trying admin operations
        print_subheader("Regular User Access Control")
        
        new_apn = {
            "name": "unauthorized_test_apn",
            "apn_string": "unauthorized.test",
            "description": "This should not be created",
            "is_active": True
        }
        
        self.test_endpoint(
            "POST", "/inventory/apns/", 403, role="user",
            data=new_apn,
            description="Regular user cannot create APN (should get 403)"
        )
        
        # Test access to organization-specific data
        print_subheader("Organization Data Isolation")
        
        self.test_endpoint(
            "GET", "/inventory/sims/", 200, role="user",
            description="User can access their organization's SIMs"
        )
        
        self.test_endpoint(
            "GET", "/usage/usage-records/summary/", 200, role="user",
            description="User can access their organization's usage summary"
        )
    
    # ============================================================================
    # CLEANUP
    # ============================================================================
    
    def cleanup_test_data(self):
        """Clean up test resources created during testing"""
        print_header("CLEANING UP TEST DATA")
        
        # Delete created APNs
        for apn_id in self.created_resources['apns']:
            response = requests.delete(
                f"{API_BASE}/inventory/apns/{apn_id}/",
                headers=self.get_headers("admin")
            )
            if response.status_code == 204:
                print_success(f"Deleted test APN: {apn_id}")
            else:
                print_warning(f"Could not delete APN {apn_id}: {response.status_code}")
        
        # Delete created SIMs
        for sim_id in self.created_resources['sims']:
            response = requests.delete(
                f"{API_BASE}/inventory/sims/{sim_id}/",
                headers=self.get_headers("admin")
            )
            if response.status_code == 204:
                print_success(f"Deleted test SIM: {sim_id}")
            else:
                print_warning(f"Could not delete SIM {sim_id}: {response.status_code}")
        
        # Delete created usage records
        for record_id in self.created_resources['usage_records']:
            response = requests.delete(
                f"{API_BASE}/usage/usage-records/{record_id}/",
                headers=self.get_headers("admin")
            )
            if response.status_code == 204:
                print_success(f"Deleted test usage record: {record_id}")
            else:
                print_warning(f"Could not delete usage record {record_id}: {response.status_code}")
    
    # ============================================================================
    # SUMMARY
    # ============================================================================
    
    def print_summary(self):
        """Print test results summary"""
        print_header("TEST SUMMARY")
        
        passed = sum(1 for result in self.test_results if result['success'])
        failed = len(self.test_results) - passed
        
        # Group by endpoint category
        categories = {}
        for result in self.test_results:
            endpoint = result['endpoint']
            if '/auth/' in endpoint:
                category = 'Authentication'
            elif '/inventory/apns/' in endpoint:
                category = 'APN Management'
            elif '/inventory/sims/' in endpoint:
                category = 'SIM Management'
            elif '/usage/billing-cycles/' in endpoint:
                category = 'Billing Cycles'
            elif '/usage/usage-records/' in endpoint:
                category = 'Usage Records'
            else:
                category = 'Other'
            
            if category not in categories:
                categories[category] = {'passed': 0, 'failed': 0}
            
            if result['success']:
                categories[category]['passed'] += 1
            else:
                categories[category]['failed'] += 1
        
        print(f"\n{Colors.BOLD}Results by Category:{Colors.RESET}\n")
        for category, counts in categories.items():
            total = counts['passed'] + counts['failed']
            status = f"{counts['passed']}/{total}"
            color = Colors.GREEN if counts['failed'] == 0 else Colors.YELLOW
            print(f"  {category:.<40} {color}{status}{Colors.RESET}")
        
        print(f"\n{Colors.BOLD}Overall Results:{Colors.RESET}")
        print(f"  Total Tests: {len(self.test_results)}")
        print(f"  {Colors.GREEN}Passed: {passed}{Colors.RESET}")
        print(f"  {Colors.RED}Failed: {failed}{Colors.RESET}")
        
        if failed > 0:
            print(f"\n{Colors.BOLD}Failed Tests:{Colors.RESET}")
            for result in self.test_results:
                if not result['success']:
                    print(f"  {Colors.RED}✗{Colors.RESET} {result['method']} {result['endpoint']}")
                    print(f"    Expected: {result['expected']}, Got: {result['actual']}")
                    if result['description']:
                        print(f"    {result['description']}")
        
        success_rate = (passed / len(self.test_results) * 100) if self.test_results else 0
        
        print(f"\n{Colors.BOLD}Success Rate: {success_rate:.1f}%{Colors.RESET}\n")
        
        if failed == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ All endpoint tests passed!{Colors.RESET}\n")
            return 0
        else:
            print(f"{Colors.YELLOW}{Colors.BOLD}⚠ Some tests failed. Review above for details.{Colors.RESET}\n")
            return 1

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║         API ENDPOINT COMPREHENSIVE TEST SUITE                      ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}\n")
    
    print_info(f"Testing API at: {BASE_URL}")
    print_info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = APITester()
    
    # Authentication
    print_header("SETUP: AUTHENTICATION")
    regular_user_token = tester.login("manager_vodacom_south", "TestPass123!", "user")
    admin_token = tester.login("Admin", "TestPass123!", "admin")
    
    if not regular_user_token or not admin_token:
        print_error("Failed to authenticate. Cannot proceed with tests.")
        sys.exit(1)
    
    try:
        # Run all test suites
        tester.test_auth_endpoints()
        tester.test_apn_endpoints()
        tester.test_sim_endpoints()
        tester.test_billing_cycle_endpoints()
        tester.test_usage_record_endpoints()
        tester.test_permissions()
        
        # Cleanup
        tester.cleanup_test_data()
        
        # Print summary
        exit_code = tester.print_summary()
        
        return exit_code
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}Error running tests: {str(e)}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
