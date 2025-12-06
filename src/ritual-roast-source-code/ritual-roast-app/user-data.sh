#!/bin/bash
exec > /var/log/user-data.log 2>&1

# 1. Update and Install Dependencies
echo "Starting Installation..."
dnf update -y
dnf install -y python3-pip git unzip

# 2. Install AWS CLI (Standard Method for AL2023)
if ! command -v aws &> /dev/null
then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    ./aws/install
fi

# 3. Create App Directory
mkdir -p /home/ec2-user/app
cd /home/ec2-user/app

# 4. Download Code (Syncing the SPECIFIC 'flask' subfolder directly)
# This puts 'ritual-roast.py' directly inside /home/ec2-user/app/
echo "Syncing S3 Bucket..."
aws s3 sync s3://virtual-roast-source-apne1/ritual-roast-app/flask/ . --region ap-northeast-1

# 5. Verify and Install Python Requirements
ls -la /home/ec2-user/app/
pip3 install -r requirements.txt

# 6. Set Environment Variables (Crucial for Secrets Manager & DB)
export AWS_DEFAULT_REGION=ap-northeast-1
export DB_SECRET_NAME="/virtualroast/db/admin"
export DB_HOST="virtual-roast-db.cbwuoswwgek3.ap-northeast-1.rds.amazonaws.com"

# 7. Start the Application
echo "Starting Flask..."
nohup python3 ritual-roast.py > /var/log/flask-app.log 2>&1 &

echo "Setup Completed Successfully!"