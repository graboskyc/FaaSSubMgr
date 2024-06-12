# FaaSSubMgr

## What is this

A bare-bones non-scalable implementation of MongoDB [ChangeStreams](https://www.mongodb.com/docs/manual/changeStreams/) integration with [Budibase](https://budibase.com/product/#automate) Automation webhook workflows, which essentially gives a trigger management system

## Set up
* Deploy a backing MongoDB cluster
* Make sure a user exists with permissions on the `faas.subscriptions` namespace
* Put the connection string for that cluster in an ENV variable called `SPECUIMDBCONNSTR` (as seen in the `sample.env`)
* Install any requirements in `requirements.txt`
* Run the python app via `main.py`

## Use
First, create a "New Stream":
* Name - any name you want
* Connection String - the connection string of the cluster to monitor the ChangeStream of
* Database Name - the database namespace to use in the cluster
* Collection Name - the collection inside the database to watch
* Pipeline - The ChangeStream change event filter pipeline
* Webhook - the URL to which to HTTP POST the full change event
* Enabled - checkbox to enable/disable the watch

Upon saving or any modification, the system will `watch` that collection using the `pipeline` provided and forward any `change_event` to the URL provided as a `POST`

It may be useful to test the webhook. Using the "Test Webhook" button will send a sample test to the Webhook as a `POST`

This may be more useful when using Budibase as a Budibase Webhook will provide a `Schema URL` which you can put in the webhook field, press "Test Webhook" and then Budibase will know the schema of the POST message. Then you chan change the Webhook value to that of the `Trigger URL` and Save to begin watching it.

## Screenshots

![](/screenshots/ss01.png)

![](/screenshots/ss02.png)

![](/screenshots/ss03.png)

![](/screenshots/ss04.png)