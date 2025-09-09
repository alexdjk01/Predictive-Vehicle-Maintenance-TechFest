
import json
from flask import Blueprint, request, jsonify

from models.inference import inference

# Create a blueprint for the routes
app_routes = Blueprint('app_routes', __name__)


@app_routes.route('/home/post-data', methods=['POST'])
def post_data():
    data = request.get_json()

    # Process the data as needed
    brand = data.get('brand')
    odometer = data.get('odometer')
    vehicle_type = data.get('vehicletype')
    year = data.get('year')
    time_budget_min = data.get('timebudget')

    obj = inference(data, artifacts_dir="backend-python/models/artifacts")
    obj["vehicle"] = {
        "brand": brand,
        "year": year,
        "vehicletype": vehicle_type,
        "odometer_km": odometer
    }
    obj["ui"] = {"time_budget_min": time_budget_min}

    return jsonify(obj), 200
