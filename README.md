# fast-gh-app
boilerplate fastapi app + tools for github app installation 

The app receives events for `installation` and `installation_repositories` and handles by updating the repositories the github application has access to.

set up
in this example, we have a github app with permissions to read/write content and read/write pull requests. This is how you would create a github app like that in your github account.

we want to be able to update the repositories the github app installation has access to

it's installed on the organization/user level, so single app installation that gets updated

write to a local file

