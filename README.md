# fast-gh-app

An example of a FastAPI application to interface with Github applications.

Github sends webhook events for events related to installation/uninstallation of a Github application on an account/organization and on a repository. This application listens to those events `installation` and `installation_repositories` events and writes to a simple local datastore to keep track of data pertaining to the installation.

Github also allows you to "authenticate" as the Github application a Github user has installed. To do this, you must generate an `installation_access_token` using the secret of your Github app as well as knowing the `installation_id` of the installation you want to authenticate as. There's also an endpoint for returning an `installation_access_token` (valid for 1 hour from generation) that can be used to authenticate and be given the same permissions as the Github app.

The bulk of the example functionality is in `main.py`. However, `main-secrets.py` is provided as an example for how to process webhook events if you provided a `webhook secret` to your Github app setup.

## Endpoints
- **POST /github-webhook**: receives Github webhook events and saves installation data into a local data store
- **GET /{username>}/active-installation**: returns an `active installation` for the user specified. Returns `None` if no active installation exists.
- **POST /{username}/installation-token**: creates a Github installation access token that can be used to make requests in Github on behalf of the installation (therefore giving you the same permissions as what the Github application has)


## Local Development
### Setup Smee

Visit [https://smee.io/](https://smee.io/) and "Start a new channel". Copy the "Webhook proxy URL" which will be used when setting up the Github app. 

### Setup Github App

If you don't already have a Github App, create a new one. Set "Webhook" to "active" and enter the "webhook proxy URL" from `smee.io` as the "Webhook URL". Once changes are saved, Github will send webhook events to the webhook URL.

If you're setting up a webhook secret, make sure to remember the secret for the later steps.

If you want to test out creating an `installation_token`, then you'll also need to generate a private key in the app's settings and store the file locally.

### Local Server Setup

Clone this repo locally. Then, install packages.

```
pip install requirements.txt
```

Set up environmental variables:
```
export GITHUB_APP_ID=<github application ID found in settings>
export PRIVATE_KEY_PATH=<file path to where the private key is stored locally>
```

If you're using a webhook secret:
```
export WEBHOOK_SECRET=<webhook secret from github app>
```

In another terminal window, we need to run `smee` to forward the webhook events to our `github-webhook` endpoint.

```
npm install
npx smee -u <webhook proxy url> -t http://127.0.0.1:8000/github-webhook

```

Run the server

```
python main.py
# python main-secrets.py if you want to try with secrets
```

