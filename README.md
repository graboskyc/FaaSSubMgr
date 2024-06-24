# FaaSSubMgr

## What is this

A bare-bones non-scalable implementation of MongoDB [ChangeStreams](https://www.mongodb.com/docs/manual/changeStreams/) integration with [Budibase](https://budibase.com/product/#automate) Automation webhook workflows, which essentially gives a trigger management system. Although the examples use Budibase, it will work with any webhook that accepts an arbitrary HTTP POST.

## Technology Used
* [FastAPI](https://fastapi.tiangolo.com/) - static webserver and APIs
* [PicoCSS](https://picocss.com/) - Styling
* [AlpineJS](https://alpinejs.dev/) - interactivity
* [Material Icons](https://fonts.google.com/icons) - Icons
* [MongoDB](https://www.mongodb.com/) - Database

## Set up
### Variables for all methods
* Deploy a backing MongoDB cluster
* Make sure a user exists with permissions on the `faas.subscriptions` and `faas.__keyvault` namespaces
* Put the connection string for that cluster in the .env file in the variable called `SPECUIMDBCONNSTR` (as seen in the `sample.env` which can be copied and renamed to just `.env`)
* Generate an encryption key with the command below and put in `MASTERENCKEYASBASE64` value in the `.env` file created in the last step. Only include the value from python within the single quotes (omit the starting and trailing single quote and the starting b)
```
>>> import os
>>> import base64
>>> base64.b64encode(os.urandom(96))
```
* DO NOT LOSE THE ABOVE as without it you will not be able to regain your data as it is encrypted
* Both variables should be in double quotes within the `.env` file

### Via a venv
* Create a venv:
```
$ cd backend
$ python -m venv venv
```
* Edit `venv/bin/activate` to put a new line at the end with contents `export SPECUIMDBCONNSTR=$1 MASTERENCKEYASBASE64=$2`
* Run `./activate.sh` script

### Via docker
* Run `./build.sh`

## Use
First, create a "New Stream":
* Name - any name you want
* Connection String - the connection string of the cluster to monitor the ChangeStream of. This is encrypted with pymongo and MongoDB's [Queryable Encryption](https://www.mongodb.com/docs/manual/core/queryable-encryption/)
* Database Name - the database namespace to use in the cluster
* Collection Name - the collection inside the database to watch
* Pipeline - The ChangeStream change event filter pipeline
* Webhook - the URL to which to HTTP POST the full change event
* Additional metadata context - any key/value you want to send in the payload. Will be in the `secretsMetadata` field. The value is stored encrypted in the database
* Enabled - checkbox to enable/disable the watch

Upon saving or any modification, the system will `watch` that collection using the `pipeline` provided and forward any `change_event` to the URL provided as a `POST`

It may be useful to test the webhook. Using the "Test Webhook" button will send a sample test to the Webhook as a `POST`

This may be more useful when using Budibase as a Budibase Webhook will provide a `Schema URL` which you can put in the webhook field, press "Test Webhook" and then Budibase will know the schema of the POST message. Then you chan change the Webhook value to that of the `Trigger URL` and Save to begin watching it.

## Screenshots

![](/screenshots/ss01.png)

![](/screenshots/ss02.png)

![](/screenshots/ss02_alt.png)

![](/screenshots/ss03.png)

![](/screenshots/ss04.png)

![](/screenshots/miniscaletest.gif)

![](/screenshots/ss05.png)

![](/screenshots/ss07.png)

![](/screenshots/ss06.png)