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
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError
from typing import Union
from fastapi import FastAPI, HTTPException
from datetime import datetime, timezone, timedelta


# FastAPI 시작
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
    try:
        res = iam_client.get_account_summary()
        return res

    except NoCredentialsError:
        raise HTTPException(status_code=403, detail="No valid AWS credentials were found.")
    except PartialCredentialsError:
        raise HTTPException(status_code=403, detail="Incomplete AWS credentials configuration.")
    except ClientError as e:
        # Handle any specific client errors
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            raise HTTPException(status_code=403, detail="Access denied to get caller identity.")
        else:
            raise HTTPException(status_code=500, detail=f"An AWS client error occurred: {e}")
    except Exception as e:
        # General exception handling
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
        

def get_account_info():
    try:
        # AWS Account ID 가져오기
        sts_response = sts_client.get_caller_identity()
        account_id = sts_response['Account']

        # AWS Account Alias 가져오기
        alias_response = iam_client.list_account_aliases()
        account_alias = alias_response['AccountAliases']

        # Account ID and Alias 출력
        #print(f"AWS Account ID: {account_id}")
        #if aliases:
        #    print(f"AWS Account Alias: {aliases[0]}")
        #else:
        #    print("No account alias found.")
        res = { 
            "AWS Account ID": account_id,
            "AWS Account Alias": account_alias[0]
        }
        return res

    except NoCredentialsError:
        raise HTTPException(status_code=403, detail="No valid AWS credentials were found.")
    except PartialCredentialsError:
        raise HTTPException(status_code=403, detail="Incomplete AWS credentials configuration.")
    except ClientError as e:
        # Handle any specific client errors
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            raise HTTPException(status_code=403, detail="Access denied to get caller identity.")
        else:
            raise HTTPException(status_code=500, detail=f"An AWS client error occurred: {e}")
    except Exception as e:
        # General exception handling
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


def expired_access_key_check(hours: int, mode: str="API"):
    try:
        # N 시간
        N_hour = hours

        # 현재시간 가져오기
        current_time = datetime.now(timezone.utc)

        # 모든 AWS IAM users 목록 가져오기
        users = iam_client.list_users()

        # empty list 변수 선언
        result = []

        for user in users['Users']:
            username = user['UserName']

            # IAM user의 Access Keys 목록 자겨오기
            access_keys = iam_client.list_access_keys(UserName=username)

            # AccessKeyMetada로부터 Access Key 생성 날짜 가져오기
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

                # Access Key가 생성된지 N시간이 지난경우 IAM user의 Access Key 세부 정보와 지난 시간 출력
                if past_hours <= 0:
                    user_info = {
                        "IAM User": username,
                        "Access Key ID": key['AccessKeyId'],
                        "Access Key Creation Date": creation_date,
                        "Access Key Status": key['Status'],
                        "Expired Hours": past_hours
                    }
                    result.append(user_info)

        # 결과는 json 혀식으로 변환
        res = json.dumps(result, indent=4)

        # CLI mode로 동작시 JSON 형식으로 출력
        if mode == 'CLI':
            # 결과값 null 인지 확인
            if not result:
                print("No expired access keys found")
            else:
                print(res)
        else:
            if not result:
                raise HTTPException(status_code=404, detail="No expired access keys found")
            return result
        
    except NoCredentialsError:
        raise HTTPException(status_code=403, detail="No valid AWS credentials were found.")
    except PartialCredentialsError:
        raise HTTPException(status_code=403, detail="Incomplete AWS credentials configuration.")
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            raise HTTPException(status_code=403, detail="Access denied to get caller identity.")
        else:
            raise HTTPException(status_code=500, detail=f"An AWS client error occurred: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    

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
    account_summary = get_account_summary()
  
    return account_summary
    

@app.get("/account/info")
async def account_info():
    """
    Get information an AWS Account Information
    """    
    account_info = get_account_info()
  
    return account_info


@app.get("/key-check")
async def get_expired_access_key_check(hours: int):
    """
    To check expired AWS Access Keys of IAM Users
    """
    keys = expired_access_key_check(hours)
  
    #if not keys:
    #    raise HTTPException(status_code=404, detail="No expired access keys found")
  
    return keys


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
    List access keys for an IAM user
    """
    try:
        res = iam_client.list_access_keys(UserName=username)
        return res['AccessKeyMetadata']
    except ClientError as e:
        raise HTTPException(status_code=404, detail=f"Cannot list access keys for {username}. {e.response['Error']['Message']}")


@app.get("/health",  summary="Health Check", response_description="Return HTTP Status Code 200 (OK)", status_code=200)
async def health():
    """
    Perform a Health Check
    """    
    return {"Status": "healthy"}


def parsing_argument():
    parser = argparse.ArgumentParser(description="AWS Access Key checker application with CLI parameters.")
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

