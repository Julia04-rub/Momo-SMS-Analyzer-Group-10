# Momo-SMS-Analyzer-Group-10
# REST API 

## Project Overview

This project implements a REST API for MoMo SMS transactions with:

- Flask API for managing transactions
- XML Parser to process raw SMS data
- DSA Comparison between Linear Search and Dictionary Lookup
- Basic Authentication is the initial security mechanism

# Members

-Angel Bwiza

-Carla Lisa Batoni

-Julia Rubibi

# Repository Structure

Momo-SMS-Analyzer-Group-10/

│── api/               # Flask API (server.py)

│── parser             # XML Parser (parse_xml.py)

│── dsa/               # DSA comparison (compare_search.py)

│── docs/              # Documentation (api_docs.md)

│── screenshots/       # Test case screenshots

│── README.md          # Setup instructions 

## Setup Instructions

1. Clone Repository

git clone https://github.com/Julia04-rub/Momo-SMS-Analyzer-Group-10.git

cd Momo-SMS-Analyzer-Group-10/momo-api-project

2. Create Virtual Environment (recommended)

python3 -m venv venv

source venv/bin/activate   # Linux/Mac

venv\Scripts\activate      # Windows

3. Install Dependencies

pip install -r requirements.txt

4. Run API Server

cd api

python3 server.py


API will run on: http://127.0.0.1:5000


## Authentication

The API uses Basic Authentication:

Username: admin

Password: password

Include credentials in request headers:

Authorization: Basic <base64(username:password)>

## API Endpoints

- Method	Endpoint	Description
- GET	/transactions	Retrieve all transactions
- GET	/transactions/{id}	Retrieve transaction by ID
- POST	/transactions	Create a new transaction
- PUT	/transactions/{id}	Update transaction
- DELETE	/transactions/{id}	Delete transaction

## DSA Comparison

Two methods implemented to search transactions by ID:

Linear Search → O(n)

Dictionary Lookup → O(1)

Benchmark (20 transactions, 100 searches):

Linear Search → 0.000150s

Dictionary Lookup → 0.000015s

 Dictionary Lookup is ~10x faster.
 
 ## Screenshots

Screenshots of test cases are available in the /screenshots folder

API running (server_running.png)

Postman GET /transactions (get_transactions.png)

Postman POST /transactions (post_transaction.png)

DELETE /transactions/{id} (delete_transaction.png)

DSA results (dsa_results.png)

XML parsing results (xml_parsing.png)

## Report

The detailed PDF report includes:

Introduction to API Security

Documentation of Endpoints

Results of DSA Comparison

Reflection on Basic Auth Limitations

 Documentation link :



# Links

Scrum board link: https://github.com/users/Julia04-rub/projects/3/views/1

architecture diagram link: https://drive.google.com/file/d/1lO-DnmZt-O2SLdT-un0lPG8p7l9vdKNP/view?usp=sharing

GitHub repository link:https://github.com/Julia04-rub/Momo-SMS-Analyzer-Group-10                                                                                              
