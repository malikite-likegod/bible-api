from datetime import datetime, timezone
from time import sleep
import threading
from sqlalchemy.orm import Session
from .database import SessionLocal  # Adjust import based on your project structure
from .models import RefreshToken  # Adjust import to your actual model location

def token_cleanup(db: Session):
    """Delete expired tokens from the database."""
    expired_tokens = db.query(RefreshToken).filter(RefreshToken.expires_at < datetime.now(timezone.utc)).all()
    for token in expired_tokens:
        db.delete(token)
    db.commit()

def start_cleanup_task(db_session_factory):
    """Starts a background thread that periodically runs the token cleanup."""
    def run():
        while True:
            db = db_session_factory()
            try:
                token_cleanup(db)
            finally:
                db.close()
            sleep(60 * 60)  # Run cleanup every hour; adjust as needed
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()