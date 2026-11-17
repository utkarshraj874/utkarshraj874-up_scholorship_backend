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
    # Create missing tables first; create_all does not change existing tables,
    # so the idempotent ALTER statements below handle columns on old schemas.
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        # Add role column to users if not exists
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(30) NOT NULL DEFAULT 'student';"))
        
        # Add admin_remarks and verified_at to documents if not exists
        conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS admin_remarks TEXT;"))
        conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP;"))
        conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS tenth_cgpa NUMERIC(4, 2);"))
        conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS twelfth_cgpa NUMERIC(4, 2);"))
        conn.commit()
        print("Updated existing tables: users, documents")

    print("Schema changes applied successfully!")

if __name__ == "__main__":
    run_migration()
