import json
import requests
import os

CHATBOT_URL = 'https://eb55-186-31-183-18.ngrok-free.app/query'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HEADERS = {
    "Content-Type": "application/json"
}
PARAMS = {
    "key": f"{GEMINI_API_KEY}"  # API Key as a query parameter
}


if __name__ == '__main__':
    base_url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'
    message = 'How AI work, tell me concisely'

    # Define the request payload
    PAYLOAD = {
        "contents": [{
            "parts": [{"text": f"{message}"}]
        }]
    }
    # DEBUG
    print(f'{base_url} - {message}')
    response = requests.post(
        base_url,
        headers=HEADERS,
        params=PARAMS,
        json=PAYLOAD,
        timeout=10,
    )

    # Check for errors
    response.raise_for_status()

    # Parse JSON response
    data = response.json()
    print("Response:", json.dumps(data, indent=2))  # Pretty print response

    if response.status_code == 200:
        print('Successssss')
        # response_data = response.json().get("message", "No response")
        #

    else:
        print(f"API error: {response.status_code}, {response.text}")
