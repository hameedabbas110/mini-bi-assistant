# AI Development Report

## 1. AI Tools Used
I used ChatGPT to understand the assignment, plan the application, get coding suggestions, and troubleshoot errors.

## 2. How AI Helped
AI assistance helped me understand the project structure, Flask API development, SQLite database queries, React frontend development, and automated testing. I reviewed and tested the application locally.

## 3. Problems Encountered
- Pip installation encountered a package hash mismatch.
- VS Code showed a Python environment or import warning.
- I needed to run the Flask backend and React frontend in separate terminals.
- I needed to configure automated tests.

## 4. How I Debugged the Problems
I examined terminal error messages, checked the active Python interpreter, tested API requests, verified the frontend in the browser, and ran pytest.

Nine automated tests passed in my development environment.

## 5. Current Implementation
The application uses Python, Flask, React, and SQLite. It supports:
- Total revenue
- Highest-revenue product
- Monthly revenue trend
- Highest-revenue region
- Comparison between two months

Question interpretation currently uses predefined rules. An LLM-based interpretation mechanism has not yet been verified as implemented.

## 6. Known Limitations
- Only supported question patterns are understood.
- Results depend on the supplied sales dataset.
- The application has not been deployed to production.
- AI integration still needs to be implemented and tested if not already added.

## 7. Improvements With One More Day
- Add an LLM-assisted question interpreter.
- Improve input validation and error handling.
- Add charts for monthly revenue.
- Expand tests for edge cases and invalid data.
- Improve deployment and setup documentation.
