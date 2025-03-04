from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import locale
import json
import os
import random
from pathlib import Path
from functools import wraps

app = Flask(__name__)
CORS(app)

# At the top of app.py, modify the locale setting
try:
    locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, '')  # Use default locale

# Create a helper function for currency formatting
def format_currency(value):
    try:
        return locale.currency(value, grouping=True)
    except locale.Error:
        return f"£{value:,.2f}"  # Fallback formatting

# Update the file paths to be relative to the app directory
BASE_DIR = Path(__file__).resolve().parent
USERS_FILE = os.path.join(BASE_DIR, 'users.json')
METRICS_FILE = os.path.join(BASE_DIR, 'metrics.json')

def ensure_data_files_exist():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({'count': 44, 'history': []}, f)
    
    if not os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, 'w') as f:
            json.dump({
                'website_visits': [],
                'signup_page_views': [],
                'signups': [],
                'connected_signups': [],
                'free_to_paid': []
            }, f)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {'count': 44, 'history': []}  # Start with 44 users

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def load_metrics():
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, 'r') as f:
            return json.load(f)
    return {
        'website_visits': [],
        'signup_page_views': [],
        'signups': [],
        'connected_signups': [],
        'free_to_paid': []
    }

def save_metrics(metrics):
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f)

def get_metric_stats(metric_data):
    if not metric_data:
        return {
            'today': 0, 
            'yesterday': 0, 
            'week_avg': 0, 
            'trends': {
                '24h': '+0%',
                '7d': '+0%',
                '30d': '+0%'
            }
        }
    
    # Sort data by date
    sorted_data = sorted(metric_data, key=lambda x: x['date'])
    
    # Get the most recent date's value
    current_value = sorted_data[-1]['value'] if sorted_data else 0
    
    # Get previous day's value
    prev_day_value = sorted_data[-2]['value'] if len(sorted_data) > 1 else 0
    
    # Get values for different time periods
    week_ago_value = next((item['value'] for item in sorted_data[:-7] if item), 0)
    month_ago_value = next((item['value'] for item in sorted_data[:-30] if item), 0)
    
    # Calculate week average
    week_data = [item['value'] for item in sorted_data[-7:]]
    week_avg = sum(week_data) / len(week_data) if week_data else 0
    
    def calculate_trend(current, previous):
        if previous == 0:
            return '+0%'
        trend = ((current - previous) / previous * 100)
        return f"{'+' if trend >= 0 else ''}{trend:.1f}%"
    
    trends = {
        '24h': calculate_trend(current_value, prev_day_value),
        '7d': calculate_trend(current_value, week_ago_value),
        '30d': calculate_trend(current_value, month_ago_value)
    }
    
    return {
        'today': current_value,
        'yesterday': prev_day_value,
        'week_avg': round(week_avg, 1),
        'trends': trends
    }

def calculate_funnel_metrics(metrics_data, date=None):
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Get values for the specified date
    def get_value(metric):
        entries = metrics_data[metric]
        value = next((item['value'] for item in entries if item['date'] == date), 0)
        return value if value > 0 else 1  # Avoid division by zero
    
    visits = get_value('website_visits')
    signup_views = get_value('signup_page_views')
    signups = get_value('signups')
    connected = get_value('connected_signups')
    paid = get_value('free_to_paid')
    
    # Calculate conversion rates
    funnel_metrics = {
        'visit_to_signup_view': {
            'rate': (signup_views / visits) * 100,
            'previous': visits,
            'current': signup_views
        },
        'signup_view_to_signup': {
            'rate': (signups / signup_views) * 100,
            'previous': signup_views,
            'current': signups
        },
        'signup_to_connected': {
            'rate': (connected / signups) * 100,
            'previous': signups,
            'current': connected
        },
        'connected_to_paid': {
            'rate': (paid / connected) * 100,
            'previous': connected,
            'current': paid
        },
        'total_conversion': {
            'rate': (paid / visits) * 100,
            'previous': visits,
            'current': paid
        }
    }
    
    return funnel_metrics

def calculate_wow_growth(metrics_data):
    today = datetime.now().date()
    week_ago = (today - timedelta(days=7)).strftime('%Y-%m-%d')
    today = today.strftime('%Y-%m-%d')
    
    wow_growth = {}
    for metric, data in metrics_data.items():
        today_value = next((item['value'] for item in data if item['date'] == today), 0)
        week_ago_value = next((item['value'] for item in data if item['date'] == week_ago), 0)
        
        if week_ago_value > 0:
            growth = ((today_value - week_ago_value) / week_ago_value) * 100
        else:
            growth = 0
            
        wow_growth[metric] = {
            'growth': growth,
            'current': today_value,
            'previous': week_ago_value
        }
    
    return wow_growth

def populate_dummy_data():
    metrics_data = {
        'website_visits': [],
        'signup_page_views': [],
        'signups': [],
        'connected_signups': [],
        'free_to_paid': []
    }
    
    # Base values with realistic conversion rates
    base_values = {
        'website_visits': 1000,
        'signup_page_views': 300,  # ~30% of visits
        'signups': 50,            # ~17% of signup views
        'connected_signups': 30,  # ~60% of signups
        'free_to_paid': 10        # ~33% of connected
    }
    
    # Daily variation ranges (min%, max%)
    daily_variation = {
        'website_visits': (-15, 25),
        'signup_page_views': (-10, 20),
        'signups': (-8, 18),
        'connected_signups': (-5, 15),
        'free_to_paid': (-3, 13)
    }
    
    # Generate data for last 30 days
    for i in range(30, -1, -1):  # Include today
        date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        daily_metrics = {}
        
        # Generate values maintaining funnel relationships
        for metric in metrics_data:
            if i == 30:  # First day
                value = base_values[metric]
            else:
                prev_value = metrics_data[metric][-1]['value']
                min_var, max_var = daily_variation[metric]
                variation = random.uniform(min_var, max_var) / 100
                value = int(prev_value * (1 + variation))
                
                # Ensure funnel logic is maintained
                if metric == 'signup_page_views':
                    value = min(value, daily_metrics['website_visits'])
                elif metric == 'signups':
                    value = min(value, daily_metrics['signup_page_views'])
                elif metric == 'connected_signups':
                    value = min(value, daily_metrics['signups'])
                elif metric == 'free_to_paid':
                    value = min(value, daily_metrics['connected_signups'])
            
            daily_metrics[metric] = value
            metrics_data[metric].append({
                'date': date,
                'value': value
            })
            
            # Add some weekly patterns
            if datetime.strptime(date, '%Y-%m-%d').weekday() in [5, 6]:  # Weekend
                metrics_data[metric][-1]['value'] = int(value * 0.7)  # 30% lower on weekends
    
    # Ensure today has good data for all visualizations
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Adjust today's and yesterday's data to ensure positive trends
    for metric in metrics_data:
        today_value = next((item for item in metrics_data[metric] if item['date'] == today), None)
        yesterday_value = next((item for item in metrics_data[metric] if item['date'] == yesterday), None)
        
        if today_value and yesterday_value:
            # Ensure today is slightly higher than yesterday
            today_value['value'] = int(yesterday_value['value'] * random.uniform(1.05, 1.15))
    
    return metrics_data

@app.route('/')
def index():
    users_data = load_users()
    metrics_data = load_metrics()
    
    # Use yesterday's date for latest metrics
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Get baseline paying users (44) plus any new paid conversions from metrics
    baseline_users = 44
    total_new_paid_users = 0
    
    # Sum up all free_to_paid conversions from metrics
    if metrics_data and 'free_to_paid' in metrics_data:
        total_new_paid_users = sum(item['value'] for item in metrics_data['free_to_paid'])
    
    # Calculate current total paying users
    current_users = baseline_users + total_new_paid_users

    # Set target date and ARR
    target_date = datetime(2025, 12, 31)
    target_arr = 1_000_000
    
    # Calculate current ARR from actual metrics
    product_price = 22.49
    monthly_revenue = product_price * current_users
    current_arr = monthly_revenue * 12  # This calculates our actual current ARR

    # Calculate users needed for £1M ARR
    monthly_revenue_needed = target_arr / 12
    users_needed = int(monthly_revenue_needed / product_price)
    users_needed_formatted = "{:,}".format(users_needed)
    
    # Calculate time remaining
    now = datetime.now()
    time_diff = target_date - now
    
    days = time_diff.days
    hours = time_diff.seconds // 3600
    minutes = (time_diff.seconds % 3600) // 60
    seconds = time_diff.seconds % 60

    # Calculate progress percentage
    progress = (current_arr / target_arr) * 100

    # Add monthly target and users needed per month calculation
    days_remaining = time_diff.days
    months_remaining = days_remaining / 30
    monthly_target = target_arr / (days_remaining / 30) if days_remaining > 0 else 0
    
    # Calculate how many new users needed per month
    users_remaining = users_needed - current_users
    monthly_users_needed = int(users_remaining / months_remaining) if months_remaining > 0 else 0
    monthly_users_formatted = "{:,}".format(monthly_users_needed)

    # Get yesterday's metrics for display (renamed from todays_metrics)
    latest_metrics = {
        'new_paid_users': next((item['value'] for item in metrics_data.get('free_to_paid', []) 
                              if item['date'] == yesterday), 0),
        'arr_added': next((item['value'] for item in metrics_data.get('free_to_paid', []) 
                         if item['date'] == yesterday), 0) * product_price * 12
    }

    # Update users_data history with metrics-based changes
    if latest_metrics['new_paid_users'] > 0:
        users_data['history'].append({
            'date': yesterday,  # Use yesterday's date
            'added': latest_metrics['new_paid_users'],
            'total': current_users
        })
        save_users(users_data)

    def calculate_probability():
        # This is a simple probability model - you can adjust the weights and factors
        base_probability = 100
        
        # Calculate monthly growth needed
        time_remaining_months = days_remaining / 30
        users_to_gain = users_needed - current_users
        
        # Calculate required monthly user growth
        required_monthly_users = users_to_gain / time_remaining_months
        
        # Calculate growth rate relative to current user base
        relative_growth_rate = required_monthly_users / current_users
        
        # Adjust probability based on growth rate
        # Allow for more aggressive growth rates for early-stage startups
        # If we need to grow more than 100% per month, start reducing probability
        growth_factor = max(0, 1 - (relative_growth_rate / 1.0))
        
        # Time factor - less harsh reduction
        # Start reducing after 12 months remaining instead of 24
        time_factor = min(1, time_remaining_months / 12)
        
        # Weight the factors (adjust these weights to tune the model)
        growth_weight = 0.7  # Growth rate is most important
        time_weight = 0.3   # Time pressure is less important
        
        # Calculate final probability
        probability = base_probability * (
            (growth_factor * growth_weight) +
            (time_factor * time_weight)
        )
        
        return max(0, min(100, probability))  # Ensure between 0 and 100

    # Calculate probability
    probability = calculate_probability()
    probability_formatted = "{:.1f}".format(probability)
    
    # Get probability color (red to green gradient)
    if probability < 30:
        probability_color = '#ff4757'  # Red
    elif probability < 70:
        probability_color = '#ffa502'  # Orange
    else:
        probability_color = '#2ed573'  # Green

    return render_template('index.html',
                         days=days,
                         hours=hours,
                         minutes=minutes,
                         seconds=seconds,
                         current_arr=format_currency(current_arr),
                         target_arr=format_currency(target_arr),
                         monthly_target=format_currency(monthly_target),
                         progress=progress,
                         product_price=format_currency(product_price),
                         monthly_users="{:,}".format(current_users),
                         monthly_revenue=format_currency(monthly_revenue),
                         users_needed=users_needed_formatted,
                         monthly_users_needed=monthly_users_formatted,
                         probability=probability_formatted,
                         probability_color=probability_color,
                         latest_metrics=latest_metrics,  # Renamed from todays_metrics
                         user_history=reversed(users_data['history'][-5:]))

def check_auth(username, password):
    """Check if a username/password combination is valid."""
    return username == os.environ.get('ADMIN_USERNAME') and password == os.environ.get('ADMIN_PASSWORD')

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/metrics', methods=['GET', 'POST'])
@requires_auth
def metrics():
    # Get selected date from query parameter, default to yesterday
    selected_date = request.args.get('date')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    if not selected_date:
        selected_date = yesterday
    
    metrics_data = load_metrics()
    
    if request.method == 'POST':
        # Always save as yesterday's date when adding new metrics
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        for metric in metrics_data.keys():
            value = int(request.form.get(metric, 0))
            # Add new data point with yesterday's date
            metrics_data[metric].append({
                'date': yesterday,  # Use yesterday's date instead of form date
                'value': value
            })
            # Keep only last 30 days
            metrics_data[metric] = metrics_data[metric][-30:]
        
        save_metrics(metrics_data)
        return redirect('/metrics')
    
    # Process metrics for display for the selected date
    processed_metrics = {}
    
    # Calculate ARR pipeline first
    product_price = 22.49
    arr_pipeline_data = []
    for date_entry in metrics_data.get('free_to_paid', []):
        arr_pipeline_data.append({
            'date': date_entry['date'],
            'value': round(date_entry['value'] * product_price * 12, 2)  # Convert to annual value
        })
    
    # Filter ARR pipeline data for selected date
    selected_arr_data = [d for d in arr_pipeline_data if d['date'] <= selected_date]
    processed_metrics['ARR Pipeline'] = get_metric_stats(selected_arr_data)  # Changed from 'arr_pipeline'
    
    # Process other metrics
    for metric, data in metrics_data.items():
        # Filter data for the selected date
        selected_data = [d for d in data if d['date'] <= selected_date]
        processed_metrics[metric] = get_metric_stats(selected_data)
    
    # Calculate funnel metrics for selected date
    funnel_metrics = calculate_funnel_metrics(metrics_data, selected_date)
    
    # Calculate week-over-week growth
    wow_growth = calculate_wow_growth(metrics_data)
    
    return render_template('metrics.html', 
                         metrics=processed_metrics,
                         metrics_history=metrics_data,
                         funnel_metrics=funnel_metrics,
                         wow_growth=wow_growth,
                         datetime=datetime,
                         yesterday_date=selected_date)

@app.route('/metrics/reset', methods=['POST'])
def reset_metrics():
    # Initialize empty metrics data
    empty_metrics = {
        'website_visits': [],
        'signup_page_views': [],
        'signups': [],
        'connected_signups': [],
        'free_to_paid': []
    }
    save_metrics(empty_metrics)
    return redirect('/metrics')

@app.route('/metrics/populate', methods=['POST'])
def populate_metrics():
    metrics_data = populate_dummy_data()
    save_metrics(metrics_data)
    return redirect('/metrics')

@app.route('/api/metrics')
def api_metrics():
    users_data = load_users()
    metrics_data = load_metrics()
    
    # Get baseline paying users (44) plus any new paid conversions from metrics
    baseline_users = 44
    total_new_paid_users = 0
    
    # Sum up all free_to_paid conversions from metrics
    if metrics_data and 'free_to_paid' in metrics_data:
        total_new_paid_users = sum(item['value'] for item in metrics_data['free_to_paid'])
    
    # Calculate current total paying users
    current_users = baseline_users + total_new_paid_users
    
    # Calculate current ARR
    product_price = 22.49
    monthly_revenue = product_price * current_users
    current_arr = monthly_revenue * 12
    
    return jsonify({
        'current_arr': current_arr,
        'target_arr': 1000000,
        'target_date': '2025-12-31'
    })

# Call this when the app starts
ensure_data_files_exist()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port) 