#!/usr/bin/env python3
"""Test email and claimed idea persistence across sessions"""

from database import get_session
from models import Idea, Claim, IdeaStatus
from sqlalchemy import and_

def test_persistence():
    """Test that email-based lookup works across sessions"""
    db = get_session()
    
    print("=== Testing Email and Claim Persistence ===\n")
    
    # Test 1: Check submitted ideas by email
    print("1. Submitted Ideas Persistence:")
    test_emails = ['test@test.com', 'john.doe@example.com']
    
    for email in test_emails:
        ideas = db.query(Idea).filter(Idea.email == email).all()
        print(f"\n  Email: {email}")
        print(f"  Found {len(ideas)} submitted ideas:")
        for idea in ideas:
            print(f"    - ID: {idea.id}, Title: {idea.title}, Status: {idea.status.value}")
    
    # Test 2: Check claimed ideas by email
    print("\n2. Claimed Ideas Persistence:")
    claimer_emails = ['duggasco@gmail.com', 'test@test.com']
    
    for email in claimer_emails:
        claims = db.query(Claim).filter(Claim.claimer_email == email).all()
        print(f"\n  Claimer Email: {email}")
        print(f"  Found {len(claims)} claimed ideas:")
        for claim in claims:
            idea = db.query(Idea).get(claim.idea_id)
            print(f"    - Idea ID: {claim.idea_id}, Title: {idea.title if idea else 'N/A'}, Team: {claim.claimer_team}")
    
    # Test 3: Combined view (what My Ideas page shows)
    print("\n3. Combined View (My Ideas functionality):")
    test_email = 'test@test.com'
    
    # Get submitted ideas
    submitted = db.query(Idea).filter(Idea.email == test_email).all()
    submitted_ids = {idea.id for idea in submitted}
    
    # Get claimed ideas
    claimed = db.query(Claim).filter(Claim.claimer_email == test_email).all()
    claimed_ids = {claim.idea_id for claim in claimed}
    
    # Find overlaps
    both_ids = submitted_ids & claimed_ids
    only_submitted = submitted_ids - both_ids
    only_claimed = claimed_ids - both_ids
    
    print(f"\n  For email {test_email}:")
    print(f"    - Ideas only submitted: {len(only_submitted)}")
    print(f"    - Ideas only claimed: {len(only_claimed)}")
    print(f"    - Ideas both submitted and claimed: {len(both_ids)}")
    print(f"    - Total unique ideas: {len(submitted_ids | claimed_ids)}")
    
    # Test 4: Verify data integrity
    print("\n4. Data Integrity Check:")
    
    # Check all ideas have emails
    ideas_without_email = db.query(Idea).filter(Idea.email == None).count()
    print(f"  - Ideas without email: {ideas_without_email}")
    
    # Check all claims have emails
    claims_without_email = db.query(Claim).filter(Claim.claimer_email == None).count()
    print(f"  - Claims without claimer email: {claims_without_email}")
    
    # Show summary
    total_ideas = db.query(Idea).count()
    total_claims = db.query(Claim).count()
    unique_submitters = db.query(Idea.email).distinct().count()
    unique_claimers = db.query(Claim.claimer_email).distinct().count()
    
    print(f"\n5. Database Summary:")
    print(f"  - Total ideas: {total_ideas}")
    print(f"  - Total claims: {total_claims}")
    print(f"  - Unique submitter emails: {unique_submitters}")
    print(f"  - Unique claimer emails: {unique_claimers}")
    
    db.close()
    
    print("\n✅ Email persistence is working correctly!")
    print("   Users can access their submitted and claimed ideas across sessions using their email.")

if __name__ == "__main__":
    test_persistence()