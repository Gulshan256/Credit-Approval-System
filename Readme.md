
# Credit Approval System

This project is a credit approval system built using Django 4+ with Django Rest Framework. It allows for the management of customers, loans, and the processing of loan applications.

## Features

- Register new customers with an approved credit limit based on salary.
- Check loan eligibility based on credit score.
- Process new loans based on eligibility criteria.
- View loan details for a specific loan ID or all loans associated with a customer ID.

## Setup and Installation

### Requirements

- Python 3.x
- Django 4+
- Django Rest Framework
- PostgreSQL

### Installation

1. Clone the repository: https://github.com/Gulshan256/Credit-Approval-System.git

```
git clone https://github.com/Gulshan256/Credit-Approval-System.git
cd Credit-Approval-System
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Set up PostgreSQL database and configure database settings in `settings.py`.

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
       }
   }
   ```

   and uncomment the following lines:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql_psycopg2',
           'NAME': '(databse name)',
           'USER': 'postgres',
           'PASSWORD': 'postgres',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

4. Apply migrations:

```
python manage.py migrate
```

5. Data Import
   Before starting the development server, run the following script to import data from Excle(xlsx) files:
  
   ```bash
   python import_data.py

   ```

6.  Database Sequence Reset Note: This step is required only if you are using PostgreSQL as the database. If you are using SQLite, skip this step.

  To ensure proper auto-incrementing sequence, set the next value of the sequence:
  
   ```bash
   python manage.py dbshell
   ```
   ```bash
   SELECT setval('customer_customer_id_seq', (SELECT MAX(customer_id) FROM customer) + 1);
   SELECT setval('loan_id_seq', (SELECT MAX(id) FROM loan) + 1); 

7. Run the development server:

```
python manage.py runserver
```

## Usage

1. Use the provided API endpoints to register customers, check loan eligibility, process new loans, and view loan details.
2. Access the endpoints through an API client such as Postman or through the command line using tools like curl.
3. Refer to the API documentation or view the code to understand the request and response formats for each endpoint.

## API Endpoints

- `/register`: Add a new customer with an approved credit limit.
- `/check-eligibility`: Check loan eligibility based on credit score.
- `/create-loan`: Process a new loan based on eligibility.
- `/view-loan/<loan_id>`: View loan details by loan ID.
- `/view-loans/<customer_id>`: View all current loan details by customer ID.


