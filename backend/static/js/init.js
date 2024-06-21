function init() {
    return {
        listOfStreams: [],
        editable: false,
        logs:false,
        checkboxes:false,
        selectedPipelineOptions: [],
        selectedStream: {"name":"", "connString":"mongodb+srv://...", "db":"", "col":"", "webhook":"", "pipeline":"[]", "enabled":false},
        webhookResponse : "",
        showPassword: false,

        async loadList() {
            console.log('Loading List');
            this.listOfStreams= await (await fetch('/api/listAll')).json();
            console.log(this.listOfStreams);
            this.editable = false;
            this.logs = false;
        },

        async loadLogs(stream) {
            console.log('Loading Logs');
            var _id = stream._id.$oid;
            this.selectedStream = await (await fetch('/api/find/'+_id)).json();
            this.selectedStream.modifiedAsDateString = new Date(this.selectedStream.modified.$date).toISOString();
            this.selectedStream.lastRanAsDateString = new Date(this.selectedStream.lastRan.$date).toISOString();
            this.logs = true;
            this.editable = false;
        },

        async generatePipeline() {
            console.log('Generating Pipeline');
            console.log(this.selectedPipelineOptions);
            if(this.selectedPipelineOptions.length == 1) {
                this.selectedStream.pipeline = JSON.stringify([
                    [{'$match': {'operationType': this.selectedPipelineOptions[0]}}]
                ]);
            } else if(this.selectedPipelineOptions.length > 0) {
                this.selectedStream.pipeline = JSON.stringify([
                    [{'$match': {'operationType': {'$in':this.selectedPipelineOptions }}}]
                ]);
            } else {
                this.selectedStream.pipeline = "[]";
            }
            this.checkboxes = false;
            this.selectedPipelineOptions = [];
        },

        async editStream(stream) {
            console.log('Editing Stream');                        
            var _id = stream._id.$oid;
            this.selectedStream = await (await fetch('/api/find/'+_id)).json();
            this.editable = true;
            this.logs = false;
            this.webhookResponse = "";
            this.selectedPipelineOptions = [];
        },

        async saveStream() {
            console.log('Saving Stream');
            if(this.checkboxes) {
                await this.generatePipeline();
            }

            if(
                (this.selectedStream.connString != 'mongodb+srv://...') 
                && (this.selectedStream.db.length > 0)
                && (this.selectedStream.col.length > 0)
                && (this.selectedStream.webhook.length > 0)
                && (this.selectedStream.name.length > 0)
                && (this.selectedStream.pipeline.length > 0)
            ) {
                var _id = this.selectedStream._id.$oid;
                delete this.selectedStream._id;
                delete this.selectedStream.modified;
                delete this.selectedStream.resumeToken;
                await fetch('/api/save/'+_id, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(this.selectedStream)
                });
                this.editable = false;
                this.selectedPipelineOptions = [];
                await this.loadList();
            } else {
                alert("You must provide a valid connection string, database name, collection name, webhook, name, and pipeline!");
            }
        },

        async newStream() {
            console.log('New Stream');
            editable = false;
            this.selectedStream = await (await fetch('/api/new')).json();
            this.editable = true;
            this.selectedPipelineOptions = [];
        },

        async deleteStream() {
            console.log('Loading List');
            if (confirm("Please confirm deleting '"+this.selectedStream.name+"'") == true) {
                var _id = this.selectedStream._id.$oid;
                await (await fetch('/api/delete/'+_id)).json();
                console.log(this.listOfStreams);
                await this.loadList();
                this.editable = false;
            }
        },

        async testWebhook() {
            console.log('Testing webhook');                        
            var _id = this.selectedStream._id.$oid;
            this.webhookResponse = await(await fetch('/api/webhooktest/'+_id, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.selectedStream)
            })).text();
        },

        async togglePassword() {
            this.showPassword = !this.showPassword;
        }
    }
}