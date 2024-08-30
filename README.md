

## Directory Structure
```bash
.
├── app
│   ├── __init__.py
│   └── main.py
├── manifests
│   └── deployment-aikc.yaml
│   └── ingress-aikc.yaml
│   └── namespace-aikc.yaml
│   └── sa-aikc.yaml
│   └── service-aikc.yaml
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

&nbsp;

## Dockerfile
```bash
FROM python:3.11-slim

ENV LC_ALL=C.UTF-8
ENV TZ=Asia/Seoul

## If you want to use static AWS Credentias fill below out but no recommend for security
#ENV AWS_ACCESS_KEY_ID=your-access-key-id
#ENV AWS_SECRET_ACCESS_KEY=your-secret-access-key
#ENV AWS_DEFAULT_REGION=your-region

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN apt-get update && apt-get install -y procps net-tools curl unzip
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

COPY ./app /app

EXPOSE 8000

CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8000", "--mode", "API"]
```

&nbsp;

## References
### AWS API
https://docs.aws.amazon.com/IAM/latest/APIReference/API_User.html
https://docs.aws.amazon.com/IAM/latest/APIReference/API_GetUser.html
https://docs.aws.amazon.com/IAM/latest/APIReference/API_AccessKey.html
https://docs.aws.amazon.com/IAM/latest/APIReference/API_AccessKeyLastUsed.html
https://docs.aws.amazon.com/IAM/latest/APIReference/API_AccessKeyMetadata.html
https://docs.aws.amazon.com/IAM/latest/APIReference/API_GetMFADevice.html

&nbsp;

### Python FastAPI
https://fastapi.tiangolo.com/tutorial/bigger-applications

https://fastapi.tiangolo.com/tutorial/middleware

&nbsp;

### Python Boto3
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sts.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sts/client/get_caller_identity.html#get-caller-identity
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam/client/list_account_aliases.html#list-account-aliases
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/boto3.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html

&nbsp;

### Python argparse
https://docs.python.org/3/library/argparse.html
