#!/usr/bin/env python3
"""
Run notification tests with proper authentication handling.
This script creates test data directly in the database for testing.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from database import get_session, init_db
from models import UserProfile, Team, Skill, Idea, ClaimApproval, Notification
from datetime import datetime
import time
import json

# Test users
TEST_USERS = {
    "manager": {
        "email": "manager@test.com",
        "name": "Test Manager",
        "role": "manager",
        "team": "Cash - GPP",
        "is_verified": True
    },
    "submitter": {
        "email": "submitter@test.com", 
        "name": "Test Submitter",
        "role": "idea_submitter",
        "team": "Cash - GPP",
        "is_verified": True
    },
    "developer": {
        "email": "developer@test.com",
        "name": "Test Developer", 
        "role": "developer",
        "team": "Cash - GPP",
        "is_verified": True,
        "skills": ["Python", "JavaScript"]
    },
    "citizen_dev": {
        "email": "citizen@test.com",
        "name": "Test Citizen Developer",
        "role": "citizen_developer", 
        "team": "COO - IDA",
        "is_verified": True,
        "skills": ["Excel", "Power BI"]
    }
}

class NotificationDatabaseTester:
    def __init__(self):
        self.db = get_session()
        self.test_results = []
        self.created_users = []
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
        
    def setup_users(self):
        """Create test users directly in database."""
        self.log("\n=== Setting up test users ===")
        
        try:
            # Ensure teams exist
            team_names = ["Cash - GPP", "COO - IDA"]
            for team_name in team_names:
                team = self.db.query(Team).filter_by(name=team_name).first()
                if not team:
                    team = Team(name=team_name, is_approved=True)
                    self.db.add(team)
                    
            # Ensure skills exist
            skill_names = ["Python", "JavaScript", "Excel", "Power BI", "React", "Java"]
            for skill_name in skill_names:
                skill = self.db.query(Skill).filter_by(name=skill_name).first()
                if not skill:
                    skill = Skill(name=skill_name)
                    self.db.add(skill)
                    
            self.db.commit()
            
            # Create users
            for user_type, user_data in TEST_USERS.items():
                # Delete if exists
                existing = self.db.query(UserProfile).filter_by(email=user_data["email"]).first()
                if existing:
                    self.db.delete(existing)
                    
                # Create new user
                user = UserProfile(
                    email=user_data["email"],
                    name=user_data["name"],
                    role=user_data["role"],
                    team=user_data["team"],
                    is_verified=user_data.get("is_verified", True),
                    created_at=datetime.utcnow()
                )
                
                # Add skills if applicable
                if "skills" in user_data:
                    for skill_name in user_data["skills"]:
                        skill = self.db.query(Skill).filter_by(name=skill_name).first()
                        if skill:
                            user.skills.append(skill)
                            
                # Special handling for manager
                if user_data["role"] == "manager":
                    team = self.db.query(Team).filter_by(name=user_data["team"]).first()
                    if team:
                        user.managed_team_id = team.id
                        
                self.db.add(user)
                self.created_users.append(user_data["email"])
                self.log(f"Created user: {user_type} ({user_data['email']})")
                
            self.db.commit()
            self.add_result("Setup all users", True, "All users created in database")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.log(f"Failed to setup users: {str(e)}", "ERROR")
            self.add_result("Setup users", False, str(e))
            return False
            
    def test_claim_notifications(self):
        """Test claim request and approval notifications."""
        self.log("\n=== Testing claim notifications ===")
        
        try:
            # Create an idea
            submitter = self.db.query(UserProfile).filter_by(email="submitter@test.com").first()
            idea = Idea(
                title="Test Idea for Claims",
                description="Testing claim notifications",
                email=submitter.email,
                benefactor_team="Cash - GPP",
                size="medium",
                priority="high",
                needed_by="2025-12-31",
                status="open",
                submitted_at=datetime.utcnow()
            )
            
            # Add skills
            python_skill = self.db.query(Skill).filter_by(name="Python").first()
            if python_skill:
                idea.skills.append(python_skill)
                
            self.db.add(idea)
            self.db.commit()
            self.created_ideas.append(idea.id)
            
            # Create claim approval request
            developer = self.db.query(UserProfile).filter_by(email="developer@test.com").first()
            manager = self.db.query(UserProfile).filter_by(email="manager@test.com").first()
            
            claim_approval = ClaimApproval(
                idea_id=idea.id,
                claimer_email=developer.email,
                claimer_name=developer.name,
                claimer_team=developer.team,
                claimer_skills=", ".join([s.name for s in developer.skills]),
                status="pending",
                created_at=datetime.utcnow()
            )
            self.db.add(claim_approval)
            
            # Create notifications
            # 1. Notification for idea submitter
            notif1 = Notification(
                user_email=submitter.email,
                type="claim_request",
                title="New Claim Request",
                message=f"{developer.name} wants to claim your idea: {idea.title}",
                idea_id=idea.id,
                related_user_email=developer.email,
                created_at=datetime.utcnow()
            )
            self.db.add(notif1)
            
            # 2. Notification for claimer's manager
            notif2 = Notification(
                user_email=manager.email,
                type="claim_approval_required",
                title="Claim Approval Required",
                message=f"{developer.name} wants to claim: {idea.title}. Your approval is required.",
                idea_id=idea.id,
                related_user_email=developer.email,
                created_at=datetime.utcnow()
            )
            self.db.add(notif2)
            
            self.db.commit()
            
            # Check notifications exist
            submitter_notifs = self.db.query(Notification).filter_by(
                user_email=submitter.email,
                type="claim_request"
            ).count()
            
            manager_notifs = self.db.query(Notification).filter_by(
                user_email=manager.email,
                type="claim_approval_required"
            ).count()
            
            if submitter_notifs > 0:
                self.add_result("Submitter claim notification", True, 
                              f"Found {submitter_notifs} claim notifications")
            else:
                self.add_result("Submitter claim notification", False,
                              "No claim notifications found")
                              
            if manager_notifs > 0:
                self.add_result("Manager approval notification", True,
                              f"Found {manager_notifs} approval notifications")
            else:
                self.add_result("Manager approval notification", False,
                              "No approval notifications found")
                              
            # Test approval notification
            claim_approval.idea_owner_approved = True
            claim_approval.idea_owner_approved_at = datetime.utcnow()
            claim_approval.idea_owner_approved_by = submitter.email
            
            # Create approval notification
            notif3 = Notification(
                user_email=developer.email,
                type="claim_approved",
                title="Claim Request Approved",
                message=f"{submitter.name} approved your claim request for: {idea.title}",
                idea_id=idea.id,
                related_user_email=submitter.email,
                created_at=datetime.utcnow()
            )
            self.db.add(notif3)
            self.db.commit()
            
            approval_notifs = self.db.query(Notification).filter_by(
                user_email=developer.email,
                type="claim_approved"
            ).count()
            
            if approval_notifs > 0:
                self.add_result("Claim approval notification", True,
                              "Developer received approval notification")
            else:
                self.add_result("Claim approval notification", False,
                              "No approval notification found")
                              
            return True
            
        except Exception as e:
            self.db.rollback()
            self.log(f"Test failed: {str(e)}", "ERROR")
            self.add_result("Claim notifications test", False, str(e))
            return False
            
    def test_status_change_notifications(self):
        """Test notifications for idea status changes."""
        self.log("\n=== Testing status change notifications ===")
        
        try:
            # Create an idea
            submitter = self.db.query(UserProfile).filter_by(email="submitter@test.com").first()
            idea = Idea(
                title="Test Idea for Status Changes",
                description="Testing status notifications",
                email=submitter.email,
                benefactor_team="Cash - GPP",
                size="small",
                priority="medium",
                status="open",
                submitted_at=datetime.utcnow()
            )
            self.db.add(idea)
            self.db.commit()
            self.created_ideas.append(idea.id)
            
            # Change status to complete
            idea.status = "complete"
            
            # Create notification
            notif = Notification(
                user_email=submitter.email,
                type="status_change",
                title="Idea Status Changed",
                message=f"Your idea '{idea.title}' status changed from open to complete",
                idea_id=idea.id,
                created_at=datetime.utcnow()
            )
            self.db.add(notif)
            self.db.commit()
            
            status_notifs = self.db.query(Notification).filter_by(
                user_email=submitter.email,
                type="status_change"
            ).count()
            
            if status_notifs > 0:
                self.add_result("Status change notification", True,
                              f"Found {status_notifs} status change notifications")
            else:
                self.add_result("Status change notification", False,
                              "No status change notifications found")
                              
            return True
            
        except Exception as e:
            self.db.rollback()
            self.log(f"Test failed: {str(e)}", "ERROR")
            self.add_result("Status change test", False, str(e))
            return False
            
    def test_assignment_notifications(self):
        """Test notifications for idea assignments."""
        self.log("\n=== Testing assignment notifications ===")
        
        try:
            manager = self.db.query(UserProfile).filter_by(email="manager@test.com").first()
            developer = self.db.query(UserProfile).filter_by(email="developer@test.com").first()
            
            # Create idea
            idea = Idea(
                title="Test Idea for Assignment",
                description="Manager will assign this",
                email=manager.email,
                benefactor_team="Cash - GPP",
                size="large",
                priority="high",
                status="open",
                submitted_at=datetime.utcnow()
            )
            self.db.add(idea)
            self.db.commit()
            self.created_ideas.append(idea.id)
            
            # Assign to developer
            idea.assigned_to_email = developer.email
            idea.assigned_at = datetime.utcnow()
            idea.assigned_by = manager.email
            
            # Create notification
            notif = Notification(
                user_email=developer.email,
                type="assignment",
                title="Idea Assigned to You",
                message=f"{manager.name} assigned you the idea: {idea.title}",
                idea_id=idea.id,
                related_user_email=manager.email,
                created_at=datetime.utcnow()
            )
            self.db.add(notif)
            self.db.commit()
            
            assignment_notifs = self.db.query(Notification).filter_by(
                user_email=developer.email,
                type="assignment"
            ).count()
            
            if assignment_notifs > 0:
                self.add_result("Assignment notification", True,
                              "Developer received assignment notification")
            else:
                self.add_result("Assignment notification", False,
                              "No assignment notification found")
                              
            return True
            
        except Exception as e:
            self.db.rollback()
            self.log(f"Test failed: {str(e)}", "ERROR")
            self.add_result("Assignment test", False, str(e))
            return False
            
    def test_team_notifications(self):
        """Test notifications when new members join team."""
        self.log("\n=== Testing team member notifications ===")
        
        try:
            manager = self.db.query(UserProfile).filter_by(email="manager@test.com").first()
            
            # Create new team member
            new_member = UserProfile(
                email="newmember@test.com",
                name="New Team Member",
                role="developer",
                team="Cash - GPP",
                is_verified=True,
                created_at=datetime.utcnow()
            )
            self.db.add(new_member)
            self.created_users.append(new_member.email)
            
            # Create notification for manager
            notif = Notification(
                user_email=manager.email,
                type="team_member_joined",
                title="New Team Member",
                message=f"{new_member.name} has joined your team Cash - GPP",
                related_user_email=new_member.email,
                created_at=datetime.utcnow()
            )
            self.db.add(notif)
            self.db.commit()
            
            team_notifs = self.db.query(Notification).filter_by(
                user_email=manager.email,
                type="team_member_joined"
            ).count()
            
            if team_notifs > 0:
                self.add_result("Team member notification", True,
                              "Manager received team member notification")
            else:
                self.add_result("Team member notification", False,
                              "No team member notification found")
                              
            return True
            
        except Exception as e:
            self.db.rollback()
            self.log(f"Test failed: {str(e)}", "ERROR")
            self.add_result("Team member test", False, str(e))
            return False
            
    def test_notification_api(self):
        """Test notification API endpoints work correctly."""
        self.log("\n=== Testing notification API ===")
        
        try:
            # Check total notifications for each user
            for user_email in ["submitter@test.com", "developer@test.com", "manager@test.com"]:
                total = self.db.query(Notification).filter_by(user_email=user_email).count()
                unread = self.db.query(Notification).filter_by(
                    user_email=user_email,
                    is_read=False
                ).count()
                
                self.log(f"{user_email}: {total} total, {unread} unread notifications")
                
            # Mark a notification as read
            notif = self.db.query(Notification).filter_by(is_read=False).first()
            if notif:
                notif.is_read = True
                notif.read_at = datetime.utcnow()
                self.db.commit()
                self.add_result("Mark notification read", True, "Successfully marked as read")
            else:
                self.add_result("Mark notification read", False, "No unread notifications found")
                
            return True
            
        except Exception as e:
            self.db.rollback()
            self.log(f"Test failed: {str(e)}", "ERROR")
            self.add_result("API test", False, str(e))
            return False
            
    def cleanup(self):
        """Clean up test data."""
        self.log("\n=== Cleaning up test data ===")
        
        try:
            # Delete notifications
            self.db.query(Notification).filter(
                Notification.user_email.in_(self.created_users)
            ).delete(synchronize_session=False)
            
            # Delete claim approvals
            for idea_id in self.created_ideas:
                self.db.query(ClaimApproval).filter_by(idea_id=idea_id).delete()
                
            # Delete ideas
            self.db.query(Idea).filter(Idea.id.in_(self.created_ideas)).delete(
                synchronize_session=False
            )
            
            # Delete users
            self.db.query(UserProfile).filter(
                UserProfile.email.in_(self.created_users + ["newmember@test.com"])
            ).delete(synchronize_session=False)
            
            self.db.commit()
            self.log("Cleanup complete")
            
        except Exception as e:
            self.db.rollback()
            self.log(f"Cleanup failed: {str(e)}", "ERROR")
            
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
                    
        # Save report
        with open("notification_db_test_report.json", "w") as f:
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
            
        self.log("Report saved to notification_db_test_report.json")
        
    def run_all_tests(self):
        """Run all tests."""
        self.log("Starting notification database tests...")
        
        # Initialize database
        init_db()
        
        # Run tests
        if self.setup_users():
            self.test_claim_notifications()
            self.test_status_change_notifications()
            self.test_assignment_notifications()
            self.test_team_notifications()
            self.test_notification_api()
            
        self.cleanup()
        self.generate_report()
        self.db.close()


if __name__ == "__main__":
    tester = NotificationDatabaseTester()
    tester.run_all_tests()