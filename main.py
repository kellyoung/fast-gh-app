from fastapi import FastAPI, Request, HTTPException
from lib.installation_store import InstallationStore
import copy

app = FastAPI()
installation_store = InstallationStore()


@app.post("/github-webhook")
async def github_webhook(request: Request):
    try:
        event = request.headers["X-GitHub-Event"]
        data = await request.json()

        if event == "installation_repositories":
            handle_installation_repositories(data)
        elif event == "installation":
            handle_installation(data)
        else:
            raise HTTPException(
                status_code=400, detail="Unsupported GitHub event"
            )

        return {"message": "Webhook received successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def handle_installation_repositories(data):
    # Handle installation_repositories event here
    print("Received installation_repositories event")
    print("# installation account", data["installation"]["account"]["login"])
    print("# installation action", data["action"])
    print("# installation id", data["installation"]["id"])
    print('# data', data)
    # TO DO figure out how to handle organizations
    github_account = (
        data.get("installation", {}).get("account", {}).get("login")
    )
    installation_id = data.get("installation", {}).get("id")
    action = data.get("action")

    print("### github_account", github_account)
    print('### installation_id', installation_id)

    existing_installation = installation_store.get(github_account) or {
        "username": github_account,
        "installation_id": installation_id,
        "all_repos": False,
        "repos": [],
        "deleted": False,
    }
    print("### existing installation", existing_installation)

    if existing_installation and action == "removed":
        removed_repos = data.get("repositories_removed", [])
        removed_repo_names = [repo["name"] for repo in removed_repos]

        print("### removed repos", removed_repo_names)
        updated_installation = copy.deepcopy(existing_installation)

        curr_repos = set(existing_installation.get("repos"))
        # this is the POTENTIAL PROBLEM AREA
        for repo in removed_repo_names:
            curr_repos.discard(repo)
        print('### repos left', curr_repos)
        updated_installation["repos"] = list(curr_repos)
        updated_installation["all_repos"] = False
        installation_store.create_or_update(updated_installation)
        return

    selected_all = data.get("repository_selection") == "all"

    if action == "added" and not selected_all:
        added_repos = data.get("repositories_added", [])
        added_repo_names = [repo["name"] for repo in added_repos]

        print("### added repositories", added_repo_names)

        updated_installation = copy.deepcopy(existing_installation)

        curr_repos = set(existing_installation.get("repos"))
        for repo in added_repo_names:
            curr_repos.add(repo)

        updated_installation["repos"] = list(curr_repos)
        updated_installation["all_repos"] = False
        installation_store.create_or_update(updated_installation)
        return

    if action == "added" and selected_all:
        print("added all repos")
        # clear set and set access_all to true
        updated_installation = copy.deepcopy(existing_installation)
        updated_installation["repos"] = []
        updated_installation["all_repos"] = True
        installation_store.create_or_update(updated_installation)
        return


def handle_installation(data):
    # Handle installation event here
    print("Received installation event")
    print(data)

    github_account = (
        data.get("installation", {}).get("account", {}).get("login")
    )
    installation_id = data.get("installation", {}).get("id")
    action = data.get("action")

    print("### github account", github_account)
    print("### installation_id", installation_id)
    print("### action", action)

    installation = {
        "username": github_account,
        "installation_id": installation_id,
        "all_repos": False,
        "repos": [],
        "deleted": False,
    }

    if action == "deleted" or action == "suspended":
        # set installation to deleted=True
        print("### installation deleted")
        installation["deleted"] = True
        installation_store.create_or_update(installation)
        return

    selected_all = (
        data.get("installation", {}).get("repository_selection") == "all"
    )
    if selected_all and (action == "created" or action == "unsuspended"):
        # create a new data object, where select = all
        print("### created installation,  selected all repos")
        installation["all_repos"] = True
        installation_store.create_or_update(installation)
        return

    if action == "created" or action == "unsuspended":
        print("### created installation, selected repos")
        added_repos = data.get("repositories", [])
        added_repo_names = [repo["name"] for repo in added_repos]
        # create a new record with repo names set to true
        installation["repos"] = added_repo_names
        installation_store.create_or_update(installation)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
