# Phone Spam Detection API

Built using FastAPI to detect and report spam phone numbers. FastAPI was considered over Django since the main motive of this project is API development, where FastAPI is API centric while Django is for full fledged applications (that might introduce garbage dependencies)

## Description

The Phone Spam Detection API provides the following functionalities:

- Register and authenticate users (/register/, /login/)
- Report spam phone numbers (/report/)
- Search for users by phone number or name (/search/phone/, /search/name/)

## Usage

Navigate to the project directory:

```bash
cd phone_spam
```

## Requirements

To run this application, install the requirements first using:

```bash
pip install -r requirements.txt
```

Python 3.10.14 (used in project)

## Prerequisites

The database URI is already configured.

Just create a mysql database (the project uses MariaDB since its primarily supported on Arch Linux) with the following details:

```bash
username: sid
password: sample123
```

After this user is created, please login and paste in the following code:

```sql
CREATE DATABASE spamCheck;
USE spamCheck;
```

We're creating two tables:

```sql
CREATE TABLE contacts (
    uuid CHAR(36) NOT NULL,
    name VARCHAR(50) NOT NULL,
    email VARCHAR(50),
    phone VARCHAR(20) NOT NULL,
    password VARCHAR(100) NOT NULL,
    contacts_list JSON,
    reports_list JSON,
    PRIMARY KEY (uuid)
);

CREATE TABLE globalBlackList (
    phone VARCHAR(20) NOT NULL,
    name VARCHAR(50),
    spam BOOLEAN DEFAULT FALSE,
    spam_reports INT DEFAULT 0,
    PRIMARY KEY (phone)
);
```

(contacts_list left untouched in project since explicitly mentioned in the task document)

## Populating the Database

To populate the database with sample data, run the populate.py script:

```bash
python populate.py
```

This will populate the database with some initial data for testing and development purposes.

## Running the Application

Run the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```

The application will start running at <b>http://localhost:8000</b>.

## Running Tests

To run the test suite, use the following command:
(Explicitly call python to add in the current directory path so that path errors do not occur)

```bash
python -m pytest test.py
```

## API Documentation

After running the application, you can access the Swagger UI documentation at http://localhost:8000/docs or the ReDoc documentation at http://localhost:8000/redoc.

## `.env` contents

```
DB_USERNAME='sid'
DB_PASSWORD='sample123'
DB_HOST='localhost'
DB_PORT='3306'
DB_NAME='spamCheck'
```
