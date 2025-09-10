# Backend README

## Predictive Vehicle Maintenance Backend

This is a Flask backend for predictive vehicle maintenance. It exposes REST API endpoints for receiving vehicle data, running inference, and serving results to the frontend.

### Requirements

- Python 3.8+
- pip

### Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the backend server:
   ```
   python backend-python/main.py
   ```

3. The API will be available at `http://localhost:5000`.

### Main Endpoints

- `POST /home/post-data`  
  Receives vehicle and accident data, runs inference, and returns results.

- `GET /dashboard`  
  Returns the latest inference results (if implemented).

### Project Structure

```
backend-python/
  main.py
  app/
    routes.py
  models/
    inference.py
    artifacts/
  requirements.txt
```

### Notes

- Make sure the `models/artifacts` directory exists and contains the required model files.
- CORS is enabled for frontend-backend communication.
- Update `artifacts_dir` path in `routes.py` if your structure changes.

---

# Frontend README

## Predictive Vehicle Maintenance Frontend

This is a React app for interacting with the predictive vehicle maintenance backend. Users can input vehicle and accident data, view predictions, and see dashboard analytics.

### Requirements

- Node.js 16+
- npm

### Setup

1. Install dependencies:
   ```
   npm install
   ```

2. Start the development server:
   ```
   npm start
   ```

3. The app will be available at [http://localhost:3000](http://localhost:3000).

### Features

- Form for entering vehicle and accident details.
- Sends data to backend and displays prediction results.
- Dashboard view for analytics and recommendations.

### Project Structure

```
frontend-dashboard/
  src/
    App.js
    Home.js
    Dashboard.js
    ...
  public/
    logos/
  package.json
```

### Notes

- Ensure the backend is running at `http://localhost:5000` for API requests.
- Update API URLs in the frontend if your backend address changes.
- See [Create React App documentation](https://facebook.github.io/create-react-app/docs/getting-started) for more details.
