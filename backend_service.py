#!/usr/bin/env python3
"""
Backend Microservice - User Management API
A simple Flask-based backend service that provides user management functionality.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
import os
import json
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# In-memory storage (in production, this would be a database)
users_db = {
    "1": {
        "id": "1",
        "name": "John Doe",
        "email": "john@example.com",
        "role": "admin",
        "created_at": "2025-01-01T10:00:00Z"
    },
    "2": {
        "id": "2",
        "name": "Jane Smith",
        "email": "jane@example.com",
        "role": "user",
        "created_at": "2025-01-02T11:00:00Z"
    }
}

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "service": "backend-user-service",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }), 200

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    logger.info("GET /api/users - Fetching all users")
    return jsonify({
        "users": list(users_db.values()),
        "count": len(users_db)
    }), 200

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    logger.info(f"GET /api/users/{user_id} - Fetching user")

    if user_id not in users_db:
        return jsonify({"error": "User not found"}), 404

    return jsonify(users_db[user_id]), 200

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    logger.info("POST /api/users - Creating new user")

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Validate required fields
    required_fields = ['name', 'email']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Generate new user
    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "name": data['name'],
        "email": data['email'],
        "role": data.get('role', 'user'),
        "created_at": datetime.utcnow().isoformat()
    }

    users_db[user_id] = new_user
    logger.info(f"Created user: {user_id}")

    return jsonify(new_user), 201

@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """Update an existing user"""
    logger.info(f"PUT /api/users/{user_id} - Updating user")

    if user_id not in users_db:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Update user fields
    user = users_db[user_id]
    for field in ['name', 'email', 'role']:
        if field in data:
            user[field] = data[field]

    user['updated_at'] = datetime.utcnow().isoformat()

    logger.info(f"Updated user: {user_id}")
    return jsonify(user), 200

@app.route('/api/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    logger.info(f"DELETE /api/users/{user_id} - Deleting user")

    if user_id not in users_db:
        return jsonify({"error": "User not found"}), 404

    deleted_user = users_db.pop(user_id)
    logger.info(f"Deleted user: {user_id}")

    return jsonify({"message": "User deleted successfully", "user": deleted_user}), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get service statistics"""
    logger.info("GET /api/stats - Fetching service statistics")

    stats = {
        "total_users": len(users_db),
        "service_info": {
            "name": "backend-user-service",
            "version": "1.0.0",
            "environment": os.getenv('ENVIRONMENT', 'development')
        },
        "timestamp": datetime.utcnow().isoformat()
    }

    return jsonify(stats), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8086))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    logger.info(f"Starting Backend User Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
