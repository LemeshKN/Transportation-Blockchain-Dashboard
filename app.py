from flask import Flask,jsonify,request,render_template
from blockchain import TransportationBlockchain
import logging
import numpy as np
import pandas as pd 
import joblib  # Import joblib to load saved machine learning models
import json 

# Load the training columns from the JSON file
with open("training_columns.json", "r") as f:
    training_columns = json.load(f)

print("Training columns loaded:", len(training_columns), "features")

# Load the trained models from their saved .pkl files
# These models were trained in Jupyter Notebook and saved using joblib.dump()

logir_model = joblib.load("logistic_regression_model.pkl")  # Load the Logistic Regression model
randomf_model = joblib.load("random_forest_model.pkl")  # Load the Random Forest model
xgb_model = joblib.load("xgboost_model.pkl")  # Load the XGBoost model


logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
blockchain = TransportationBlockchain() # Initialize blockchain

@app.route('/')
def home():
    return "Hello, Blockchain!"

@app.route('/chain', methods=['GET'])
def get_chain():
    """
    Returns the entire blockchain.
    """
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index": block["index"],  # Changed from .index to ["index"]
            "timestamp": block["timestamp"],
            "delay_data": block["delay_data"],
            "previous_hash": block["previous_hash"],
            "hash": block["hash"]
        })
    return jsonify({"length": len(chain_data), "chain": chain_data}), 200

@app.route('/add_delay', methods=['POST'])
def add_delay():
    """
    Adds a new delay record to the blockchain.
    """
    try:
        data = request.get_json()

        required_fields = ["location", "route", "delay_minutes"]
        if not all(field in data for field in required_fields):
           return jsonify({"error": "Missing required fields"}), 400

        new_block = blockchain.add_delay_record(data)
    
        return jsonify({
           "message": "New delay record added",
           "block": {
                "index": new_block["index"],  # Changed from .index to ["index"]
                "timestamp": new_block["timestamp"],
                "delay_data": new_block["delay_data"],
                "previous_hash": new_block["previous_hash"],
                "hash": new_block["hash"]
            }
        }), 201
    except Exception as e:
        logging.error(f"Error adding delay record: {e}")
        return jsonify({"error": "An error occurred while adding the delay"}), 500

@app.route('/last_block', methods=['GET'])
def get_last_block():
    """
    Returns the last block in the blockchain.
    """
    return jsonify({
        "last_block": {
            "index": blockchain.chain[-1]["index"],  # Changed from .index to ["index"]
            "timestamp": blockchain.chain[-1]["timestamp"],
            "delay_data": blockchain.chain[-1]["delay_data"],
            "previous_hash": blockchain.chain[-1]["previous_hash"],
            "hash": blockchain.chain[-1]["hash"]
        }
    }), 200

# Rest of the code remains the same as it doesn't access block attributes
@app.route('/validate_chain', methods=['GET'])
def validate_chain():
    if blockchain.is_chain_valid():
        return jsonify({"message": "Blockchain is valid "}), 200
    else:
        return jsonify({"message": "Blockchain is NOT valid "}), 400


@app.route('/reset_chain', methods=['DELETE'])
def reset_chain():
    global blockchain
    blockchain = TransportationBlockchain()
    return jsonify({"message": "Blockchain has been reset"}), 200



# New Route: /predict for ML Predictions
@app.route('/predict', methods=['POST'])
def predict():
    """
    Predicts delay time using the ML models based on raw input data.
    Expects JSON input with the raw features:
      - Route
      - Day
      - Incident
      - Direction

    The raw input is one-hot encoded to ensure it matches the features used during training.
    """
    try:
        # Get input data from the request.
        data = request.get_json()
        required_fields = ["Route", "Day", "Incident", "Direction"]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        # Create a DataFrame from the raw input data.
        raw_df = pd.DataFrame([{
            "Route": data["Route"],
            "Day": data["Day"],
            "Incident": data["Incident"],
            "Direction": data["Direction"]
        }])

        # One-hot encode the input data.
        input_encoded = pd.get_dummies(raw_df)
        # Reindex to ensure all training columns are present; fill missing columns with 0.
        input_encoded = input_encoded.reindex(columns=training_columns, fill_value=0)
        # Convert the encoded DataFrame to a NumPy array.
        input_data = input_encoded.values

        # Get predictions from each model
        logir_pred = logir_model.predict(input_data)[0]
        randomf_pred = randomf_model.predict(input_data)[0]
        xgb_pred = xgb_model.predict(input_data)[0]

        # Map numeric predictions (0 or 1) to user-friendly labels
        def map_prediction(pred):
           return "Delay Expected" if pred == 1 else "No Delay"
        
         # Create labels for each prediction
        logir_label = map_prediction(logir_pred)
        randomf_label = map_prediction(randomf_pred)
        xgb_label = map_prediction(xgb_pred)


        # Return the predictions and their labels as JSON response
        return jsonify({
            "logistic_regression_prediction": int(logir_pred),"\n"
            "logistic_regression_label": logir_label,"\n"
            "random_forest_prediction": int(randomf_pred),"\n"
            "random_forest_label": randomf_label,"\n"
            "xgboost_prediction": int(xgb_pred),"\n"
            "xgboost_label": xgb_label
        }), 200

    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Renders the dashboard to visualize the blockchain ledger and provide a prediction form.
    """
    # Pass the blockchain data (chain) to the template
    return render_template("dashboard.html", chain=blockchain.chain)

@app.route('/delay_trends', methods=['GET'])
def delay_trends():
    """
    Calculates and returns the average delay per day using the static dataset.
    This data is used to update the line chart on the dashboard.
    """
    try:
        # Load the dataset from the 'data' folder
        df = pd.read_csv("../data/ttc_bus_delay_data_2024.csv")
        
        # Ensure the dataset has the necessary columns
        # For example, 'Day' (e.g., Monday) and 'Min Delay' (delay in minutes)
        if 'Day' not in df.columns or 'Min Delay' not in df.columns:
            return jsonify({"error": "Dataset missing required columns."}), 400
        
        # Group the data by day and calculate the average delay for each day
        avg_delays = df.groupby('Day')['Min Delay'].mean()
        
        # Reorder the days to a standard week order
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        labels = days_order
        averageDelays = [round(avg_delays.get(day, 0), 2) for day in days_order]
        
        # Return the data as JSON
        return jsonify({"labels": labels, "averageDelays": averageDelays}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)