import boto3
import csv
from io import StringIO
from datetime import datetime, timedelta
import json

def lambda_handler(event, context):
    # AWS clients
    ce = boto3.client('ce', region_name='us-east-1')  # Cost Explorer only works in us-east-1
    s3 = boto3.client('s3')
    sns = boto3.client('sns')

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

    # Prepare results & detect high-cost services
    results = []
    high_cost_services = []

    for day in response['ResultsByTime']:
        date = day['TimePeriod']['Start']
        for group in day['Groups']:
            service = group['Keys'][0]
            amount = float(group['Metrics']['UnblendedCost']['Amount'])
            results.append({'Date': date, 'Service': service, 'Amount': amount})
            if amount > 2:  # Threshold for high-cost
                high_cost_services.append({'Date': date, 'Service': service, 'Amount': amount})

    # Save CSV to S3
    csv_buffer = StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=['Date', 'Service', 'Amount'])
    writer.writeheader()
    writer.writerows(results)

    bucket_name = 'mys3bucket-125600'
    file_name = f"cost_report_{datetime.today().strftime('%Y-%m-%d')}.csv"
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())

    # SNS notification
    topic_arn = "arn:aws:sns:ap-south-1:952346071341:cost_optimization"
    
    # General report notification
    sns.publish(
        TopicArn=topic_arn,
        Subject="AWS Cost Report Generated",
        Message=f"The AWS cost report for the last 7 days has been successfully generated and saved to S3: s3://{bucket_name}/{file_name}"
    )

    # High-cost alert notification
    if high_cost_services:
        message = "⚠️ High Cost Alert for AWS Services (>$50):\n"
        for svc in high_cost_services:
            message += f"- {svc['Service']} on {svc['Date']}: ${svc['Amount']:.2f}\n"
        sns.publish(
            TopicArn=topic_arn,
            Subject="AWS High-Cost Service Alert",
            Message=message
        )

    print(f"Saved results to s3://{bucket_name}/{file_name} and notified SNS")
    return results
