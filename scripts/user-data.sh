#!/bin/bash
exec > /var/log/user-data.log 2>&1

echo "Starting Production Setup..."

# 1. Install Dependencies
dnf update -y
dnf install -y python3-pip git unzip

# 2. Install AWS CLI
if ! command -v aws &> /dev/null
then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    ./aws/install
fi

# 3. Create App Directory
mkdir -p /home/ec2-user/app
cd /home/ec2-user/app

# 4. Download Code (Deep Sync)
echo "Syncing code from S3..."
aws s3 sync s3://virtual-roast-source-apne1/ritual-roast-app/flask/ . --region ap-northeast-1

# 5. Install Requirements
pip3 install -r requirements.txt

# 6. Set Environment Variables
export AWS_DEFAULT_REGION=ap-northeast-1
export DB_SECRET_NAME="/virtualroast/db/admin"
export DB_HOST="virtual-roast-db.cbwuoswwgek3.ap-northeast-1.rds.amazonaws.com"

# 7. Start the App
echo "Starting Flask..."
nohup python3 ritual-roast.py > /var/log/flask-app.log 2>&1 &

echo "Setup Completed Successfully!"