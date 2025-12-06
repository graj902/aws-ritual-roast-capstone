# ☕ Ritual Roast - Enterprise 3-Tier Web Architecture on AWS

**A highly available, fault-tolerant, and secure recipe submission platform deployed on AWS.**

## 📖 Project Overview
This project implements a classic **3-Tier Architecture** (Web, App, Data) using AWS Cloud services. It is designed to handle variable traffic loads, self-heal during component failures, and secure sensitive data using industry-standard encryption and network isolation.

**Live Demo:** [https://www.rajdevops.click](https://www.rajdevops.click)

---

## 🏗️ High-Level Design (HLD)
The architecture follows the **AWS Well-Architected Framework**, utilizing a Multi-AZ strategy for disaster recovery.

### **Architecture Flow:**
1.  **Users** access the application via a Custom Domain (\`rajdevops.click\`) resolved by **Route 53**.
2.  Traffic is routed to **Amazon CloudFront** (CDN) for caching and SSL termination (HTTPS).
3.  CloudFront forwards dynamic requests to an **Application Load Balancer (ALB)** in the Public Subnet.
4.  The ALB distributes traffic to **EC2 Instances** hosted in **Private Subnets** across two Availability Zones (\`ap-northeast-1a\`, \`ap-northeast-1c\`).
5.  The application logic (Flask) connects to an **Amazon RDS (MySQL)** database, which runs in a **Multi-AZ** configuration for high availability.
6.  **Secrets Manager** rotates and supplies database credentials securely at runtime.

---

## 🔧 Low-Level Design (LLD) & Configuration

### **1. Network Layer (VPC)**
* **Region:** \`ap-northeast-1\` (Tokyo)
* **CIDR:** \`10.16.0.0/16\`
* **Subnets:** 6 Total (2 Public, 2 Private App, 2 Private Data).
* **Gateways:**
    * **Internet Gateway:** For ALB and NAT Gateway traffic.
    * **NAT Gateway:** Allows Private Subnet instances to download updates/code without exposing them to inbound internet traffic.

### **2. Compute Layer (EC2 & Auto Scaling)**
* **OS:** Amazon Linux 2023
* **Instance Type:** \`t3.medium\` (Optimized for boot performance)
* **Auto Scaling Group:**
    * **Min:** 2 | **Max:** 4
    * **Scaling Policy:** Target Tracking.
    * **Health Checks:** ELB Health Check enabled (replaces failed app instances automatically).

### **3. Security & Identity**
* **IAM Roles:** EC2 instances use an Instance Profile with least-privilege access to S3 (Code Artifacts) and Secrets Manager.
* **Security Groups (Chained):**
    * \`ALB-SG\`: Allows HTTPS (443) from Anywhere (\`0.0.0.0/0\`).
    * \`App-SG\`: Allows Port 5000 **ONLY** from \`ALB-SG\`.
    * \`DB-SG\`: Allows Port 3306 **ONLY** from \`App-SG\`.

### **4. Storage & Database**
* **S3:** Stores versioned application artifacts in \`virtual-roast-source-apne1\`.
* **RDS:** MySQL 8.0 Multi-AZ deployment.
* **Secrets Manager:** Stores DB credentials (\`/virtualroast/db/admin\`); Automatic rotation enabled.

---

## 🛠️ Deployment Steps

### **Prerequisites**
* AWS Account with Admin Access
* Registered Domain Name (Route 53)
* SSL Certificate in \`us-east-1\` (ACM)

### **Step 1: Network Setup**
Provision VPC, Subnets, and Route Tables. Ensure Private Subnets route \`0.0.0.0/0\` to the NAT Gateway.

### **Step 2: Database & Security**
Deploy RDS in Multi-AZ. Store credentials in Secrets Manager. Create Security Groups with chained references.

### **Step 3: Application Launch**
Create a Launch Template with the User Data script (found in \`scripts/user-data.sh\`) to bootstrap the application.

### **Step 4: Global Delivery**
Deploy CloudFront distribution pointing to the ALB. Create Route 53 Alias records for the custom domain.

---

## 🧪 Troubleshooting Scenarios Encountered
During deployment, several critical issues were diagnosed and resolved:

1.  **503 Service Unavailable:** Caused by the ALB Default Action being set to "Fixed Response" instead of "Forward". Resolved by updating the Listener Rule.
2.  **Instance Connection Refused:** Caused by the Private Subnet missing a route to the NAT Gateway, preventing \`pip install\` from running. Resolved by fixing the Route Table association.
3.  **Application Crash (Error 110):** The EC2 instance could not connect to RDS. Diagnosed as a missing Security Group rule allowing egress traffic on Port 3306.

---

## 🏆 Acknowledgements
This project is based on the "AWS Cloud Architect" curriculum by **Rajesh Daswani** (IaaS Academy).