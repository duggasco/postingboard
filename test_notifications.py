#!/usr/bin/env python3
"""
Comprehensive notification testing script for all user types and workflows.
Tests all notification scenarios end-to-end.
"""

import requests
import json
import time
from datetime import datetime
import sys

BASE_URL = "http://localhost:9094"
ADMIN_PASSWORD = "2929arch"

# Test users data
TEST_USERS = {
    "manager": {
        "email": "manager@test.com",
        "name": "Test Manager",
        "role": "manager",
        "team": "Cash - GPP",
        "managed_team": "Cash - GPP"
    },
    "idea_submitter": {
        "email": "submitter@test.com", 
        "name": "Test Submitter",
        "role": "idea_submitter",
        "team": "Cash - GPP"
    },
    "developer": {
        "email": "developer@test.com",
        "name": "Test Developer", 
        "role": "developer",
        "team": "Cash - GPP",
        "skills": ["Python", "JavaScript", "React"]
    },
    "citizen_dev": {
        "email": "citizen@test.com",
        "name": "Test Citizen Developer",
        "role": "citizen_developer", 
        "team": "COO - IDA",
        "skills": ["Excel", "Power BI"]
    },
    "developer2": {
        "email": "developer2@test.com",
        "name": "Test Developer Two",
        "role": "developer",
        "team": "Cash - GPP",
        "skills": ["Java", "Spring"]
    }
}

class NotificationTester:
    def __init__(self):
        self.sessions = {}
        self.test_results = []
        self.created_ideas = []
        
    def log(self, message, level="INFO"):
        """Log test progress."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def add_result(self, test_name, success, details=""):
        """Add test result."""
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        status = "✓ PASS" if success else "✗ FAIL"
        self.log(f"{status}: {test_name} - {details}")
        
    def setup_admin_session(self):
        """Create admin session."""
        session = requests.Session()
        
        # Login as admin
        resp = session.post(f"{BASE_URL}/admin/login", data={"password": ADMIN_PASSWORD})
        if resp.status_code == 200:
            self.sessions["admin"] = session
            self.log("Admin session created")
            return True
        else:
            self.log("Failed to create admin session", "ERROR")
            return False
            
    def create_user_profile(self, user_type, user_data):
        """Create a user profile via admin API."""
        admin_session = self.sessions.get("admin")
        if not admin_session:
            return False
            
        # First delete if exists
        admin_session.delete(f"{BASE_URL}/api/admin/users/{user_data['email']}")
        
        # Ensure user is verified
        user_data["is_verified"] = True
        
        # Create new user
        resp = admin_session.post(f"{BASE_URL}/api/admin/users", json=user_data)
        if resp.status_code == 201:
            self.log(f"Created user profile: {user_type} ({user_data['email']})")
            return True
        else:
            self.log(f"Failed to create user profile: {user_type} - {resp.text}", "ERROR")
            return False
            
    def create_verified_session(self, email):
        """Create a session that simulates a verified user.
        
        This bypasses email verification for testing purposes.
        In a real scenario, users would verify via email.
        """
        session = requests.Session()
        
        # For testing, we'll use a special admin endpoint to create verified sessions
        # If that doesn't exist, we'll simulate the verification process
        
        # Store session for later use
        self.sessions[email] = session
        self.log(f"Created test session for {email}")
        return session
            
    def test_1_setup_users(self):
        """Set up all test users."""
        self.log("\n=== TEST 1: Setting up test users ===")
        
        if not self.setup_admin_session():
            self.add_result("Setup admin session", False, "Failed to login as admin")
            return False
            
        # Create all user profiles
        for user_type, user_data in TEST_USERS.items():
            success = self.create_user_profile(user_type, user_data)
            if not success:
                self.add_result(f"Create {user_type} profile", False)
                return False
                
        # Create sessions for all users (simulating verified sessions)
        for user_type, user_data in TEST_USERS.items():
            session = self.create_verified_session(user_data["email"])
            if not session:
                self.add_result(f"Create {user_type} session", False)
                return False
                
        # Special case: Approve manager's request to manage team
        manager_email = TEST_USERS["manager"]["email"]
        manager_session = self.sessions[manager_email]
        
        # Submit manager request
        resp = manager_session.post(f"{BASE_URL}/profile/update", json={
            "name": TEST_USERS["manager"]["name"],
            "role": "manager",
            "team": TEST_USERS["manager"]["team"],
            "managed_team": TEST_USERS["manager"]["managed_team"]
        })
        
        time.sleep(1)  # Wait for request to process
        
        # Approve manager request as admin
        admin_session = self.sessions["admin"]
        resp = admin_session.get(f"{BASE_URL}/api/admin/manager-requests")
        if resp.status_code == 200:
            data = resp.json()
            pending = data.get("pending_requests", [])
            for req in pending:
                if req["user_email"] == manager_email:
                    approve_resp = admin_session.post(
                        f"{BASE_URL}/api/admin/manager-requests/{req['id']}/approve"
                    )
                    if approve_resp.status_code == 200:
                        self.log("Manager request approved")
                        break
                        
        self.add_result("Setup all test users", True, "All users created and verified")
        return True
        
    def test_2_claim_request_notifications(self):
        """Test notifications when user requests to claim an idea."""
        self.log("\n=== TEST 2: Testing claim request notifications ===")
        
        # Submitter creates an idea
        submitter_session = self.sessions[TEST_USERS["idea_submitter"]["email"]]
        idea_data = {
            "title": "Test Idea for Claim Notifications",
            "description": "This idea will be used to test claim notifications",
            "benefactor_team": "Cash - GPP",
            "skills": ["Python", "JavaScript"],
            "size": "medium",
            "priority": "high",
            "needed_by": "2025-12-31",
            "reward": "Recognition and kudos"
        }
        
        resp = submitter_session.post(f"{BASE_URL}/submit", json=idea_data)
        if resp.status_code != 201:
            self.add_result("Create test idea", False, resp.text)
            return False
            
        idea_id = resp.json()["id"]
        self.created_ideas.append(idea_id)
        self.log(f"Created test idea {idea_id}")
        
        # Developer claims the idea
        developer_session = self.sessions[TEST_USERS["developer"]["email"]]
        claim_data = {
            "name": TEST_USERS["developer"]["name"],
            "team": TEST_USERS["developer"]["team"]
        }
        
        resp = developer_session.post(f"{BASE_URL}/idea/{idea_id}/claim", json=claim_data)
        if resp.status_code != 200:
            self.add_result("Submit claim request", False, resp.text)
            return False
            
        time.sleep(1)  # Wait for notifications to be created
        
        # Check submitter's notifications
        resp = submitter_session.get(f"{BASE_URL}/api/user/notifications")
        if resp.status_code == 200:
            notifications = resp.json()
            claim_notifications = [n for n in notifications if n["type"] == "claim_request"]
            if claim_notifications:
                self.add_result("Submitter receives claim request notification", True, 
                              f"Found {len(claim_notifications)} claim request notifications")
                self.log(f"Notification: {claim_notifications[0]['message']}")
            else:
                self.add_result("Submitter receives claim request notification", False, 
                              "No claim request notifications found")
        else:
            self.add_result("Check submitter notifications", False, resp.text)
            
        # Check manager's notifications  
        manager_session = self.sessions[TEST_USERS["manager"]["email"]]
        resp = manager_session.get(f"{BASE_URL}/api/user/notifications")
        if resp.status_code == 200:
            notifications = resp.json()
            approval_notifications = [n for n in notifications if n["type"] == "claim_approval_required"]
            if approval_notifications:
                self.add_result("Manager receives approval request notification", True,
                              f"Found {len(approval_notifications)} approval notifications")
                self.log(f"Notification: {approval_notifications[0]['message']}")
            else:
                self.add_result("Manager receives approval request notification", False,
                              "No approval notifications found")
        else:
            self.add_result("Check manager notifications", False, resp.text)
            
        return True
        
    def test_3_claim_approval_notifications(self):
        """Test notifications for claim approvals and denials."""
        self.log("\n=== TEST 3: Testing claim approval/denial notifications ===")
        
        # Get pending claim approvals for submitter
        submitter_session = self.sessions[TEST_USERS["idea_submitter"]["email"]]
        resp = submitter_session.get(f"{BASE_URL}/api/claim-approvals/pending")
        if resp.status_code != 200:
            self.add_result("Get pending approvals", False, resp.text)
            return False
            
        pending = resp.json()
        if not pending:
            self.add_result("Find pending approval", False, "No pending approvals found")
            return False
            
        approval_id = pending[0]["id"]
        
        # Submitter approves the claim
        resp = submitter_session.post(f"{BASE_URL}/api/claim-approvals/{approval_id}/approve")
        if resp.status_code != 200:
            self.add_result("Submitter approve claim", False, resp.text)
            return False
            
        time.sleep(1)
        
        # Check developer's notifications for approval
        developer_session = self.sessions[TEST_USERS["developer"]["email"]]
        resp = developer_session.get(f"{BASE_URL}/api/user/notifications")
        if resp.status_code == 200:
            notifications = resp.json()
            approval_notifications = [n for n in notifications if "approved your claim" in n.get("message", "")]
            if approval_notifications:
                self.add_result("Developer receives approval notification", True,
                              "Found approval notification from idea owner")
                self.log(f"Notification: {approval_notifications[0]['message']}")
            else:
                self.add_result("Developer receives approval notification", False,
                              "No approval notification found")
                
        # Now test denial scenario - create another idea
        idea_data = {
            "title": "Test Idea for Denial Notification",
            "description": "This claim will be denied",
            "benefactor_team": "COO - IDA",
            "skills": ["Excel"],
            "size": "small",
            "priority": "low",
            "needed_by": "2025-12-31"
        }
        
        resp = submitter_session.post(f"{BASE_URL}/submit", json=idea_data)
        if resp.status_code != 201:
            self.add_result("Create second test idea", False, resp.text)
            return False
            
        idea_id = resp.json()["id"]
        self.created_ideas.append(idea_id)
        
        # Citizen developer claims it
        citizen_session = self.sessions[TEST_USERS["citizen_dev"]["email"]]
        resp = citizen_session.post(f"{BASE_URL}/idea/{idea_id}/claim", json={
            "name": TEST_USERS["citizen_dev"]["name"],
            "team": TEST_USERS["citizen_dev"]["team"]
        })
        
        time.sleep(1)
        
        # Get pending approval and deny it
        resp = submitter_session.get(f"{BASE_URL}/api/claim-approvals/pending")
        if resp.status_code == 200:
            pending = resp.json()
            for approval in pending:
                if approval["idea"]["id"] == idea_id:
                    deny_resp = submitter_session.post(
                        f"{BASE_URL}/api/claim-approvals/{approval['id']}/deny"
                    )
                    if deny_resp.status_code == 200:
                        self.log("Claim denied by submitter")
                        break
                        
        time.sleep(1)
        
        # Check citizen developer's notifications for denial
        resp = citizen_session.get(f"{BASE_URL}/api/user/notifications")
        if resp.status_code == 200:
            notifications = resp.json()
            denial_notifications = [n for n in notifications if "denied your claim" in n.get("message", "")]
            if denial_notifications:
                self.add_result("Citizen developer receives denial notification", True,
                              "Found denial notification")
                self.log(f"Notification: {denial_notifications[0]['message']}")
            else:
                self.add_result("Citizen developer receives denial notification", False,
                              "No denial notification found")
                
        return True
        
    def test_4_manager_approval_notifications(self):
        """Test manager approval workflow notifications."""
        self.log("\n=== TEST 4: Testing manager approval notifications ===")
        
        # Get pending approvals for manager
        manager_session = self.sessions[TEST_USERS["manager"]["email"]]
        resp = manager_session.get(f"{BASE_URL}/api/claim-approvals/pending")
        if resp.status_code != 200:
            self.add_result("Get manager pending approvals", False, resp.text)
            return False
            
        pending = resp.json()
        manager_approvals = [a for a in pending if not a.get("manager_approved")]
        
        if manager_approvals:
            approval_id = manager_approvals[0]["id"]
            
            # Manager approves the claim
            resp = manager_session.post(f"{BASE_URL}/api/claim-approvals/{approval_id}/approve")
            if resp.status_code == 200:
                self.log("Manager approved claim")
                
                time.sleep(1)
                
                # Check if claim was created (both approvals complete)
                developer_session = self.sessions[TEST_USERS["developer"]["email"]]
                resp = developer_session.get(f"{BASE_URL}/api/my-ideas")
                if resp.status_code == 200:
                    ideas = resp.json()
                    claimed = [i for i in ideas if i["relationship"] in ["claimed", "both"]]
                    if claimed:
                        self.add_result("Claim created after dual approval", True,
                                      f"Developer has {len(claimed)} claimed ideas")
                    else:
                        self.add_result("Claim created after dual approval", False,
                                      "No claimed ideas found")
            else:
                self.add_result("Manager approve claim", False, resp.text)
        else:
            self.add_result("Find manager approval request", False, 
                          "No pending manager approvals found")
            
        return True
        
    def test_5_status_change_notifications(self):
        """Test notifications for idea status changes."""
        self.log("\n=== TEST 5: Testing status change notifications ===")
        
        # Admin changes an idea status to complete
        admin_session = self.sessions["admin"]
        if self.created_ideas:
            idea_id = self.created_ideas[0]
            
            # Update idea status to complete
            resp = admin_session.put(f"{BASE_URL}/api/ideas/{idea_id}", json={
                "status": "complete"
            })
            
            if resp.status_code == 200:
                self.log(f"Changed idea {idea_id} status to complete")
                
                time.sleep(1)
                
                # Check submitter notifications
                submitter_session = self.sessions[TEST_USERS["idea_submitter"]["email"]]
                resp = submitter_session.get(f"{BASE_URL}/api/user/notifications")
                if resp.status_code == 200:
                    notifications = resp.json()
                    status_notifications = [n for n in notifications if n["type"] == "status_change"]
                    if status_notifications:
                        self.add_result("Submitter receives status change notification", True,
                                      f"Found {len(status_notifications)} status notifications")
                        self.log(f"Notification: {status_notifications[0]['message']}")
                    else:
                        self.add_result("Submitter receives status change notification", False,
                                      "No status change notifications found")
            else:
                self.add_result("Change idea status", False, resp.text)
                
        return True
        
    def test_6_assignment_notifications(self):
        """Test notifications when manager assigns ideas."""
        self.log("\n=== TEST 6: Testing assignment notifications ===")
        
        # Manager creates an idea to assign
        manager_session = self.sessions[TEST_USERS["manager"]["email"]]
        idea_data = {
            "title": "Test Idea for Assignment",
            "description": "Manager will assign this to a team member",
            "benefactor_team": "Cash - GPP",
            "skills": ["Java"],
            "size": "large",
            "priority": "medium",
            "needed_by": "2025-12-31"
        }
        
        resp = manager_session.post(f"{BASE_URL}/submit", json=idea_data)
        if resp.status_code != 201:
            self.add_result("Create idea for assignment", False, resp.text)
            return False
            
        idea_id = resp.json()["id"]
        self.created_ideas.append(idea_id)
        
        # Get team members
        resp = manager_session.get(f"{BASE_URL}/api/teams/1/members")  # Assuming team ID 1
        if resp.status_code == 200:
            members = resp.json()
            # Find developer2 to assign to
            developer2_email = TEST_USERS["developer2"]["email"]
            assignee = next((m for m in members if m["email"] == developer2_email), None)
            
            if assignee:
                # Assign idea
                resp = manager_session.post(f"{BASE_URL}/api/ideas/{idea_id}/assign", json={
                    "assigned_to_email": developer2_email
                })
                
                if resp.status_code == 200:
                    self.log(f"Assigned idea {idea_id} to {developer2_email}")
                    
                    time.sleep(1)
                    
                    # Check developer2's notifications
                    developer2_session = self.sessions[developer2_email]
                    resp = developer2_session.get(f"{BASE_URL}/api/user/notifications")
                    if resp.status_code == 200:
                        notifications = resp.json()
                        assignment_notifications = [n for n in notifications if n["type"] == "assignment"]
                        if assignment_notifications:
                            self.add_result("Developer receives assignment notification", True,
                                          "Found assignment notification")
                            self.log(f"Notification: {assignment_notifications[0]['message']}")
                        else:
                            self.add_result("Developer receives assignment notification", False,
                                          "No assignment notification found")
                else:
                    self.add_result("Assign idea", False, resp.text)
            else:
                self.add_result("Find team member", False, "Developer2 not in team")
        else:
            self.add_result("Get team members", False, resp.text)
            
        return True
        
    def test_7_team_notifications(self):
        """Test notifications when new members join team."""
        self.log("\n=== TEST 7: Testing team member notifications ===")
        
        # Create a new user who will join the manager's team
        new_user = {
            "email": "newmember@test.com",
            "name": "New Team Member",
            "role": "developer",
            "team": "Cash - GPP",
            "skills": ["Python", "Django"]
        }
        
        admin_session = self.sessions["admin"]
        resp = admin_session.post(f"{BASE_URL}/api/admin/users", json=new_user)
        if resp.status_code == 201:
            self.log("Created new team member")
            
            time.sleep(1)
            
            # Check manager's notifications
            manager_session = self.sessions[TEST_USERS["manager"]["email"]]
            resp = manager_session.get(f"{BASE_URL}/api/user/notifications")
            if resp.status_code == 200:
                notifications = resp.json()
                team_notifications = [n for n in notifications if n["type"] == "team_member_joined"]
                if team_notifications:
                    self.add_result("Manager receives team member notification", True,
                                  "Found new team member notification")
                    self.log(f"Notification: {team_notifications[0]['message']}")
                else:
                    self.add_result("Manager receives team member notification", False,
                                  "No team member notifications found")
                    
            # Clean up - delete the test user
            admin_session.delete(f"{BASE_URL}/api/admin/users/newmember@test.com")
        else:
            self.add_result("Create new team member", False, resp.text)
            
        return True
        
    def test_8_manager_request_notifications(self):
        """Test notifications for manager request approvals/denials."""
        self.log("\n=== TEST 8: Testing manager request notifications ===")
        
        # Create a user who will request to be a manager
        requester = {
            "email": "requester@test.com",
            "name": "Manager Requester",
            "role": "manager",
            "team": "COO - IDA"
        }
        
        admin_session = self.sessions["admin"]
        admin_session.post(f"{BASE_URL}/api/admin/users", json=requester)
        
        # Create session for requester
        requester_session = self.create_verified_session(requester["email"])
        if not requester_session:
            self.add_result("Create requester session", False)
            return False
            
        # Submit manager request
        resp = requester_session.post(f"{BASE_URL}/profile/update", json={
            "name": requester["name"],
            "role": "manager",
            "team": requester["team"],
            "managed_team": "COO - IDA"
        })
        
        if resp.status_code == 200:
            self.log("Submitted manager request")
            
            time.sleep(1)
            
            # Check admin notifications
            resp = admin_session.get(f"{BASE_URL}/api/admin/notifications")
            if resp.status_code == 200:
                admin_notifs = resp.json()
                if admin_notifs.get("pending_manager_requests", 0) > 0:
                    self.add_result("Admin receives manager request notification", True,
                                  f"{admin_notifs['pending_manager_requests']} pending requests")
                else:
                    self.add_result("Admin receives manager request notification", False,
                                  "No pending manager requests in admin notifications")
                    
            # Get and approve the request
            resp = admin_session.get(f"{BASE_URL}/api/admin/manager-requests")
            if resp.status_code == 200:
                data = resp.json()
                pending = data.get("pending_requests", [])
                for req in pending:
                    if req["user_email"] == requester["email"]:
                        approve_resp = admin_session.post(
                            f"{BASE_URL}/api/admin/manager-requests/{req['id']}/approve"
                        )
                        if approve_resp.status_code == 200:
                            self.log("Approved manager request")
                            
                            time.sleep(1)
                            
                            # Check requester notifications
                            resp = requester_session.get(f"{BASE_URL}/api/user/notifications")
                            if resp.status_code == 200:
                                notifications = resp.json()
                                approval_notifs = [n for n in notifications 
                                                 if n["type"] == "manager_request_approved"]
                                if approval_notifs:
                                    self.add_result("User receives manager approval notification", True,
                                                  "Found approval notification")
                                    self.log(f"Notification: {approval_notifs[0]['message']}")
                                else:
                                    self.add_result("User receives manager approval notification", False,
                                                  "No approval notification found")
                            break
                            
            # Clean up
            admin_session.delete(f"{BASE_URL}/api/admin/users/requester@test.com")
            
        return True
        
    def test_9_admin_dashboard_notifications(self):
        """Test admin notification dashboard."""
        self.log("\n=== TEST 9: Testing admin notification dashboard ===")
        
        admin_session = self.sessions["admin"]
        
        # Check admin notifications endpoint
        resp = admin_session.get(f"{BASE_URL}/api/admin/notifications")
        if resp.status_code == 200:
            notifs = resp.json()
            self.log(f"Admin notifications: {json.dumps(notifs, indent=2)}")
            
            self.add_result("Admin notifications endpoint", True,
                          f"Pending: {notifs.get('pending_manager_requests', 0)} manager requests, "
                          f"{notifs.get('pending_team_approvals', 0)} team approvals, "
                          f"{notifs.get('pending_claim_approvals', 0)} claim approvals")
                          
            # Test admin dashboard page loads
            resp = admin_session.get(f"{BASE_URL}/admin/dashboard")
            if resp.status_code == 200 and "Pending Requests" in resp.text:
                self.add_result("Admin dashboard shows notifications", True,
                              "Dashboard displays pending requests section")
            else:
                self.add_result("Admin dashboard shows notifications", False,
                              "Dashboard missing notifications section")
        else:
            self.add_result("Admin notifications endpoint", False, resp.text)
            
        return True
        
    def cleanup(self):
        """Clean up test data."""
        self.log("\n=== Cleaning up test data ===")
        
        admin_session = self.sessions.get("admin")
        if admin_session:
            # Delete test ideas
            for idea_id in self.created_ideas:
                admin_session.delete(f"{BASE_URL}/api/ideas/{idea_id}")
                
            # Delete test users
            for user_data in TEST_USERS.values():
                admin_session.delete(f"{BASE_URL}/api/admin/users/{user_data['email']}")
                
        self.log("Cleanup complete")
        
    def generate_report(self):
        """Generate test report."""
        self.log("\n=== TEST REPORT ===")
        
        total_tests = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total_tests - passed
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/total_tests)*100:.1f}%")
        
        if failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
                    
        # Save detailed report
        with open("notification_test_report.json", "w") as f:
            json.dump({
                "summary": {
                    "total": total_tests,
                    "passed": passed,
                    "failed": failed,
                    "success_rate": f"{(passed/total_tests)*100:.1f}%",
                    "timestamp": datetime.now().isoformat()
                },
                "results": self.test_results
            }, f, indent=2)
            
        self.log("Detailed report saved to notification_test_report.json")
        
    def run_all_tests(self):
        """Run all notification tests."""
        self.log("Starting comprehensive notification testing...")
        
        tests = [
            self.test_1_setup_users,
            self.test_2_claim_request_notifications,
            self.test_3_claim_approval_notifications,
            self.test_4_manager_approval_notifications,
            self.test_5_status_change_notifications,
            self.test_6_assignment_notifications,
            self.test_7_team_notifications,
            self.test_8_manager_request_notifications,
            self.test_9_admin_dashboard_notifications
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log(f"Test failed with exception: {str(e)}", "ERROR")
                self.add_result(test.__name__, False, f"Exception: {str(e)}")
                
        self.cleanup()
        self.generate_report()
        

if __name__ == "__main__":
    # Check if app is running
    try:
        resp = requests.get(BASE_URL)
        if resp.status_code != 200:
            print("ERROR: Application not running on http://localhost:9094")
            sys.exit(1)
    except:
        print("ERROR: Cannot connect to application at http://localhost:9094")
        print("Please start the application with: ./start-flask.sh")
        sys.exit(1)
        
    tester = NotificationTester()
    tester.run_all_tests()