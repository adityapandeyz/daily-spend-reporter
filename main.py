from fastapi import FastAPI
from mangum import Mangum
import boto3
from database import engine
import models
from database import SessionLocal

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

@app.get("/daily-spend-reporter/db-url")
def get_db_url():
    ssm = boto3.client('ssm', region_name='ap-south-1')
    parameter_name = "/daily-spend-reporter/db-url"
    try:
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        db_url = response['Parameter']['Value']
        return {"db_url": db_url}
    except ssm.exceptions.ParameterNotFound:
        return {"error": f"Parameter '{parameter_name}' not found in SSM Parameter Store."}
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# The Lambda adapter
handler = Mangum(app)