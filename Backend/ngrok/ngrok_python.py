from pyngrok import ngrok

from dotenv import load_dotenv
import os

load_dotenv()
# Get ngrok authtoken from environment variables
authtoken = os.getenv("NGROK_AUTHTOKEN")


if not authtoken:
    raise ValueError("NGROK_AUTHTOKEN not found in .env file")


listener = ngrok.forward("localhost:8080", authtoken_from_env=True,
    oauth_provider="google")

print(f"Ingress established at: {listener.url()}")