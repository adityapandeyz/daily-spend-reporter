import boto3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def fetch_db_url_from_aws():
    ssm = boto3.client('ssm', region_name='ap-south-1')
    parameter_name = "/daily-spend-reporter/db-url"
    try:
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        return response['Parameter']['Value']
    except ssm.exceptions.ParameterNotFound:
        # Fallback for local testing if AWS isn't reachable
        return "sqlite:///./test.db"

# 1. Fetch the URL dynamically
SQLALCHEMY_DATABASE_URL = fetch_db_url_from_aws()

# 2. Create the Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Create a Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. The Base class
Base = declarative_base()