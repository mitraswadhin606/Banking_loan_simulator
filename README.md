# Banking Loan Risk Assessment

A Flask web application for submitting loan applications, reviewing risk factors, and manually approving or rejecting applications.

## Features

- Login for banking staff
- Loan application form
- Automatic risk assessment based on applicant information
- Application list and application details
- Manual approval or rejection workflow
- Dashboard statistics and recent applications
- Responsive CSS interface

## Requirements

- Python 3.10 or newer
- Flask
- pytest for running tests

## Setup

Create and activate the virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the application

```powershell
python app.py
```

Open http://127.0.0.1:5000 in a browser.

## Demo login

- Username: `admin`
- Password: `admin123`

A second demo account is available:

- Username: `manager`
- Password: `manager123`

## Application workflow

1. Log in.
2. Open **New Application**.
3. Enter the applicant and loan details.
4. Submit the application.
5. Open **Applications** to view the submitted record.
6. Open the application ID to review the details.
7. Select **Approve application** or **Reject application**.

New applications start with the status **In Review**. Their final status is set manually by the reviewer.

## Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Project structure

```text
app.py                  Flask routes and risk assessment logic
requirements.txt        Python dependencies
static/css/style.css    Application styles
static/js/app.js        Frontend JavaScript
templates/              Jinja HTML templates
tests/test_risk.py      Risk assessment tests
```
