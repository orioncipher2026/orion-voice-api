#!/usr/bin/env python3
"""Call Les with Orion Voice AI."""

import jwt
import time
import uuid
import requests
import sys

# Config
APP_ID = "312455f6-4460-49f0-9ce4-5e9238e181cb"
PRIVATE_KEY_PATH = r"C:\Users\les-m\.openclaw\workspace\voice-to-ai-engines\private.key"
LES_NUMBER = "15198091100"
ORION_NUMBER = "17806699599"

def get_ngrok_url():
    """Get current ngrok tunnel URL."""
    try:
        tunnels = requests.get("http://127.0.0.1:4040/api/tunnels").json()
        for t in tunnels.get("tunnels", []):
            if "https" in t.get("public_url", ""):
                return t["public_url"].replace("https://", "")
    except:
        pass
    return None

def call_les(ngrok_host=None):
    """Make outbound call to Les."""
    if not ngrok_host:
        ngrok_host = get_ngrok_url()
        if not ngrok_host:
            print("ERROR: Could not get ngrok URL. Is ngrok running?")
            return False
    
    print(f"WebSocket: wss://{ngrok_host}/socket")
    
    # Load private key
    with open(PRIVATE_KEY_PATH) as f:
        private_key = f.read()
    
    # Generate JWT
    token = jwt.encode({
        "application_id": APP_ID,
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "jti": str(uuid.uuid4())
    }, private_key, algorithm="RS256")
    
    # NCCO - include webhook_url to prevent connector crash
    ncco = [
        {
            "action": "talk",
            "text": "Hello Les! Connecting to Orion now.",
            "language": "en-US"
        },
        {
            "action": "connect",
            "endpoint": [{
                "type": "websocket",
                "uri": f"wss://{ngrok_host}/socket?participant=user1&call_direction=outbound&webhook_url=https://{ngrok_host}/event",
                "content-type": "audio/l16;rate=16000"
            }]
        }
    ]
    
    # Make call
    response = requests.post(
        "https://api.nexmo.com/v1/calls",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        json={
            "to": [{"type": "phone", "number": LES_NUMBER}],
            "from": {"type": "phone", "number": ORION_NUMBER},
            "ncco": ncco
        }
    )
    
    print(f"Call status: {response.status_code}")
    data = response.json()
    if response.status_code == 201:
        print(f"Call UUID: {data.get('uuid')}")
        print("Phone should ring now!")
        return True
    else:
        print(f"Error: {data}")
        return False

if __name__ == "__main__":
    ngrok_host = sys.argv[1] if len(sys.argv) > 1 else None
    call_les(ngrok_host)
