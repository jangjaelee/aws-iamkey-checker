FROM python:3.11-slim

ENV LC_ALL=C.UTF-8
ENV TZ=Asia/Seoul

# If you want to use your environment for AWS Credentias, fill it out below.
# But It's very vulnerable to security.
# Recommend using IRSA on EKS or Kubernetes Secret object.
#ENV AWS_ACCESS_KEY_ID=your-access-key-id
#ENV AWS_SECRET_ACCESS_KEY=your-secret-access-key
#ENV AWS_DEFAULT_REGION=ap-northeast-2


WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN apt-get update && apt-get install -y procps net-tools curl unzip
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

COPY ./app /app

EXPOSE 8000

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8000", "--mode", "API"]
