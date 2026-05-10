import boto3
from datetime import datetime

# Initialize the AWS clients
s3 = boto3.client('s3')
sns = boto3.client('sns')

# These are your specific resource names from our setup
BUCKET_NAME = 'rolex-spends-reports'
TOPIC_ARN = 'arn:aws:sns:ap-south-1:526362561361:SpendReportAlerts'

def deliver_report():
    # 1. Create a unique filename with a timestamp 📅
    # This prevents files from being overwritten
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_key = f"reports/spend_summary_{timestamp}.csv"
    
    # This is where your app saves the generated report in Lambda
    local_file_path = '/tmp/test.db' 

    # 2. Upload the file to S3 🗄️
    s3.upload_file(local_file_path, BUCKET_NAME, file_key)

    # 3. Send the SNS notification 📣
    report_url = f"https://s3.console.aws.amazon.com/s3/object/{BUCKET_NAME}?prefix={file_key}"
    message = f"Your spend report is ready! \n\nView it here: {report_url}"
    
    sns.publish(
        TopicArn=TOPIC_ARN,
        Message=message,
        Subject="Daily Spend Report Ready"
    )
    
    return {"status": "Success", "file": file_key}