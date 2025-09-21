# backend/scheduler.py
import time
from datetime import datetime, timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy.orm import Session
from sqlalchemy.sql import func # MODIFIED: Added this import

import crud
import models
import automation_worker
import security
from database import SessionLocal

def run_scheduled_post(db: Session, post: models.Post):
    """The logic to run a single scheduled post job."""
    print(f"--- Running post ID: {post.id} ---")
    post.status = "processing"
    db.commit()

    all_accounts = crud.get_accounts(db)
    success_count = 0
    
    for account in all_accounts:
        print(f"Posting for account: {account.username}")
        try:
            plain_password = security.decrypt_password(account.encrypted_password)
            import asyncio
            status = asyncio.run(automation_worker.create_post(
                account.username,
                plain_password,
                post.content
            ))
            if status == "Post Successful":
                success_count += 1
        except Exception as e:
            print(f"Error posting for account {account.username}: {e}")

    post.status = f"Completed ({success_count}/{len(all_accounts)} successful)"
    db.commit()
    print(f"--- Finished post ID: {post.id} ---")


def check_for_posts_to_run():
    """The main job that the scheduler runs every minute."""
    print(f"[{datetime.now()}] Scheduler running: Checking for pending posts...")
    db = SessionLocal()
    try:
        # Find posts that are scheduled for the past and are still pending
        posts_to_run = db.query(models.Post).filter(
            # MODIFIED: Using the database's own NOW() function for a reliable time comparison
            models.Post.scheduled_at <= func.now(),
            models.Post.status == 'pending'
        ).all()

        if not posts_to_run:
            print("No posts to run at this time.")
            return

        for post in posts_to_run:
            run_scheduled_post(db, post)
    finally:
        db.close()

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(check_for_posts_to_run, 'interval', minutes=1, misfire_grace_time=60)
    print("Scheduler started. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass