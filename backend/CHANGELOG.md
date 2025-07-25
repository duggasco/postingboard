# Changelog

## [2.0.0] - 2025-07-25

### 🚨 BREAKING CHANGES
- **UUID Migration**: Complete migration from integer IDs to UUIDs for all entities
  - All API responses now return `uuid` field instead of `id`
  - URL patterns changed to use UUID format (e.g., `/idea/550e8400-e29b-41d4-a716-446655440000`)
  - Frontend code updated to use UUID references
  - Database migrated to UUID-based schema

### Added
- `utils.getUuid()` helper function in JavaScript for UUID handling
- `utils.formatUuid()` helper function for displaying shortened UUIDs in admin tables
- Comprehensive UUID migration guide and documentation

### Changed
- All API endpoints now return UUID-only responses
- JavaScript files updated to use `utils.getUuid()` for ID references
- Templates updated to use `.uuid` property instead of `.id`
- Admin panels now display shortened UUIDs (first 8 characters) with full UUID on mouseover
- Database primary and foreign keys converted to UUID format

### Removed
- Integer ID fields from all API responses
- Old backup files (`my_ideas_old.html`, `idea_detail.html.canvas_backup`)
- Duplicate `auth/auth/profile.html` file

### Fixed
- Variable naming inconsistencies (idea_id → idea.uuid)
- Notification field naming consistency
- JavaScript onclick handlers properly quote UUID strings

### Technical Details
- Phase 1: Fixed immediate issues with variable names and removed old files
- Phase 2: Added uuid field alongside id in API responses (transition period)
- Phase 3: Updated all JavaScript and templates to use uuid
- Phase 4: Removed id field from API responses (breaking change)
- Comprehensive testing completed with admin session

### Security Improvements
- UUIDs prevent ID enumeration attacks
- Enhanced privacy as IDs don't reveal creation order
- Better suited for distributed systems

### Migration Notes
- This is a one-way migration - rollback is not supported
- External integrations must update to use uuid field
- See UUID_MIGRATION_GUIDE.md for detailed migration information