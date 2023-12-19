import copy


def handle_installation_repositories(data, installation_store):
    # TO DO figure out how to handle organizations
    github_account = (
        data.get("installation", {}).get("account", {}).get("login")
    )
    installation_id = data.get("installation", {}).get("id")
    action = data.get("action")

    existing_installation = installation_store.get(github_account) or {
        "username": github_account,
        "installation_id": installation_id,
        "all_repos": False,
        "repos": [],
        "deleted": False,
    }

    if existing_installation and action == "removed":
        removed_repos = data.get("repositories_removed", [])
        removed_repo_names = [repo["name"] for repo in removed_repos]

        updated_installation = copy.deepcopy(existing_installation)

        curr_repos = set(existing_installation.get("repos"))
        for repo in removed_repo_names:
            curr_repos.discard(repo)
        updated_installation["repos"] = list(curr_repos)
        updated_installation["all_repos"] = False
        installation_store.create_or_update(updated_installation)
        return

    selected_all = data.get("repository_selection") == "all"

    if action == "added" and not selected_all:
        added_repos = data.get("repositories_added", [])
        added_repo_names = [repo["name"] for repo in added_repos]

        updated_installation = copy.deepcopy(existing_installation)

        curr_repos = set(existing_installation.get("repos"))
        for repo in added_repo_names:
            curr_repos.add(repo)

        updated_installation["repos"] = list(curr_repos)
        updated_installation["all_repos"] = False
        installation_store.create_or_update(updated_installation)
        return

    if action == "added" and selected_all:
        # clear set and set access_all to true
        updated_installation = copy.deepcopy(existing_installation)
        updated_installation["repos"] = []
        updated_installation["all_repos"] = True
        installation_store.create_or_update(updated_installation)
        return


def handle_installation(data, installation_store):
    github_account = (
        data.get("installation", {}).get("account", {}).get("login")
    )
    installation_id = data.get("installation", {}).get("id")
    action = data.get("action")

    installation = {
        "username": github_account,
        "installation_id": installation_id,
        "all_repos": False,
        "repos": [],
        "deleted": False,
    }

    if action == "deleted" or action == "suspended":
        # set installation to deleted=True
        installation["deleted"] = True
        installation_store.create_or_update(installation)
        return

    selected_all = (
        data.get("installation", {}).get("repository_selection") == "all"
    )
    if selected_all and (action == "created" or action == "unsuspended"):
        # create a new data object, where select = all
        installation["all_repos"] = True
        installation_store.create_or_update(installation)
        return

    if action == "created" or action == "unsuspended":
        added_repos = data.get("repositories", [])
        added_repo_names = [repo["name"] for repo in added_repos]
        # create a new record with repo names set to true
        installation["repos"] = added_repo_names
        installation_store.create_or_update(installation)
