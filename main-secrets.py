from fastapi import FastAPI, Request, HTTPException, Depends, Header
from lib.installation_store import InstallationStore
from lib.handle_webhooks import (
    handle_installation,
    handle_installation_repositories,
)
import os

app = FastAPI()
installation_store = InstallationStore()

# Define the GitHub webhook secret
WEBHOOK_SECRET = os.environ["GITHUB_WEBHOOK_SECRET"]


# Dependency to verify GitHub webhook secret
async def verify_signature(
    request: Request, x_hub_signature: str = Header(...)
):
    body = await request.body()
    event_type = request.headers["X-GitHub-Event"]
    json_body = await request.json()
    signature = f"sha1={get_signature(WEBHOOK_SECRET, body)}"

    if not compare_signatures(signature, x_hub_signature):
        raise HTTPException(
            status_code=403, detail="Invalid GitHub webhook signature"
        )

    return {"body": json_body, "event_type": event_type}


def get_signature(secret, data):
    import hmac
    import hashlib

    return hmac.new(secret.encode(), data, hashlib.sha1).hexdigest()


def compare_signatures(sig1, sig2):
    import secrets

    return secrets.compare_digest(sig1, sig2)


@app.post("/github-webhook")
async def github_webhook(request: dict = Depends(verify_signature)):
    try:
        data = request.get("body")
        event = request.get("event_type")

        if event == "installation_repositories":
            handle_installation_repositories(data, installation_store)
        elif event == "installation":
            handle_installation(data, installation_store)
        else:
            raise HTTPException(
                status_code=400, detail="Unsupported GitHub event"
            )

        return {"message": "Webhook received successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
