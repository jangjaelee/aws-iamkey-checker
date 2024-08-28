#!/usr/bin/python3
# -*-Python-script-*-
#
#/**
# * Title    : AWS Access Key expired checker of IAM Users
# * Auther   : by Jangjae, Lee
# * Created  : 08-28-2024
# * Modified : 08-29-2024
# * E-mail   : cine0831@gmail.com
#**/

import boto3
import json
import uvicorn
import argparse
from botocore.exceptions import ClientError
from typing import Union
from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone, timedelta

# Starting FastAPI
app = FastAPI()

# 기본 프로바일을 사용하여 세션 생성
session = boto3.Session()
    
# AWS Security Token Service(STS)client 생성
sts_client = session.client('sts')

# AWS Identity and Access Management(IAM) client 생성
#iam_client = boto3.client('iam')
iam_client = session.client('iam')


N = int(0)

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



def expired_access_key_check(hours: int, mode: str="API"):
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

    if mode == 'CLI':
        res = json.dumps(result, indent=4)
        #Print the result list as a JSON array
        print(res)
    else:
        return result


@app.get("/")
async def root():
    """
    This is main page
    """
    return {"AWS Access Key expirion checker for IAM User"}


@app.get("/account/summary")
async def account_summary():
    """
    Get information an AWS Account Summary
    """    
    try:
        account_summary = get_account_summary()
        return account_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/account/info")
async def account_info():
    """
    Get information an AWS Account Information
    """    
    try:
        account_info = get_account_info()
        return account_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/key-check")
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


@app.get("/user/{username}")
async def get_user_info(username: str):
    """
    Get information about an IAM user.
    """
    try:
        res = iam_client.get_user(UserName=username)
        return res['User']
    except ClientError as e:
        raise HTTPException(status_code=404, detail=f"User {username} not found. {e.response['Error']['Message']}")


@app.get("/user/{username}/access-keys")
async def list_access_keys(username: str):
    """
    List access keys for an IAM user.
    """
    try:
        res = iam_client.list_access_keys(UserName=username)
        return res['AccessKeyMetadata']
    except ClientError as e:
        raise HTTPException(status_code=404, detail=f"Cannot list access keys for {username}. {e.response['Error']['Message']}")


def parsing_argument():
    parser = argparse.ArgumentParser(description="FastAPI application with CLI parameters.")
    parser.add_argument("-T", "--time", type=int, default=2160, help="Expiration time" )
    parser.add_argument("-H", "--host", type=str, default="127.0.0.1", help="Listen address")
    parser.add_argument("-P", "--port", type=int, default=8000, help="Port number")
    parser.add_argument("-M", "--mode", type=str, default="API", help="CLI or API mode")
    #parser.add_argument("-V", "--version", typ'version', version='v0.1')
    return parser.parse_args()

def main():
    # by using argument on CLI
    args = parsing_argument()
    config = args

    #if mode CLI or API
    if config.mode == 'API':
        uvicorn.run("main:app", host=config.host, port=config.port)
    elif config.mode == 'CLI':
        expired_access_key_check(config.time, config.mode)
    else:
        exit

    
if __name__ == "__main__":
    main()

