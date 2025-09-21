# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

# Import from our other files
import models
import schemas
import crud
import security
import automation_worker
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Add CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add this to the end of backend/main.py

@app.post("/accounts/{account_id}/post")
async def create_post_for_account(
    account_id: int, 
    post: schemas.PostCreate, 
    db: Session = Depends(get_db)
):
    db_account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    plain_password = security.decrypt_password(db_account.encrypted_password)

    # Call the automation worker
    status = await automation_worker.create_post(
        db_account.username, 
        plain_password, 
        post.content
    )

    # Optional: Log this action or update a post history table in the future

    return {"account_id": account_id, "status": status}

# backend/main.py
# (All existing code for FastAPI setup and accounts endpoints remains)
# ...

# NEW ENDPOINTS FOR POSTS
@app.post("/posts/", response_model=schemas.PostResponse)
def schedule_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    return crud.create_post(db=db, post=post)

@app.get("/posts/", response_model=List[schemas.PostResponse])
def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    posts = crud.get_posts(db, skip=skip, limit=limit)
    return posts

# Endpoint to CREATE a new account
@app.post("/accounts/", response_model=schemas.AccountResponse)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_account = crud.get_account_by_username(db, username=account.username)
    if db_account:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_account(db=db, account=account)

# Endpoint to READ (List) all accounts
@app.get("/accounts/", response_model=List[schemas.AccountResponse])
def read_accounts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    accounts = crud.get_accounts(db, skip=skip, limit=limit)
    return accounts

# Endpoint to DELETE an account
@app.delete("/accounts/{account_id}", response_model=schemas.AccountResponse)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    db_account = crud.delete_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

# Endpoint to VERIFY an account's login
@app.post("/accounts/{account_id}/verify", response_model=schemas.AccountResponse)
async def verify_account_login(account_id: int, db: Session = Depends(get_db)):
    db_account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")

    plain_password = security.decrypt_password(db_account.encrypted_password)
    status = await automation_worker.verify_login(db_account.username, plain_password)
    
    db_account.status = status
    db.commit()
    db.refresh(db_account)
    
    return db_account