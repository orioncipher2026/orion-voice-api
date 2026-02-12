#!/usr/bin/env python3
"""Vonage Voice Server - connects calls to ElevenLabs via WebSocket."""

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Configuration
PROCESSOR_SERVER = "03c860a98291e6.lhr.life"  # localhost.run URL for ElevenLabs connector
SERVICE_PHONE = os.environ.get("SERVICE_PHONE", "17806699599")

@app.route("/answer", methods=["GET"])
def answer():
    """Handle incoming calls - connect to ElevenLabs via WebSocket."""
    uuid = request.args.get("uuid", "unknown")
    from_number = request.args.get("from", "unknown")
    
    print(f"[INBOUND] Call from {from_number}, UUID: {uuid}")
    
    # NCCO: Greet, then connect via WebSocket to ElevenLabs connector
    ws_uri = f"wss://{PROCESSOR_SERVER}/socket?participant=user1&call_direction=inbound&peer_uuid={uuid}"
    
    ncco = [
        {
            "action": "talk",
            "text": "Hello! This is Orion. How can I help you today?",
            "language": "en-US",
            "style": 11
        },
        {
            "action": "connect",
            "endpoint": [{
                "type": "websocket",
                "uri": ws_uri,
                "content-type": "audio/l16;rate=16000"
            }]
        }
    ]
    
    return jsonify(ncco)


@app.route("/event", methods=["POST", "GET"])
def event():
    """Handle call events."""
    data = request.json or request.args.to_dict()
    print(f"[EVENT] {data.get('status', 'unknown')}: {data}")
    return "OK", 200


@app.route("/call", methods=["GET"])
def make_call():
    """Trigger outbound call to a number."""
    import jwt
    import time
    import uuid as uuid_lib
    import requests
    
    number = request.args.get("number")
    if not number:
        return "Missing 'number' parameter", 400
    
    # Load credentials
    app_id = "312455f6-4460-49f0-9ce4-5e9238e181cb"
    with open("private.key", "r") as f:
        private_key = f.read()
    
    # Generate JWT
    payload = {
        "application_id": app_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "jti": str(uuid_lib.uuid4())
    }
    token = jwt.encode(payload, private_key, algorithm="RS256")
    
    # NCCO for outbound call
    ncco = [
        {
            "action": "talk",
            "text": "Hello! Connecting you to Orion now.",
            "language": "en-US"
        },
        {
            "action": "connect",
            "endpoint": [{
                "type": "websocket",
                "uri": f"wss://{PROCESSOR_SERVER}/socket?participant=user1&call_direction=outbound",
                "content-type": "audio/l16;rate=16000"
            }]
        }
    ]
    
    # Make the call
    response = requests.post(
        "https://api.nexmo.com/v1/calls",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "to": [{"type": "phone", "number": number}],
            "from": {"type": "phone", "number": SERVICE_PHONE},
            "ncco": ncco
        }
    )
    
    print(f"[OUTBOUND] Calling {number}: {response.status_code}")
    return jsonify(response.json()), response.status_code


if __name__ == "__main__":
    print("="*60)
    print("Vonage Voice Server")
    print(f"Phone: {SERVICE_PHONE}")
    print(f"Connector: {PROCESSOR_SERVER}")
    print("="*60)
    app.run(host="0.0.0.0", port=9000, debug=False)
