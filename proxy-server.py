#!/usr/bin/env python3
"""
Simple CORS proxy server to handle token requests
"""
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/proxy/tokens/generate', methods=['POST'])
def proxy_token():
    """Proxy token requests to the AWS endpoint"""
    try:
        # Get the agent_name from query parameters
        agent_name = request.args.get('agent_name', 'agent-1')
        
        # AWS endpoint
        aws_url = f"https://live.xpectrum-ai.com/tokens/generate?agent_name={agent_name}"
        
        # Headers to forward
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': 'xpectrum-ai@123'
        }
        
        # For token generation, we don't need a request body
        # The AWS endpoint expects just the headers and query parameters
        data = {}  # Empty body is fine for this endpoint
        
        print(f"Proxying request to: {aws_url}")
        print(f"Headers: {headers}")
        print(f"Agent name: {agent_name}")
        
        # Make request to AWS
        response = requests.post(aws_url, headers=headers, json=data)
        
        print(f"AWS response status: {response.status_code}")
        print(f"AWS response: {response.text}")
        
        # Return the response
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        print(f"Proxy error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("Starting CORS proxy server on http://localhost:5001")
    print("Use this URL in your browser client instead of the AWS endpoint directly")
    app.run(host='0.0.0.0', port=5001, debug=True) 