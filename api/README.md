# Transportation Blockchain Dashboard

## Project Overview
This project is a blockchain-based system for logging and analyzing transportation delay data. It integrates a simple blockchain with machine learning models (trained in Jupyter Notebook) to predict delays. The Flask API allows you to add new delay records, retrieve blockchain data, make predictions, and visualize data via a front-end dashboard.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Virtual Environment (venv)
- Git

### Project Directory Structure

The project is organized as follows:

```
transport_blockchain_project/
├── data/                          # Contains the dataset (e.g., transportation_data.csv)
├── notebook/                      # Jupyter Notebook files used for training/testing the ML model
├── api/                          # Flask API code and front-end dashboard
│   ├── app.py                    # Main Flask application
│   ├── blockchain.py             # Blockchain logic
│   ├── templates/                # HTML templates for the dashboard
│   │   └── dashboard.html        # Dashboard page
│   ├── requirements.txt          # Python dependencies
│   └── (other model files, e.g., *.pkl, training_columns.json)
└── README.md                     # This documentation file
```

### Installation Steps

1. **Clone the Repository**:
```bash
git clone <your-repo-url>
cd transport_blockchain_project/api
```

2. **Create and Activate a Virtual Environment:**

*On Windows (PowerShell):*
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
```

*On Windows (CMD):*
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. **Install Dependencies:**
```bash
pip install -r api/requirements.txt
```

4. **Run the Flask API:**

*Navigate to the API folder:*
```bash
cd api
```

*Start the application:*
```bash
python app.py
```

The app will run at http://127.0.0.1:5000/.

## API Endpoints

### 1. Home
- URL: /
- Method: GET
- Description: Returns a simple greeting to confirm the API is running.
- Example Response: 
```bash
Hello, Blockchain!
```

### 2. Get Blockchain Ledger
- URL: /chain
- Method: GET
- Description: Returns the full blockchain (all delay records) as a JSON object.
- Example Response:
```json
{
    "length": 2,
    "chain": [
        {
            "index": 0,
            "timestamp": 1697040000.123,
            "delay_data": {"message": "Genesis Block - Start of Delay Tracking"},
            "previous_hash": "0",
            "hash": "abc123..."
        },
        {
            "index": 1,
            "timestamp": 1697043600.456,
            "delay_data": {
                "location": "Central Station",
                "route": "Bus-5A",
                "delay_minutes": 15
            },
            "previous_hash": "abc123...",
            "hash": "def456..."
        }
    ]
}
```

### 3. Add New Delay Record
- URL: /add_delay
- Method: POST
- Description: Adds a new delay record to the blockchain.
- Required JSON Payload:
```json
{
    "location": "Central Raipur Station",
    "route": "Bus-NH-53",
    "delay_minutes": 10
}
```
- Example Response:
```json
{
    "message": "New delay record added",
    "block": {
        "index": 1,
        "timestamp": 1697043600.456,
        "delay_data": {
            "location": "Central Station",
            "route": "Bus-5A",
            "delay_minutes": 15
        },
        "previous_hash": "abc123...",
        "hash": "def456..."
    }
}
```

### 4. Get Last Block
- URL: /last_block
- Method: GET
- Description: Returns the last block in the blockchain.

### 5. Validate Blockchain
- URL: /validate
- Method: GET
- Description: Validates the blockchain by checking the hashes of each block.
- Example Response:
```json
{
    "message": "Blockchain is valid"
}
```

### 6. Reset Blockchain
- URL: /reset
- Method: POST
- Description: Resets the blockchain to its initial state.

### 7. Predict Delay
- URL: /predict
- Method: POST
- Description: Accepts raw transportation data, processes it with one-hot encoding to match training data, runs predictions using multiple ML models, and returns both numeric predictions and human-readable labels.
- Required JSON Payload:
```json
{
    "Route": "Bus-5A",
    "Day": "Monday",
    "Incident": "General Delay",
    "Direction": "N"
}
```
- Example Response:
```json
{
    "logistic_regression_prediction": 1,
    "logistic_regression_label": "Delay Expected",
    "random_forest_prediction": 1,
    "random_forest_label": "Delay Expected",
    "xgboost_prediction": 1,
    "xgboost_label": "Delay Expected"
}
```

### 8. Get Delay Trends
- URL: /delay_trends
- Method: GET
- Description: Loads the static dataset (from the data folder), calculates the average delay for each day (using the "Day" and "Min Delay" columns), and returns day labels and average delays for chart visualization.
- Example Response:
```json
{
    "labels": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "averageDelays": [12.0, 15.0, 8.0, 20.0, 10.0, 7.0, 5.0]
}
```

### 9. Dashboard
- URL: /dashboard
- Method: GET
- Description: Renders the dashboard to visualize the blockchain ledger and provide a prediction form.

## ML Model and Blockchain Integration

### ML Model
The ML models were trained in Jupyter Notebook on historical transportation data. The models (Logistic Regression, Random Forest, XGBoost) are saved as .pkl files and loaded in the Flask API for predictions.

### Blockchain
New delay records and prediction results are logged on a blockchain to ensure data transparency and integrity. The blockchain is persisted in a JSON file (blockchain_data.json).

## Version Control and GitHub

### 1. Initialize a Git Repository:
```bash
git init
```

### 2. Add All Files:
```bash
git add .
```

### 3. Commit Changes:
```bash
git commit -m "Initial commit of Transportation Blockchain Dashboard project"
```

### 4. Push to GitHub:
- Create a repository on GitHub.
- Follow GitHub instructions to push your local repository to the remote repository.

**Ensure your repository includes:**
- app.py
- blockchain.py
- requirements.txt
- training_columns.json (if applicable)
- Saved ML model files (e.g., logistic_regression_model.pkl, etc.)
- README.md
- The templates/ folder with dashboard.html
- The data/ folder with your dataset

## Deployment

1. **Choose a Deployment Platform:**
   - Options include Render, Heroku, or Railway.

2. **Push Your Code to GitHub:**
   - Ensure your repository is up-to-date.

3. **Deploy the Application:**
   - Follow the chosen platform's instructions to deploy your Flask API.

4. **Test the Public URL:**
   - Once deployed, test all endpoints on the live URL to ensure everything works correctly.

## Additional Notes

### Jupyter Notebook Work
The ML models were trained and tested in Jupyter Notebook. The notebook helped in rapid prototyping and data exploration. The saved model files and the training columns (used for one-hot encoding) are now integrated into the Flask API for real-time predictions and blockchain logging.

### Data Persistence
The blockchain data is stored in blockchain_data.json to ensure that records persist even after restarting the Flask app.
```