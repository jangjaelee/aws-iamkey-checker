# AWS IAM user's Access Key expired checker

This project provides a solution for monitoring the expiration status of AWS IAM users' Access Keys. It is designed to run as a containerized application on Kubernetes, supporting both API and CLI modes for flexible usage.

### Prerequisites
- **Python**: 3.11 or higher
- **Docker**: Required for building the container image
- **Kubernetes**: Required for deploying and running the application

&nbsp;

## Project Structure:
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
│   └── secret-aws-credentials.yaml
│   └── service-aikc.yaml
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

&nbsp;

## Dockerfile Overview
The Dockerfile is configured to create a lightweight container for the application. It installs necessary dependencies, including the AWS CLI, and sets up the environment for execution.
```bash
FROM python:3.11-slim

ENV LC_ALL=C.UTF-8
ENV TZ=Asia/Seoul

# If you want to use your environment for AWS Credentias, fill it out below.
# But It's very vulnerable to security.
# Recommend using IRSA on EKS or Kubernetes Secret object.
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

## Building the Docker Image
To build the Docker image, use the following command:
```bash
docker built -t app-aikc:latest .
```

&nbsp;

## Pushing the Docker Image to a Container Registry
Follow these steps to push your Docker image to a container registry:
```bash
docker login
docker tag app-aikc:latest cine0831/app-aikc:latest
docker push cine0831/app-aikc:latest
```

&nbsp;

## Kubernetes Setup for AWS Credentials
If you're not using IAM Roles for Service Accounts (IRSA) in EKS, you'll need to create a Kubernetes Secret to store your AWS credentials:
```bash
kubectl create secret generic secret-aws-credentials -n aikc \
  --from-literal=aws_access_key_id=<YOUR_AWS_ACCESS_KEY_ID> \
  --from-literal=aws_secret_access_key=<YOUR_AWS_SECRET_ACCESS_KEY>
```

&nbsp;

## API Usage
### Retrieve IAM Users with Expired Access Keys
To get a list of IAM users whose Access Keys have expired beyond a specified number of hours:
```bash
curl http://<IP>:<Port>/key-check?hours=<Parameter(int)>
```

Response Example:
```bash
[
  {
    "IAM User": "applicant",
    "Access Key ID": "asdfasdfasdf",
    "Access Key Creation Date": "2024-08-20 09:21:19+00:00",
    "Access Key Status": "Active",
    "Expired Hours": -761
  },
  {
    "IAM User": "applicant",
    "Access Key ID": "weasdfasdfasdf",
    "Access Key Creation Date": "2024-08-28 07:21:10+00:00",
    "Access Key Status": "Active",
    "Expired Hours": -951
  }
]
```

&nbsp;

### Retrieve AWS Account Information
- **Account Number and Alias:**
```bash
curl http://<IP>:<Port>/account/info
```
- **AWS Account Information Summary:**
```bash
curl http://<IP>:<Port>/account/summary
```

&nbsp;

### Retrieve IAM User Information
- **User Details:**
```bash
curl http://<IP>:<Port>/user/{username}
```
- **Access Key List for a User:**
```bash
curl http://<IP>:<Port>/user/{username}/access-keys
```

&nbsp;

## CLI Usage
To run the application in CLI mode and retrieve IAM users with expired Access Keys:
```bash
usage: main.py [-h] [-T TIME] [-H HOST] [-P PORT] [-M MODE] [-V]

AWS Access Key checker application with CLI parameters.

options:
  -h, --help            show this help message and exit
  -T TIME, --time TIME  Expiration time, default: 2160 hours
  -H HOST, --host HOST  Listen address, default: 127.0.0.1
  -P PORT, --port PORT  Port number, default: 8000
  -M MODE, --mode MODE  CLI or API mode
  -V, --version         show program's version number and exit
```

```bash
python main.py --mode CLI --time <N_hours>
```

Usage Example with Kubernetes:
```bash
kubectl exec -it app-aikc-66644cd6d8-vvkpj -n aikc -- python main.py --mode CLI --time 1000
```

&nbsp;

## References
#### AWS API
https://docs.aws.amazon.com/IAM/latest/APIReference/API_User.html
https://docs.aws.amazon.com/IAM/latest/APIReference/API_GetUser.html
https://docs.aws.amazon.com/IAM/latest/APIReference/API_ListUsers.html
https://docs.aws.amazon.com/IAM/latest/APIReference/API_AccessKey.html
https://docs.aws.amazon.com/IAM/latest/APIReference/API_AccessKeyLastUsed.html
https://docs.aws.amazon.com/IAM/latest/APIReference/API_AccessKeyMetadata.html
https://docs.aws.amazon.com/IAM/latest/APIReference/API_GetMFADevice.html

&nbsp;

#### Python FastAPI
https://fastapi.tiangolo.com/tutorial/bigger-applications<br>
https://fastapi.tiangolo.com/tutorial/middleware

&nbsp;

#### Python Boto3
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sts.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sts/client/get_caller_identity.html#get-caller-identity<br>
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/iam/client/list_account_aliases.html#list-account-aliases<br>
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/boto3.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html
https://github.com/boto/botocore/blob/develop/botocore/exceptions.py

&nbsp;

#### Python Library and ASGI
https://docs.python.org/3/library/argparse.html
https://asgi.readthedocs.io/en/latest/introduction.html#how-does-asgi-work
