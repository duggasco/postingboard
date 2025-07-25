# UUID Migration Plan - Complete Integer ID Removal

## Overview
This plan outlines the complete migration from integer IDs to UUIDs for all database relationships and application code.

## Current State
- All models have UUID columns
- API endpoints accept UUIDs
- Foreign keys still use integer IDs
- Session storage uses integer IDs
- Some JavaScript still references integer IDs

## Migration Steps

### Phase 1: Add UUID Foreign Key Columns
1. Add UUID foreign key columns alongside existing integer foreign keys:
   - `claim.idea_uuid` (references `idea.uuid`)
   - `notification.idea_uuid` (references `idea.uuid`)
   - `bounty.idea_uuid` (references `idea.uuid`)
   - `status_history.idea_uuid` (references `idea.uuid`)
   - `idea_comment.idea_uuid` (references `idea.uuid`)
   - `idea_external_link.idea_uuid` (references `idea.uuid`)
   - `idea_activity.idea_uuid` (references `idea.uuid`)
   - `idea_stage_data.idea_uuid` (references `idea.uuid`)
   - `user_profile.team_uuid` (references `team.uuid`)
   - `user_profile.managed_team_uuid` (references `team.uuid`)
   - `manager_request.requested_team_uuid` (references `team.uuid`)
   - `claim_approval.idea_uuid` (references `idea.uuid`)

2. Create new association tables:
   - `idea_skills_uuid` (idea_uuid, skill_uuid)
   - `user_skills_uuid` (user_uuid, skill_uuid)

### Phase 2: Populate UUID Foreign Keys
1. Run migration script to copy UUID values from related records
2. Verify data integrity

### Phase 3: Update Application Code
1. Update all model relationships to use UUID columns
2. Update all queries to join on UUID columns
3. Update session storage to store UUIDs instead of IDs
4. Update JavaScript to use UUIDs exclusively

### Phase 4: Drop Integer Columns
1. Drop old integer foreign key columns
2. Drop old association tables
3. Remove integer ID primary keys (keep as non-primary columns temporarily)

### Phase 5: Final Cleanup
1. Make UUID the primary key for all tables
2. Remove integer ID columns entirely
3. Update any remaining references

## Risks and Mitigation
- **Data Loss**: Create full backup before migration
- **Downtime**: Plan for maintenance window
- **Rollback**: Keep migration scripts reversible
- **Testing**: Comprehensive testing at each phase

## Implementation Order
1. Start with less critical tables (notifications, comments)
2. Move to core tables (claims, ideas)
3. Update association tables last