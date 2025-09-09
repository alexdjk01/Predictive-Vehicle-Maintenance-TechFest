# Predictive Vehicle Maintenance Backend

This project is a backend service for the Predictive Vehicle Maintenance application. It is built using Flask and is designed to receive data from a React frontend application.

## Project Structure

```
backend-python
├── app
│   ├── __init__.py
│   ├── routes.py
│   └── utils.py
├── main.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd backend-python
   ```

2. **Create a virtual environment** (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required packages**:
   ```
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```
   python main.py
   ```

The application will start on `http://127.0.0.1:5000` by default.

## API Endpoints

- **POST /home/post-data**: Receives vehicle data from the frontend, processes it, and returns a response.

## Usage

Send a POST request to `/home/post-data` with the following JSON structure:

```json
{
  "brand": "BMW",
  "year": 2000,
  "odometer": 150000,
  "accidentzone": "none",
  "rust": 2,
  "severity": 3,
  "flooded": false,
  "timebudget": 30
}
```

The backend will process the data and respond with the appropriate information.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.