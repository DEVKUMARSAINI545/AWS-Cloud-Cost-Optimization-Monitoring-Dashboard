import boto3
import csv
from io import StringIO
from datetime import datetime, timedelta
import json
def lambda_handler(event, context):
    # Connect to Cost Explorer in us-east-1
    ce = boto3.client('ce', region_name='us-east-1')
    s3 = boto3.client('s3')
    sns = boto3.client('sns')  # SNS client
    # Last 7 days
    start = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
    end = datetime.today().strftime('%Y-%m-%d')
    
    # Fetch daily cost per service
    response = ce.get_cost_and_usage(
        TimePeriod={'Start': start, 'End': end},
        Granularity='DAILY',
        Metrics=['UnblendedCost'],
        GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
    )
    
    # Prepare results
    results = [
        {
            'Date': day['TimePeriod']['Start'],
            'Service': group['Keys'][0],
            'Amount': group['Metrics']['UnblendedCost']['Amount']
        }
        for day in response['ResultsByTime']
        for group in day['Groups']
    ]
    csv_buffer = StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=['Date', 'Service', 'Amount'])
    writer.writeheader()
    writer.writerows(results)

    bucket_name = 'mys3bucket-125600'
    file_name = f"cost_report_{datetime.today().strftime('%Y-%m-%d')}.csv"
     
    s3.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=csv_buffer.getvalue()
    )
    topic_arn = "arn:aws:sns:ap-south-1:<ACCOUNT NO>:SNS_for_cost"
    sns.publish(
        TopicArn=topic_arn,
        Subject="AWS Cost Report Generated",
        Message=f"The AWS cost report for the last 7 days has been successfully generated and saved to S3."
   )
    print(f"Saved results to s3://{bucket_name}/{file_name} and notified SNS")
    return results
