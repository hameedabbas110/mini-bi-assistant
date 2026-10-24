# Mini AI Business Intelligence Assistant

A web application that answers natural-language questions about sales data using a Flask API and SQLite database.

## Features

- Calculate total revenue and transaction count.
- Find the product with the highest revenue.
- Show monthly revenue trends.
- Find the region with the highest revenue.
- Compare revenue between two months.
- Display answers with supporting data.
- Handle empty and unsupported questions.

## Technology Stack

- Frontend: React and Vite
- Backend: Python and Flask
- Database: SQLite
- Data processing: Pandas
- Testing: Pytest

## Architecture

1. Sales data is loaded from a CSV file into an SQLite database.
2. The React frontend sends questions to the Flask backend.
3. The backend identifies supported question types.
4. SQL queries calculate the results.
5. The API returns structured answers and supporting figures.
6. The frontend displays the results.

## Setup Instructions

### 1. Activate the Python environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Start the backend

From the project root:

```powershell
python backend/app.py
```

### 3. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually http://localhost:5173/.

### 4. Run automated tests

From the project root:

```powershell
python -m pytest -v
```

## Data Quality

The initial database load reported 49 valid transactions and 2 excluded invalid or duplicate rows.

## AI Integration

The current question interpretation uses predefined rules. The assignment requires an AI or LLM-assisted interpretation mechanism; this should be implemented and documented before final submission if it has not already been added.

## Known Limitations

- Only supported question types are answered.
- Results depend on the supplied sales dataset.
- The application is a demonstration, not a production deployment.

## Testing

Nine automated tests have passed in the current development environment.

## Future Improvements

- Add an AI-assisted question interpreter.
- Add charts and more analytics.
- Improve input validation and error handling.
- Expand automated test coverage.

## AI Development Report

Create `AI_DEVELOPMENT_REPORT.md` documenting the AI tools actually used, development assistance, problems encountered, debugging steps, and future improvements.
