To download materials from CU LMS (Central University Learning Management System), follow these instructions.

## Prerequisites
Ensure Python 3 and pip are installed on your system.

## Step 1: Install Dependencies
Run this command in your terminal to install required Python packages:
```
pip install -r requirements.txt
```
## Step 2: Set Up Authentication
- Open the CU LMS website in your browser and log in to your account.
- Copy your browser's cookies (use Developer Tools > Application > Cookies).
- Paste the cookies into the `headers.json` file

## Step 3: Run the Script
Execute the download script with:
```
python3 run.py
```