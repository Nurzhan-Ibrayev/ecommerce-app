# Prerequisites
Before you begin, ensure that you have the following software installed on your machine:

Python 3.7 or higher: The backend of the application is built using Flask.
MongoDB: The NoSQL database for storing user and product data. You can install it locally or use a cloud service like MongoDB Atlas.
pip: Python package manager to install required libraries.

## Project Structure
Ensure your project folder is structured as follows:
```
ecommerce-app/
│
├── app.py                   
├── requirements.txt         
├── templates/              
│   ├── base.html
│   ├── index.html
│   └── register.html
│   └── login.html
│   └── cart.html
│   └── purchase_history.html
├── static/                  
│   ├── css/style.css
└── README.md 
```
## Installation Steps

### Clone the Repository
```bash
git clone git@github.com:Nurzhan-Ibrayev/ecommerce-app.git
```

### Create a Virtual Environment
```bash
python -m venv venv
# For Windows
venv\Scripts\activate
# For macOS/Linux
source venv/bin/activate

```

### Create a Virtual Environment
```bash
pip install -r requirements.txt
```

### Update Configuration
```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")  # Replace with your connection string
db = client['your_database_name']      
```

## Running the Application
```bash
python app.py
```
By default, Flask applications run on http://127.0.0.1:5000/. You can open this URL in your web browser to access the application.