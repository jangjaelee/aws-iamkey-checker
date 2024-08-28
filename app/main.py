#!/usr/bin/python3
# -*-Python-script-*-
#
#/**
# * Title    : AWS Access Key expired checker of IAM Users
# * Auther   : by Jangjae, Lee
# * Created  : 08-28-2024
# * Modified : 
# * E-mail   : cine0831@gmail.com
#**/

import boto3
import json
import uvicorn
from botocore.exceptions import ClientError
from typing import Union
from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone, timedelta

app = FastAPI()

# 기본 프로바일을 사용하여 세션 생성
session = boto3.Session()
    
# AWS Security Token Service(STS)client 생성
sts_client = session.client('sts')

# AWS Identity and Access Management(IAM) client 생성
#iam_client = boto3.client('iam')
iam_client = session.client('iam')


def get_account_summary():
    res = iam_client.get_account_summary()
    return res


def get_account_info():
    # AWS Account ID 획득
    sts_response = sts_client.get_caller_identity()
    account_id = sts_response['Account']

    # Get account aliases
    alias_response = iam_client.list_account_aliases()
    account_alias = alias_response['AccountAliases']

    # Account ID and Alias 출력
    #print(f"AWS Account ID: {account_id}")
    #if aliases:
    #    print(f"AWS Account Alias: {aliases[0]}")
    #else:
    #    print("No account alias found.")
    res = { "AWS Account ID": account_id, "AWS Account Alias": account_alias[0] }
    return res



def expired_access_key_check(hours: int):
    N_hour = hours

    # Get the current time
    current_time = datetime.now(timezone.utc)

    # Get the list of all IAM users
    users = iam_client.list_users()

    result = []

    # Iterate over each user
    for user in users['Users']:
        username = user['UserName']

        # List the access keys for the user
        access_keys = iam_client.list_access_keys(UserName=username)

        # Check each access key's creation date
        for key in access_keys['AccessKeyMetadata']:
            creation_date = str(key['CreateDate'])

            # 문자열을 datetime 객체로 변환
            start_time = datetime.fromisoformat(creation_date)

            # 경과 시간 계산
            elapsed_time = current_time - start_time
            #total_days = int(elapsed_time.days)
            total_hours = int(elapsed_time.total_seconds() / 3600)
            #print(total_hours)

            past_hours = total_hours - N_hour
            #print(past_hours)

            # If the key was created within the past N days, print the details
            if past_hours <= 0:
                user_info = {
                    "IAM User": username,
                    "Access Key ID": key['AccessKeyId'],
                    "Access Key Creation Date": creation_date,
                    "Access Key Status": key['Status'],
                    "Expiration Time": past_hours
                }
                result.append(user_info)

    #res = json.dumps(result, indent=4)
    # Print the result list as a JSON array
    #print(res)
    return result


@app.get("/")
async def root():
    """
    This is main page
    """
    return {"AWS Access Key expirion checker for IAM User"}


@app.get("/account_summary")
async def account_summary():
    """
    Get information an AWS Account Summary
    """    
    try:
        account_summary = get_account_summary()
        return account_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/account_info")
async def account_info():
    """
    Get information an AWS Account Information
    """    
    try:
        account_info = get_account_info()
        return account_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/key_check")
async def get_expired_access_key_check(hours: int):
    """
    To check expired AWS Access Keys of IAM Users
    """    
    try:
        keys = expired_access_key_check(hours)
        if not keys:
            raise HTTPException(status_code=404, detail="No expired access keys found")
        return keys
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    #opt = parsing(sys.argv[1:])
    #run(opt)

    N = int(20000) 

    uvicorn.run(app, host="0.0.0.0", port=8000)

    #get_account_info()
    # Call the function to list users with recent access keys
    #list_users_with_recent_access_keys(N)

if __name__ == "__main__":
    main()
