from app.db.session import Base
from app import models
# MVP uses app startup create_all in development; production can point Alembic at Base.metadata.
target_metadata=Base.metadata
