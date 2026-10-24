import sys
from pathlib import Path
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from sqlalchemy import text
from backend.app.core.database import engine
from backend.app.models import Base

def run_migration():
    print("Running database migration...")
    with engine.connect() as conn:
        # Add role column to users if not exists
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(30) NOT NULL DEFAULT 'student';"))
        
        # Add admin_remarks and verified_at to documents if not exists
        conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS admin_remarks TEXT;"))
        conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP;"))
        conn.commit()
        print("Updated existing tables: users, documents")

    # Create new tables: notifications, help_queries
    Base.metadata.create_all(bind=engine)
    print("Created any missing tables successfully!")

if __name__ == "__main__":
    run_migration()
