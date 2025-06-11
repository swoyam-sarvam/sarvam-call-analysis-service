# CSV Analyzer

A Streamlit application for analyzing CSV files with authentication.

## Setup

1. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with the following content:
```
USERNAME=your_username
PASSWORD=your_password
```

## Running the Application

Run the application using:
```bash
streamlit run main.py
```

The application will start and open in your default web browser.

## Features

1. Secure authentication using environment variables
2. CSV file upload and analysis
3. Display of basic dataset information
4. Column-wise data type and null value analysis

## File Structure

- `main.py`: Main application entry point
- `auth.py`: Authentication module
- `home.py`: Home page with CSV upload functionality
- `.env`: Environment variables for authentication (create this file)
- `requirements.txt`: Python dependencies 