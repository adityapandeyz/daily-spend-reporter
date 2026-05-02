from fastapi import Depends, FastAPI
from mangum import Mangum
import boto3
from database import engine
import models
from database import SessionLocal
import schemas
from sqlalchemy.orm import Session
from database import engine
from sqlalchemy import func

app = FastAPI(title="Daily Spend Reporter")

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def health_check():
    return {"status": "Intern-Project-Active", "message": "FastAPI is running!"}

@app.get("/check-bucket")
def check_s3_bucket():
    # Using boto3 to talk to S3
    s3 = boto3.client('s3', region_name='ap-south-1')
    response = s3.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    return {"my_buckets": buckets}
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/spend/")
def create_spend_entry(spend: schemas.SpendCreate, db: SessionLocal = Depends(get_db)):
    db_entry = models.SpendEntry(
        amount=spend.amount,
        category=spend.category,
        description=spend.description
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@app.get("/spend/")
def read_spend_entries(db: SessionLocal = Depends(get_db)):
    entries = db.query(models.SpendEntry).all()
    return entries

@app.get("/spend/{entry_id}")
def read_spend_entry(entry_id: int, db: SessionLocal = Depends(get_db)):
    entry = db.query(models.SpendEntry).filter(models.SpendEntry.id == entry_id).first()
    if entry is None:
        return {"error": "Entry not found"}
    return entry

@app.get('/spend/report/total')
def total_spend_report(db: SessionLocal = Depends(get_db)):
    total = db.query(models.SpendEntry).with_entities(func.sum(models.SpendEntry.amount)).scalar()
    return {"total_spend": total}

@app.get('/spend/report/category_totals_today')
def category_totals_today(db: SessionLocal = Depends(get_db)):
    from datetime import date
    today = date.today()
    results = db.query(
        models.SpendEntry.category,
        func.sum(models.SpendEntry.amount).label('total')
    ).filter(func.date(models.SpendEntry.created_at) == today).group_by(models.SpendEntry.category).all()
    
    return {"category_totals_today": [{"category": r[0], "total": r[1]} for r in results]}

# The Lambda adapter
handler = Mangum(app)