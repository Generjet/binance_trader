# [Flask Datta Able](https://app-generator.dev/product/datta-able/flask/)

Open-source **Flask** project crafted on top of **Datta Able Dashboard**, an open-source `Bootstrap` design.
The product is designed to deliver the best possible user experience with highly customizable feature-rich pages. 

- 👉 [Flask Datta Able](https://app-generator.dev/product/datta-able/flask/) - `Product Page`
- 👉 [Flask Datta Able](https://flask-datta-demo.onrender.com) - `LIVE Demo` 
- 👉 [Flask Datta Able Documentation](https://app-generator.dev/docs/products/flask/datta-able/index.html) - `Complete Information` and Support Links
  - [Getting Started with Flask](https://app-generator.dev/docs/technologies/flask/index.html) - a `comprehensive tutorial`
  - `Configuration`: Install Tailwind/Flowbite, Prepare Environment, Setting up the Database 
  - `Start with Docker`
  - `Manual Build`
  - `Start the project`
  - `Deploy on Render`

<br />

## Deploy LIVE

> One-click deploy (requires to have already an account).

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

<br />

## Features

- Simple, Easy-to-Extend Codebase
- Datta Able Design - Full Integration 
- Bootstrap 5 Styling 
- Session-based Authentication
- DB Persistence: SQLite (default), can be used with MySql, PgSql
- DB Tools: Flask-Migrate
- Flask-RestX API
- Async Tasks (Celery)
- Docker 
- CI/CD integration for Render 

![Flask Datta Able - Open-Source Flask Starter](https://user-images.githubusercontent.com/51070104/176118649-7233ffbc-6118-4f56-8cda-baa81d256877.png)

<br />

## [Datta Able PRO Version](https://app-generator.dev/product/datta-able-pro/flask/)

> The premium version provides more features, priority on support, and is more often updated - [Live Demo](https://flask-datta-pro.onrender.com/).

- **Simple, Easy-to-Extend** Codebase
- **Berry PRO** Design - Bootstrap 5 Design 
- **Extended User Profiles**
- [Charts](https://flask-datta-pro.onrender.com/charts/) 
- [DataTables](https://flask-datta-pro.onrender.com/tables): Server-side Pagination, Search, Filters, Export
- API
- **File Manager**
- **Celery** (async tasks)
- **Docker**
- **Deployment-Ready** for Render 

![Datta Able PRO - Full-Stack Flask Starter provided by App-Generator.](https://user-images.githubusercontent.com/51070104/170474361-a58da82b-fff9-4a59-81a8-7ab99f478f48.png)

<br />

---
[Flask Datta Able](https://app-generator.dev/product/datta-able/flask/) - Open-Source **Flask** Starter provided by [App Generator](https://app-generator.dev)

# data abble 
Manual Build
It’s best to use a Python Virtual Environment for installing the project dependencies. You can use the following code to create the virtual environment

virtualenv env
To activate the environment execute env\Scripts\activate.bat for Windows or source env/bin/activate on Linux-based operating systems.

Having the VENV active, we can proceed and install the project dependencies:

pip install -r requirements.txt
Environment
The starter loads the environment variables from .env file. Here are the critical ones:

DEBUG: set by default to False (development mode)

SECRET_KEY: a random value used by Django to secure sensitive information like passwords and cookie information

Database Credentials: DB_ENGINE, DB_USERNAME, DB_PASS, DB_HOST, DB_PORT, DB_NAME
if detected, the database is switched automatically from the default SQLite to the specified DBMS

Setting up the Database
By default, the application uses SQLite for persistence. In order to use MySql / PostgreSQL, you’ll need to install the Python driver(s):

pip install mysqlclient # for MySql
# OR
pip install psycopg2    # for PostgreSQL
To connect the application with the database, you’ll need to fill in the credentials int the .env file and run the migrations.

.env
DB_ENGINE=mysql
# OR
DB_ENGINE=postgresql

# DB credentials below
DB_HOST=localhost
DB_NAME=<DB_NAME_HERE>
DB_USERNAME=<DB_USER_HERE>
DB_PASS=<DB_PASS_HERE>
DB_PORT=3306
Set up the environment

export FLASK_APP=run.py
Use the following commands to set up the database:

# Init migration folder
flask db init # to be executed only once

flask db migrate # Generate migration SQL
flask db upgrade # Apply changes
Running the project
The following command starts the project using Flask development server:

flask run              # Starts on default PORT 5000
flask run --port 8999  # Starts on PORT 8999 (custom port)
By default Flask starts on port 5000 but this can be easily changed by adding the PORT number as argument. At this point, the app runs at http://127.0.0.1:5000/