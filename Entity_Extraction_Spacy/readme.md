1. Install requirements for the service

pip install -r requirements.txt

2. Download spacy model if not already done
python -m spacy download en_core_web_sm

3. Start the application using the below commands: 

celery worker --app=services.api.jobs.config --pool=gevent --concurrency=20 --loglevel=INFO
gunicorn services.api.parse.app:api --bind ip:port

4. Extract entities using the endpoint '/extract_msa_entities' and below request json

Request JSON:
{"content": "Master Services Agreement",
"callBack": {
"category": "MSA",
"fileName": "D09988.txt",
"uniqueId": "D09988:1234",
"organizationId": "6",
"senseType": "ML",
"workflowName": "WorkflowA",
"sessionId": "session-id",
"transactionId": "tran-id"},
"file_store":"hsghd",
"queueDetails": {
    "host": "clones-dev.southindia.cloudapp.azure.com",
    "port": "5672",
    "userName": "admin",
    "password": "admin",
    "queueName": "v4.inbound.dev"
  }}

Response JSON: 
{"organizationId": "6", 
"senseType": "ML", 
"workflowName": "WorkflowA", 
"sessionId": "session-id", 
"transactionId": "tran-id",
"requestJson": { 
    "error": "false", 
    "errorMessage": "", 
    "firstParty": "Wolters Kluwer United States Inc", 
    "secondParty": "Impelsys Inc.", 
    "effectiveDate": "07/02/2012",
    "rebate_table_flag" : False,
    "payment": "",
    "warranties":"",
    "termination": "",
    "indemnification":"",	
    "callBack": {
        "category": "MSA", 
        "fileName": "D09988.txt", 
        "uniqueId": "D09988:1234"
}}}
