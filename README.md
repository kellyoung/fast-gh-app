# fast-gh-app

An example of a FastAPI application to interface with Github applications.

Github sends webhook events for events related to installation/uninstallation of a Github application on an account/organization and on a repository. This application listens to those events `installation` and `installation_repositories` events and writes to a simple local datastore to keep track of data pertaining to the installation.

Github also allows you to "authenticate" as the Github application a Github user has installed. To do this, you must generate an `installation_access_token` using the secret of your Github app as well as knowing the `installation_id` of the installation you want to authenticate as. There's also an endpoint for returning an `installation_access_token` (valid for 1 hour from generation) that can be used to authenticate and be given the same permissions as the Github app.

The bulk of the example functionality is in `main.py`. However, `main-secrets.py` is provided as an example for how to process webhook events if you provided a `webhook secret` to your Github app setup.

## Local Development

### Setup Github App

### Setup Smee

### Local Server Setup

