"""
UUID utility functions for dual ID support during migration.
"""

import re
import uuid as uuid_lib
from typing import Union, Optional

# UUID regex pattern
UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)

def is_valid_uuid(value: Union[str, int]) -> bool:
    """Check if a value is a valid UUID."""
    if isinstance(value, int):
        return False
    return bool(UUID_PATTERN.match(str(value)))

def is_valid_id(value: Union[str, int]) -> bool:
    """Check if a value is a valid integer ID."""
    try:
        int(str(value))
        return True
    except ValueError:
        return False

def get_by_identifier(model_class, identifier: Union[str, int], db):
    """
    Get a model instance by UUID only.
    Integer ID support has been removed for security.
    """
    if is_valid_uuid(identifier):
        # Only UUID lookup is allowed
        return db.query(model_class).filter(model_class.uuid == str(identifier)).first()
    else:
        return None

def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid_lib.uuid4())

def ensure_uuid(model_instance) -> str:
    """
    Ensure a model instance has a UUID, generating one if needed.
    Returns the UUID string.
    """
    if not hasattr(model_instance, 'uuid') or not model_instance.uuid:
        model_instance.uuid = generate_uuid()
    return model_instance.uuid

def get_identifier_for_url(model_instance) -> str:
    """
    Get the appropriate identifier for URL generation.
    During migration, this returns UUID if available, otherwise integer ID.
    """
    if hasattr(model_instance, 'uuid') and model_instance.uuid:
        return model_instance.uuid
    return str(model_instance.id)

def migrate_foreign_key_to_uuid(
    db, 
    table_name: str,
    column_name: str,
    target_model,
    new_column_name: Optional[str] = None
):
    """
    Helper to migrate a foreign key column from integer to UUID.
    Creates a new column with UUID references.
    """
    from sqlalchemy import text
    
    if not new_column_name:
        new_column_name = f"{column_name}_uuid"
    
    # Add new UUID column
    try:
        db.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {new_column_name} VARCHAR(36)"))
        db.commit()
    except Exception as e:
        if "already exists" not in str(e).lower():
            raise
    
    # Populate UUID values based on integer foreign keys
    query = text(f"""
        UPDATE {table_name} t
        SET {new_column_name} = (
            SELECT uuid FROM {target_model.__tablename__} 
            WHERE id = t.{column_name}
        )
        WHERE {column_name} IS NOT NULL
        AND {new_column_name} IS NULL
    """)
    
    db.execute(query)
    db.commit()

# Decorator to ensure only UUID identifiers are accepted
def uuid_only(f):
    """Decorator to ensure route only accepts UUID identifiers."""
    from functools import wraps
    from flask import jsonify, redirect, url_for, flash, request
    
    @wraps(f)
    def decorated_function(identifier, *args, **kwargs):
        if not is_valid_uuid(identifier):
            # Check if this is an API call or web request
            if request and request.path.startswith('/api/'):
                return jsonify({'error': 'Invalid identifier format'}), 400
            else:
                flash('Invalid identifier', 'error')
                return redirect(url_for('main.home'))
        return f(identifier, *args, **kwargs)
    
    return decorated_function