# app/db/models/__init__.py

from app.core.database import Base # Import Base

# Import all your model classes here to register them with SQLAlchemy's Base
from app.db.models.user import User, UserToken
from app.db.models.group import Group, GroupMember
from app.db.models.journal import Journal
from app.db.models.comment import Comment
from app.db.models.media import Media

# You can also define common properties or methods here if needed