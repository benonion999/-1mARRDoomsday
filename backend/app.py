from flask import jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/metrics')
def api_metrics():
    users_data = load_users()
    metrics_data = load_metrics()
    current_users = users_data['count']
    
    # Calculate current ARR
    product_price = 22.49
    monthly_revenue = product_price * current_users
    current_arr = monthly_revenue * 12
    
    return jsonify({
        'current_arr': current_arr,
        'target_arr': 1000000,
        'target_date': '2025-12-31'
    }) 