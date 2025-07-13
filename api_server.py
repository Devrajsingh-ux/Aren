"""
AREN API Server
This module provides a RESTful API for the AREN assistant.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from brain.engine import ArenEngine
from utils.logging_utils import logger

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize AREN engine
aren_engine = ArenEngine()

@app.route('/', methods=['GET'])
def home():
    """Root endpoint to confirm server is running"""
    return "AREN is running now.", 200

@app.route('/status', methods=['GET'])
def status():
    """Health check endpoint"""
    try:
        # Simple test to see if AREN engine is working
        test_response = aren_engine.process_input("test")
        if test_response:
            return jsonify({"status": "ok", "message": "AREN API is operational"}), 200
        else:
            return jsonify({"status": "error", "message": "AREN engine not responding"}), 500
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/listen', methods=['POST'])
def listen():
    """Process user input and return AREN's response"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"status": "error", "message": "Missing 'text' in request"}), 400
        
        user_input = data['text']
        user_id = data.get('userId', 'default_user')
        
        logger.info(f"API request from user {user_id}: {user_input}")
        
        # Process the input using AREN engine
        response = aren_engine.process_input(user_input)
        
        return jsonify({
            "status": "success",
            "reply": response,
            "userId": user_id
        }), 200
    except Exception as e:
        logger.error(f"API processing error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def run_server(host='::', port=1906):
    """Run the API server with IPv6 support"""
    logger.info(f"Starting AREN API server on {host}:{port}")
    
    # Use standard Flask run method with IPv6 host
    app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    # Get port from command line arguments if provided
    port = 1906
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            logger.error(f"Invalid port number: {sys.argv[1]}")
    
    run_server(port=port) 