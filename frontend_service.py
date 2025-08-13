#!/usr/bin/env python3
"""
Frontend Microservice - Web Dashboard
A simple Flask-based frontend service that provides a web interface for user management.
"""

from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import requests
import logging
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Backend service configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8086')

# HTML Templates
MAIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Management Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-bottom: 20px; }
        .stats { display: flex; gap: 20px; margin-bottom: 20px; }
        .stat-card { background: #007bff; color: white; padding: 15px; border-radius: 5px; flex: 1; text-align: center; }
        .user-form { background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .user-form input, .user-form select { margin: 5px; padding: 8px; width: 200px; }
        .user-form button { background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
        .user-form button:hover { background: #218838; }
        .users-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .users-table th, .users-table td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        .users-table th { background-color: #f8f9fa; }
        .users-table tr:nth-child(even) { background-color: #f9f9f9; }
        .btn { padding: 5px 10px; margin: 2px; border: none; border-radius: 3px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-warning { background: #ffc107; color: black; }
        .alert { padding: 15px; margin-bottom: 20px; border: 1px solid transparent; border-radius: 4px; }
        .alert-success { color: #155724; background-color: #d4edda; border-color: #c3e6cb; }
        .alert-danger { color: #721c24; background-color: #f8d7da; border-color: #f5c6cb; }
        .service-status { text-align: right; color: #6c757d; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 DevOps Microservices Demo</h1>
            <p>User Management Dashboard - Frontend Service</p>
            <div class="service-status">
                Backend: {{ backend_status }} | Frontend: {{ frontend_status }} | Last Updated: {{ timestamp }}
            </div>
        </div>

        {% if message %}
        <div class="alert alert-{{ message_type }}">{{ message }}</div>
        {% endif %}

        <div class="stats">
            <div class="stat-card">
                <h3>{{ stats.total_users if stats else 'N/A' }}</h3>
                <p>Total Users</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.service_info.environment if stats else 'N/A' }}</h3>
                <p>Environment</p>
            </div>
            <div class="stat-card">
                <h3>{{ stats.service_info.version if stats else 'N/A' }}</h3>
                <p>Backend Version</p>
            </div>
        </div>

        <div class="user-form">
            <h3>➕ Add New User</h3>
            <form method="POST" action="/add_user">
                <input type="text" name="name" placeholder="Full Name" required>
                <input type="email" name="email" placeholder="Email Address" required>
                <select name="role">
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                    <option value="moderator">Moderator</option>
                </select>
                <button type="submit">Add User</button>
            </form>
        </div>

        <h3>👥 User List</h3>
        {% if users %}
        <table class="users-table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Created At</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for user in users %}
                <tr>
                    <td>{{ user.id[:8] }}...</td>
                    <td>{{ user.name }}</td>
                    <td>{{ user.email }}</td>
                    <td>{{ user.role }}</td>
                    <td>{{ user.created_at[:10] }}</td>
                    <td>
                        <a href="/delete_user/{{ user.id }}" class="btn btn-danger" 
                           onclick="return confirm('Are you sure you want to delete this user?')">Delete</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>No users found or backend service unavailable.</p>
        {% endif %}

        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #6c757d; text-align: center;">
            <p>🔧 DevOps Demo - Frontend Service v1.0.0</p>
            <p>Backend URL: {{ backend_url }}</p>
        </div>
    </div>
</body>
</html>
"""

def call_backend_api(endpoint, method='GET', data=None):
    """Helper function to call backend API"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        logger.info(f"Calling backend API: {method} {url}")

        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=5)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()
        return response.json(), response.status_code

    except requests.exceptions.RequestException as e:
        logger.error(f"Backend API call failed: {e}")
        return {"error": str(e)}, 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    # Check backend health
    backend_health, status_code = call_backend_api('/health')
    backend_status = "healthy" if status_code == 200 else "unhealthy"

    return jsonify({
        "status": "healthy",
        "service": "frontend-dashboard",
        "backend_status": backend_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }), 200

@app.route('/')
def dashboard():
    """Main dashboard page"""
    logger.info("GET / - Loading dashboard")

    # Get users from backend
    users_response, users_status = call_backend_api('/api/users')
    users = users_response.get('users', []) if users_status == 200 else []

    # Get stats from backend
    stats_response, stats_status = call_backend_api('/api/stats')
    stats = stats_response if stats_status == 200 else None

    # Check backend health
    backend_health, backend_status_code = call_backend_api('/health')
    backend_status = "🟢 Online" if backend_status_code == 200 else "🔴 Offline"

    return render_template_string(
        MAIN_TEMPLATE,
        users=users,
        stats=stats,
        backend_status=backend_status,
        frontend_status="🟢 Online",
        backend_url=BACKEND_URL,
        timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        message=request.args.get('message'),
        message_type=request.args.get('type', 'success')
    )

@app.route('/add_user', methods=['POST'])
def add_user():
    """Add a new user via backend API"""
    logger.info("POST /add_user - Adding new user")

    user_data = {
        'name': request.form['name'],
        'email': request.form['email'],
        'role': request.form['role']
    }

    response, status_code = call_backend_api('/api/users', 'POST', user_data)

    if status_code == 201:
        message = f"User '{user_data['name']}' added successfully!"
        message_type = "success"
    else:
        message = f"Failed to add user: {response.get('error', 'Unknown error')}"
        message_type = "danger"

    return redirect(url_for('dashboard', message=message, type=message_type))

@app.route('/delete_user/<user_id>')
def delete_user(user_id):
    """Delete a user via backend API"""
    logger.info(f"GET /delete_user/{user_id} - Deleting user")

    response, status_code = call_backend_api(f'/api/users/{user_id}', 'DELETE')

    if status_code == 200:
        message = "User deleted successfully!"
        message_type = "success"
    else:
        message = f"Failed to delete user: {response.get('error', 'Unknown error')}"
        message_type = "danger"

    return redirect(url_for('dashboard', message=message, type=message_type))

@app.route('/api/frontend-stats')
def frontend_stats():
    """Get frontend service statistics"""
    logger.info("GET /api/frontend-stats - Fetching frontend statistics")

    # Get backend stats
    backend_stats, backend_status = call_backend_api('/api/stats')

    stats = {
        "frontend_service": {
            "name": "frontend-dashboard",
            "version": "1.0.0",
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "backend_url": BACKEND_URL
        },
        "backend_status": "online" if backend_status == 200 else "offline",
        "backend_stats": backend_stats if backend_status == 200 else None,
        "timestamp": datetime.utcnow().isoformat()
    }

    return jsonify(stats), 200

@app.errorhandler(404)
def not_found(error):
    return render_template_string("""
    <h1>404 - Page Not Found</h1>
    <p>The requested page could not be found.</p>
    <a href="/">← Back to Dashboard</a>
    """), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return render_template_string("""
    <h1>500 - Internal Server Error</h1>
    <p>Something went wrong on the frontend service.</p>
    <a href="/">← Back to Dashboard</a>
    """), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8084))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    logger.info(f"Starting Frontend Dashboard Service on port {port}")
    logger.info(f"Backend URL configured as: {BACKEND_URL}")
    app.run(host='0.0.0.0', port=port, debug=debug)
