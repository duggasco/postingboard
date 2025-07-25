# UUID Migration Research

## Current State Analysis

### Models Using Integer IDs
1. **Idea** - Primary entity, referenced by many others
2. **Skill** - Referenced in many-to-many relationships
3. **Team** - Referenced by UserProfile
4. **Claim** - References Idea
5. **UserProfile** - Uses email as unique identifier, but has integer ID
6. **VerificationCode** - References UserProfile by email
7. **ManagerRequest** - References UserProfile and Team
8. **ClaimApproval** - References Idea
9. **EmailSettings** - Standalone entity
10. **Notification** - References Idea
11. **Bounty** - References Idea
12. **StatusHistory** - References Idea
13. **IdeaComment** - References Idea
14. **IdeaExternalLink** - References Idea
15. **IdeaActivity** - References Idea
16. **IdeaStageData** - References Idea

### Foreign Key Relationships
- `idea_skills` table: idea_id → Idea.id, skill_id → Skill.id
- `user_skills` table: user_id → UserProfile.id, skill_id → Skill.id
- Multiple tables reference Idea.id
- UserProfile references team_id and managed_team_id

### Route Patterns Using IDs
- `/idea/<int:idea_id>` - Individual idea pages
- `/api/ideas/<int:idea_id>/...` - Various API endpoints
- `/api/teams/<int:team_id>/...` - Team-related endpoints
- `/api/skills/<int:skill_id>` - Skill management

## UUID Benefits
1. **Security**: Non-enumerable, preventing sequential attacks
2. **Privacy**: Cannot guess other entity IDs
3. **Distributed Systems**: Can generate IDs without database coordination
4. **Merging Data**: No conflicts when merging databases

## UUID Drawbacks
1. **Storage**: 16 bytes vs 4 bytes for integer
2. **Index Performance**: Slightly slower due to size
3. **URL Length**: Longer URLs (36 characters)
4. **Readability**: Harder to work with during debugging

## Implementation Strategy

### 1. Database Changes
- Add UUID columns alongside existing integer IDs
- Populate UUIDs for existing records
- Update foreign keys to use UUIDs
- Remove integer ID columns after migration

### 2. SQLAlchemy Considerations
- Use `sqlalchemy.dialects.postgresql.UUID` or generic UUID type
- Python `uuid.uuid4()` for generation
- String representation for SQLite compatibility

### 3. Migration Approach
- **Phase 1**: Add UUID columns, keep integer IDs
- **Phase 2**: Dual-write to both ID types
- **Phase 3**: Update all references to use UUIDs
- **Phase 4**: Remove integer ID columns

### 4. Code Changes Required
- Model definitions
- Route handlers
- API endpoints
- Frontend JavaScript
- URL generation
- Query filters

## Testing Strategy
1. Unit tests for UUID generation
2. Migration script testing
3. API endpoint testing
4. Frontend functionality testing
5. Performance benchmarking