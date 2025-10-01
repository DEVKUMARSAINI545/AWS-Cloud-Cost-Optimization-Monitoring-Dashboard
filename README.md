# 🚀 AWS Cloud Cost Optimization & Monitoring Dashboard

![AWS](https://img.shields.io/badge/AWS-Cloud-orange) 
![Python](https://img.shields.io/badge/Python-3.11-blue) 
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌟 Project Overview
The **AWS Cloud Cost Optimization & Monitoring Dashboard** is a project that helps organizations:

- **Monitor**, **analyze**, and **optimize AWS cloud spending**  
- Gain **real-time insights** into costs across AWS services and regions  
- Identify **cost-saving opportunities** and reduce unnecessary expenses  

> This project provides a complete **dashboard and automated reporting system** for cloud cost management.

---

## 💡 Features
- **Real-time Cost Monitoring**: Track costs by service, account, and region  
- **Cost Alerts**: Notifications via **AWS SNS** when usage exceeds thresholds  
- **Data Visualization**: Interactive charts and dashboards using **QuickSight**  
- **Automated Reporting**: Export cost reports in **CSV**  
- **Optimization Insights**: Detect idle or underutilized resources for cost savings  

---

## 🛠 Technologies Used

| Category | Tools / Services |
|----------|-----------------|
| **Cloud** | AWS Lambda, AWS Cost Explorer API, AWS SNS, AWS S3, Amazon EventBridge|
| **Programming** | Python (Boto3) |
| **Visualization** | AWS QuickSight |

---

## ⚙ How It Works
1. **Data Collection:** AWS Lambda fetches cost data from **AWS Cost Explorer**  
2. **Data Storage:** Cost data is stored in **S3 buckets** for historical tracking  
3. **Data Processing:** Python scripts aggregate and process the data  
4. **Visualization:** Interactive dashboards display trends and usage patterns  
5. **Alerts:** AWS SNS notifies stakeholders if costs exceed predefined thresholds  

---

## 📈 Benefits
- Reduce unnecessary AWS spending  
- Gain **full visibility** into cloud usage  
- Enable **data-driven decisions** for optimization  
- Automate cost monitoring and reporting  

---

## 📝 Setup Instructions

 ## Full Steps ##
```bash
Enable AWS Cost Explorer from the Billing Dashboard.
```
**1.Create an S3 bucket to store cost reports.**
![S3 Bucket ](images/s3bucket.png)

**2.Create an SNS topic for cost alerts.**
![SNS topic ](images/s3bucket.png)

**3.Configure IAM roles for Lambda with access to Cost Explorer, S3, and SNS.**
![IAM Roles ](images/s3bucket.png)

**4.Go to AWS Lambda and create a new Lambda function.**
![IAM Roles ](images/s3bucket.png)

**5.Attach the IAM role with necessary permissions.**
![IAM Roles ](images/s3bucket.png)

**6.Write a Python script using Boto3 to fetch GetCostAndUsage from AWS Cost Explorer.**
```bash
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
```

**7.In the Lambda function, add code to save the cost data as CSV in S3:**
```bash
  bucket_name = 'mys3bucket-125600'
    file_name = f"cost_report_{datetime.today().strftime('%Y-%m-%d')}.csv"
     
    s3.put_object(
        Bucket=bucket_name,
        Key=file_name,
        Body=csv_buffer.getvalue()
    )
```
**8.In Lambda, add SNS notification when cost exceeds a threshold:**
```bash
  topic_arn = "arn:aws:sns:ap-south-1:<YOUR ACCOUNT ID>:SNS_for_cost"
    sns.publish(
        TopicArn=topic_arn,
        Subject="AWS Cost Report Generated",
        Message=f"The AWS cost report for the last 7 days has been successfully generated and saved to S3."
   )
    print(f"Saved results to s3://{bucket_name}/{file_name} and notified SNS")
    return results
```
