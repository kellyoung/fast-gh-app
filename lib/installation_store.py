import json


class InstallationStore:
    """
    A temporary in-memory data store/functionality for proof of concept.
    Store the data related to a Github app installation
    """

    def __init__(self, data={}, file_location="./data_store"):
        self.store = data
        self.file_location = file_location

    def get(self, username: str):
        active_installation = self.store.get(username, {}).get("active")
        if not active_installation:
            return
        return active_installation

    def create_or_update(self, installation_object):
        username = installation_object.get("username")
        # not handling the case of if there is an active installation
        users_installations = self.store.get(username)
        if not users_installations:
            self.store[username] = {
                "active": installation_object,
                "deleted": [],
            }
        is_deleted = installation_object.get("deleted")
        # if deleted push the installation object to deleted
        if is_deleted:
            users_installations.get("deleted").append(installation_object)
            users_installations["active"] = None
            self._save_to_file()
            return

        self.store[username]["active"] = installation_object
        self._save_to_file()
        return installation_object

    def _save_to_file(self):
        try:
            with open(self.file_location, "w") as file_writer:
                file_writer.write(json.dumps(self.store, indent=4))
                print("Data written to file successfully.")
        except Exception as e:
            print(f"Error writing to file: {e}")
