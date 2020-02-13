ICE_DL_Predict - Intelligent Computing Environment-Deep Learning-Predict API
---------------------------------------------------------
For installation do:

    1. >>> pip install -r requirements.txt
    2. Rename config.ini.orig to config.ini
    

Requires
    1. MongoDB
    2. Redis Server
    3. Celery - Distributed Task Queue
    4. Docker
    5. Minio
    6. Darknet

Starting Celery Tasks scheduler
___________________________________
celery -A jobs.tasks worker --loglevel=info
or
./jobs.sh

Minio Server
___________________________________

    Installing Minio
    ___________________________________
    docker pull minio/minio


    Creating our Minio server
    ___________________________________
    sudo docker run -p 9000:9000 --name ICEdlminio -e "MINIO_ACCESS_KEY=icedlminio" -e "MINIO_SECRET_KEY=icedlminio12345" -v /mnt/datadl:/datadl -v /mnt/config:/root/.minio minio/minio server /datadl


    Starting our Minio server
    ___________________________________
    sudo docker start ICEdlminio


    To store the models on Minio server using python
    ___________________________________
    requires: >>> pip3 install minio

    # Import Minio library.
    from minio import Minio
    from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                             BucketAlreadyExists)
    # Initialize minioClient
    minioClient = Minio('localhost:9000', access_key='icedlminio', secret_key='icedlminio12345', secure=False)
    #we will store each config files of the model in a different bucket using the model_name as bucket_name. Make a bucket with the make_bucket API call.
    model_name = "model-name"
    file_name = "file.data"
    file_path = "/tmp/file.data"
    try:
           minioClient.make_bucket(bucket_name = model_name)
    except BucketAlreadyOwnedByYou as err:
           pass
    except BucketAlreadyExists as err:
           pass
    except ResponseError as err:
           raise
        # Put an object 'file.data' with contents from 'file.data'.
    try:
        minioClient.fput_object(bucket_name = model_name, object_name = file_name , file_path = file_path)
    except ResponseError as err:
        print(err)


Starting ICE-DL-Predict  API
___________________________________

gunicorn -k gevent -t 120 --graceful-timeout 300 app.falcon_app:app -b :9001


Mongodb
___________________________________

    Files to Upload in the Minio store and the entry for MongoDb is given below:
    ___________________________________

{
    "_id" : ObjectId("5d318bded94e2efe0f9ff2b8"),
    "model_name" : "trade-info",
    "model_class" : "models.missed_sales_oppty.missedSalesPredict.MissedSalesPipeline",
    "model_config_documents" : {
        "init_checkpoint" : "model.ckpt-70.meta",
        "predict_tf_record" : "predict.tf_record",
        "dummy1" : "checkpoint",
        "dummy2" : "graph.pbtxt",
        "dummy3" : "model.ckpt-70.data-00000-of-00001",
        "dummy4" : "model.ckpt-70.index"
    },
    "updated_at" : ISODate("2019-08-13T15:44:18.965Z")
}