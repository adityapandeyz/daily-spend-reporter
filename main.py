from fastapi import Depends, FastAPI, HTTPException, status
from mangum import Mangum
import boto3
import models
import schemas
from database import SessionLocal, engine
from sqlalchemy import func
from sqlalchemy.orm import Session

app = FastAPI(
    title="Daily Spend Reporter",
    description="Track and report daily spending by category",
    version="1.0.0"
)

models.Base.metadata.create_all(bind=engine)

@app.get("/")
def health_check():
    return {"status": "Intern-Project-Active", "message": "FastAPI is running!"}

@app.get("/check-bucket")
def check_s3_bucket():
    """Check available S3 buckets in AWS account"""
    try:
        s3 = boto3.client('s3', region_name='ap-south-1')
        response = s3.list_buckets()
        buckets = [bucket['Name'] for bucket in response['Buckets']]
        return {"my_buckets": buckets}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch S3 buckets: {str(e)}"
        )
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/spend/", response_model=schemas.SpendResponse, status_code=status.HTTP_201_CREATED)
def create_spend_entry(spend: schemas.SpendCreate, db: Session = Depends(get_db)):
    """Create a new spend entry"""
    db_entry = models.SpendEntry(
        amount=spend.amount,
        category=spend.category,
        description=spend.description
    )
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

@app.get("/spend/", response_model=list[schemas.SpendResponse])
def read_spend_entries(db: Session = Depends(get_db), limit: int = 100):
    """Get all spend entries with pagination"""
    entries = db.query(models.SpendEntry).limit(limit).all()
    return entries

@app.get("/spend/{entry_id}", response_model=schemas.SpendResponse)
def read_spend_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(models.SpendEntry).filter(models.SpendEntry.id == entry_id).first()
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Spend entry with id {entry_id} not found"
        )
    return entry

@app.get('/spend/report/total', response_model=schemas.TotalSpendResponse)
def total_spend_report(db: Session = Depends(get_db)):
    """Get total spending across all entries"""
    total = db.query(models.SpendEntry).with_entities(func.sum(models.SpendEntry.amount)).scalar()
    return {"total_spend": total or 0}

@app.get('/spend/report/category_totals_today', response_model=schemas.CategoryTotalsResponse)
def category_totals_today(db: Session = Depends(get_db)):
    """Get spending totals by category for today"""
    from datetime import date
    today = date.today()
    results = db.query(
        models.SpendEntry.category,
        func.sum(models.SpendEntry.amount).label('total')
    ).filter(func.date(models.SpendEntry.created_at) == today).group_by(
        models.SpendEntry.category
    ).all()
    
    return {
        "category_totals_today": [
            {"category": r[0], "total": r[1]} for r in results
        ]
    }

# The Lambda adapter
handler = Mangum(app)