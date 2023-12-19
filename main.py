import os
from fastapi import FastAPI, Request, HTTPException
from lib.installation_store import InstallationStore
from lib.handle_webhooks import (
    handle_installation,
    handle_installation_repositories,
)
from lib.installation_token import generate_jwt, generate_installation_token

app_id = os.environ["GITHUB_APP_ID"]
private_key_path = os.environ["PRIVATE_KEY_PATH"]

app = FastAPI()
installation_store = InstallationStore()


@app.post("/github-webhook")
async def github_webhook(request: Request):
    try:
        event = request.headers["X-GitHub-Event"]
        data = await request.json()

        if event == "installation_repositories":
            handle_installation_repositories(data, installation_store)
        elif event == "installation":
            handle_installation(data, installation_store)
        else:
            return {"message": "Unsupported webhook event"}

        return {"message": "Webhook received successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{username}/active-installation")
async def get_active_installation(username: str):
    try:
        active_installation = installation_store.get(username)
        return {"data": active_installation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/installation-token")
async def create_installation_token(request: Request):
    try:
        data = await request.json()
        username = data["username"]
        print(username)
        active_installation_res = await get_active_installation(username)
        active_installation = active_installation_res["data"]
        if not active_installation:
            raise HTTPException(
                status_code=404,
                detail=f"No active installation found for {username}",
            )

        jwt_token = generate_jwt(app_id, private_key_path)
        return generate_installation_token(
            jwt_token, active_installation["installation_id"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
