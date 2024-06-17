from datetime import datetime
from os import environ
import simplejson as json
import boto3, botocore.exceptions

def main(event, context):
    shortcode = event.get("c", "")
    ip = event.get("http", {}).get("headers", {}).get("x-forwarded-for", "unknown")
    country = event.get("http", {}).get("headers", {}).get("cf-ipcountry", "unknown")
    useragent = event.get("http", {}).get("headers", {}).get("user-agent", "unknown")
    req_id = event.get("http", {}).get("headers", {}).get("x-request-id", "unknown")
    
    s3bucket = environ.get("wasabi_bucket")
    s3key = environ.get("wasabi_accesskey")
    s3secret = environ.get("wasabi_secretkey")
    s3 = boto3.client('s3',
        endpoint_url = 'https://s3.us-west-1.wasabisys.com',
        aws_access_key_id = s3key,
        aws_secret_access_key = s3secret
    )

    targeturl = ""
    if shortcode != "":
        try:
            obj = s3.get_object(Bucket = s3bucket, Key = shortcode)
            j = json.loads(obj['Body'].read().decode('utf-8'))
            targeturl = j['target']
        except botocore.exceptions.ClientError as e:                  
            if e.response['Error']['Code'] == 'NoSuchKey':
                print(f"shortcode {shortcode} not found in db")            
        except Exception as e:
            print(f"Error reading db")
    else:
        targeturl = "https://www.google.com"
    
    if targeturl != "":
        headers = {"Location": targeturl}
        http_code = 302
        body = ""
    else:
        headers = {"Content-Type": "text/html"}
        http_code = 500
        body = f"Error getting code {shortcode}"

    return {
        "headers": headers,
        "statusCode": http_code,
        "body": body
    }
