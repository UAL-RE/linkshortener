from datetime import datetime
from os import environ
import random
import string
import simplejson as json
import boto3, botocore.exceptions

def main(event, context):

      # Only allow authenticated requests
      accesstoken = event.get("t", "")
      if accesstoken != environ.get("token"):
            return {
                  "headers": {"Content-Type": "text/html"},
                  "statusCode": 403,
                  "body": "Forbidden"
            }

      urltoshorten = event.get("u", "")
      xtraparam = event.get("p", "")      
      s3key = environ.get("wasabi_accesskey")
      s3secret = environ.get("wasabi_secretkey")
      s3bucket = environ.get("wasabi_bucket")
      ip = event.get("http", {}).get("headers", {}).get("x-forwarded-for", "unknown")
      country = event.get("http", {}).get("headers", {}).get("cf-ipcountry", "unknown")
      useragent = event.get("http", {}).get("headers", {}).get("user-agent", "unknown")
      func_base = context.api_host + "/api/v1/web/" + context.namespace
      req_id = event.get("http", {}).get("headers", {}).get("x-request-id", "unknown")
      req_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]

      s3 = boto3.client('s3',
            endpoint_url = 'https://s3.us-west-1.wasabisys.com',
            aws_access_key_id = s3key,
            aws_secret_access_key = s3secret
      )

      #generate 5 character shortcode - only letters, numbers, dashes
      shortcode = ""
      count = 0
      while shortcode == "" and count <= 100:  # loop but include a circuit breaker just in case
            char_set = string.ascii_letters + string.digits + '-'
            shortcode = ''.join(random.sample(char_set, 5))
            
            try:
                  obj = s3.get_object(Bucket = s3bucket, Key = shortcode)
                  print(f"{shortcode} already exists, trying another one")
                  shortcode = ''
            except botocore.exceptions.ClientError as e:                  
                  if e.response['Error']['Code'] == 'NoSuchKey':
                        break  # shortcode wasn't found and is therefore unique. Continue
                  else:
                        shortcode = ''
                        body = "Error: " + str(e)
                        break
            except Exception as e:
                  shortcode = ''
                  body = "Error: " + str(e)
                  break
            
            count += 1

      shortenedurl = ""
      if urltoshorten != "" and shortcode != "":            
            data = {
                  "target": urltoshorten,
                  "shortcode": shortcode,
                  "ip": ip,
                  "country": country,
                  "useragent": useragent,
                  "requestid": req_id 
            }
            
            try:
                  s3.put_object(
                        Body = json.dumps(data),
                        Bucket = s3bucket,
                        Key = shortcode
                  )
                  shortenedurl = func_base + "/app/r" + "?c=" + shortcode  
            except Exception as e:
                  print(e)
                  body = "Error: " + str(e)
           

      if xtraparam == "echo":
            body = (f"urltoshorten: {urltoshorten} <br>shortenedurl: {shortenedurl} <br><br>" +
                  f"IP: {ip} <br>" +
                  f"Country: {country}<br>" +
                  f"UA: {useragent}<br>" +
                  f"Request ID: {req_id}<br>" +
                  f"Function base URL: {func_base}<br>" +
                  f"Time (UTC): {req_time}")
      elif shortenedurl != "":
            body = shortenedurl

      return {
            "headers": {"Content-Type": "text/html"},
            "statusCode": 200,
            "body": body
      }

if __name__ == '__main__':
      print(main({}, {}))
