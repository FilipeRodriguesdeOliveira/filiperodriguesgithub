#!/usr/bin/env python3
"""
ELION MARKET 360 - Backend API Testing
Tests all backend endpoints for the marketing automation platform
"""

import requests
import sys
import json
from datetime import datetime
import time

class ElionAPITester:
    def __init__(self, base_url="https://elionmarket.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
        if details and not success:
            print(f"    Details: {details}")

    def make_request(self, method, endpoint, data=None, expected_status=200):
        """Make HTTP request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                return False, f"Status {response.status_code}: {response.text}"

        except Exception as e:
            return False, f"Request failed: {str(e)}"

    def test_health_check(self):
        """Test if backend is accessible"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            success = response.status_code in [200, 404]  # 404 is ok for root endpoint
            self.log_test("Backend Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.log_test("Backend Health Check", False, str(e))
            return False

    def test_user_registration(self):
        """Test user registration"""
        test_email = f"test_{int(time.time())}@elion.com"
        user_data = {
            "email": test_email,
            "password": "Test123!",
            "name": "Test User"
        }
        
        success, response = self.make_request('POST', 'auth/register', user_data, 200)
        
        if success and isinstance(response, dict):
            if 'token' in response and 'user' in response:
                self.token = response['token']
                self.user_id = response['user']['id']
                self.log_test("User Registration", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("User Registration", False, "Missing token or user in response")
                return False
        else:
            self.log_test("User Registration", False, str(response))
            return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        login_data = {
            "email": "test@elion.com",
            "password": "Test123!"
        }
        
        success, response = self.make_request('POST', 'auth/login', login_data, 200)
        
        if success and isinstance(response, dict):
            if 'token' in response:
                # Use existing test user if available
                self.token = response['token']
                self.user_id = response['user']['id']
                self.log_test("User Login", True, f"User ID: {self.user_id}")
                return True
            else:
                self.log_test("User Login", False, "Missing token in response")
                return False
        else:
            self.log_test("User Login", False, str(response))
            return False

    def test_get_user_profile(self):
        """Test getting current user profile"""
        if not self.token:
            self.log_test("Get User Profile", False, "No auth token available")
            return False
            
        success, response = self.make_request('GET', 'auth/me', expected_status=200)
        
        if success and isinstance(response, dict):
            if 'id' in response and 'email' in response:
                self.log_test("Get User Profile", True, f"Email: {response['email']}")
                return True
            else:
                self.log_test("Get User Profile", False, "Missing user data in response")
                return False
        else:
            self.log_test("Get User Profile", False, str(response))
            return False

    def test_create_connection(self):
        """Test creating platform connections"""
        if not self.token:
            self.log_test("Create Connection", False, "No auth token available")
            return False

        platforms = ['meta', 'google_ads', 'ga4', 'website']
        success_count = 0
        
        for platform in platforms:
            conn_data = {
                "platform": platform,
                "credentials": {"api_key": f"demo_key_{platform}"}
            }
            
            success, response = self.make_request('POST', 'connections', conn_data, 200)
            
            if success and isinstance(response, dict):
                if 'id' in response and response['platform'] == platform:
                    success_count += 1
                    self.log_test(f"Create Connection - {platform}", True, f"Connection ID: {response['id']}")
                else:
                    self.log_test(f"Create Connection - {platform}", False, "Invalid response structure")
            else:
                self.log_test(f"Create Connection - {platform}", False, str(response))
        
        return success_count == len(platforms)

    def test_get_connections(self):
        """Test retrieving connections"""
        if not self.token:
            self.log_test("Get Connections", False, "No auth token available")
            return False
            
        success, response = self.make_request('GET', 'connections', expected_status=200)
        
        if success and isinstance(response, list):
            self.log_test("Get Connections", True, f"Found {len(response)} connections")
            return True
        else:
            self.log_test("Get Connections", False, str(response))
            return False

    def test_create_goal(self):
        """Test creating marketing goals"""
        if not self.token:
            self.log_test("Create Goal", False, "No auth token available")
            return False

        objectives = ['leads', 'brand', 'followers', 'sales']
        success_count = 0
        
        for objective in objectives:
            goal_data = {
                "objective": objective,
                "target_value": 1000,
                "description": f"Test goal for {objective}"
            }
            
            success, response = self.make_request('POST', 'goals', goal_data, 200)
            
            if success and isinstance(response, dict):
                if 'id' in response and response['objective'] == objective:
                    success_count += 1
                    self.log_test(f"Create Goal - {objective}", True, f"Goal ID: {response['id']}")
                else:
                    self.log_test(f"Create Goal - {objective}", False, "Invalid response structure")
            else:
                self.log_test(f"Create Goal - {objective}", False, str(response))
        
        return success_count == len(objectives)

    def test_get_goals(self):
        """Test retrieving goals"""
        if not self.token:
            self.log_test("Get Goals", False, "No auth token available")
            return False
            
        success, response = self.make_request('GET', 'goals', expected_status=200)
        
        if success and isinstance(response, list):
            self.log_test("Get Goals", True, f"Found {len(response)} goals")
            return True
        else:
            self.log_test("Get Goals", False, str(response))
            return False

    def test_get_data_collection(self):
        """Test retrieving collected data"""
        if not self.token:
            self.log_test("Get Data Collection", False, "No auth token available")
            return False
            
        success, response = self.make_request('GET', 'data-collection', expected_status=200)
        
        if success and isinstance(response, list):
            self.log_test("Get Data Collection", True, f"Found {len(response)} data entries")
            return True
        else:
            self.log_test("Get Data Collection", False, str(response))
            return False

    def test_ai_analysis(self):
        """Test AI analysis functionality"""
        if not self.token:
            self.log_test("AI Analysis", False, "No auth token available")
            return False

        ai_types = ['brain', 'niche', 'strategy', 'campaign', 'metrics', 'optimizer', 'crm']
        success_count = 0
        
        for ai_type in ai_types:
            analysis_data = {
                "type": ai_type,
                "context": {"test": True}
            }
            
            print(f"    Testing AI analysis for {ai_type}... (this may take a few seconds)")
            success, response = self.make_request('POST', 'ai/analyze', analysis_data, 200)
            
            if success and isinstance(response, dict):
                if 'id' in response and 'analysis' in response:
                    success_count += 1
                    self.log_test(f"AI Analysis - {ai_type}", True, f"Analysis ID: {response['id']}")
                else:
                    self.log_test(f"AI Analysis - {ai_type}", False, "Invalid response structure")
            else:
                self.log_test(f"AI Analysis - {ai_type}", False, str(response))
        
        return success_count > 0  # At least one AI analysis should work

    def test_get_analyses(self):
        """Test retrieving AI analyses"""
        if not self.token:
            self.log_test("Get Analyses", False, "No auth token available")
            return False
            
        success, response = self.make_request('GET', 'ai/analyses', expected_status=200)
        
        if success and isinstance(response, list):
            self.log_test("Get Analyses", True, f"Found {len(response)} analyses")
            return True
        else:
            self.log_test("Get Analyses", False, str(response))
            return False

    def test_create_campaign(self):
        """Test creating campaigns"""
        if not self.token:
            self.log_test("Create Campaign", False, "No auth token available")
            return False

        campaign_data = {
            "name": "Test Campaign",
            "platform": "meta",
            "objective": "leads",
            "structure": {"budget": 100, "duration": "7 days"}
        }
        
        success, response = self.make_request('POST', 'campaigns', campaign_data, 200)
        
        if success and isinstance(response, dict):
            if 'id' in response and response['name'] == campaign_data['name']:
                self.log_test("Create Campaign", True, f"Campaign ID: {response['id']}")
                return True
            else:
                self.log_test("Create Campaign", False, "Invalid response structure")
                return False
        else:
            self.log_test("Create Campaign", False, str(response))
            return False

    def test_get_campaigns(self):
        """Test retrieving campaigns"""
        if not self.token:
            self.log_test("Get Campaigns", False, "No auth token available")
            return False
            
        success, response = self.make_request('GET', 'campaigns', expected_status=200)
        
        if success and isinstance(response, list):
            self.log_test("Get Campaigns", True, f"Found {len(response)} campaigns")
            return True
        else:
            self.log_test("Get Campaigns", False, str(response))
            return False

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        if not self.token:
            self.log_test("Dashboard Stats", False, "No auth token available")
            return False
            
        success, response = self.make_request('GET', 'dashboard/stats', expected_status=200)
        
        if success and isinstance(response, dict):
            expected_keys = ['connections', 'total_campaigns', 'active_campaigns']
            if all(key in response for key in expected_keys):
                self.log_test("Dashboard Stats", True, f"Stats: {response}")
                return True
            else:
                self.log_test("Dashboard Stats", False, "Missing expected keys in response")
                return False
        else:
            self.log_test("Dashboard Stats", False, str(response))
            return False

    def run_all_tests(self):
        """Run comprehensive backend testing"""
        print("🚀 Starting ELION MARKET 360 Backend Testing")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_health_check():
            print("❌ Backend is not accessible. Stopping tests.")
            return False
        
        # Authentication tests
        auth_success = False
        if self.test_user_registration():
            auth_success = True
        elif self.test_user_login():
            auth_success = True
        
        if not auth_success:
            print("❌ Authentication failed. Stopping tests.")
            return False
            
        self.test_get_user_profile()
        
        # Core functionality tests
        self.test_create_connection()
        self.test_get_connections()
        self.test_create_goal()
        self.test_get_goals()
        self.test_get_data_collection()
        
        # AI functionality tests (may take longer)
        print("\n🤖 Testing AI functionality...")
        self.test_ai_analysis()
        self.test_get_analyses()
        
        # Campaign and metrics tests
        self.test_create_campaign()
        self.test_get_campaigns()
        self.test_dashboard_stats()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} passed")
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ Backend testing completed successfully!")
            return True
        else:
            print("❌ Backend has significant issues that need attention.")
            return False

def main():
    """Main test execution"""
    tester = ElionAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total_tests': tester.tests_run,
                'passed_tests': tester.tests_passed,
                'success_rate': (tester.tests_passed / tester.tests_run) * 100 if tester.tests_run > 0 else 0,
                'timestamp': datetime.now().isoformat()
            },
            'detailed_results': tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())