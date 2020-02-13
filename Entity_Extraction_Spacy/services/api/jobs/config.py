from celery import Celery
from services.api.util.config.cms_config import CMSConfig

#The below line is for getting broker from config.ini
#celery_app = Celery('services.api.jobs', broker= CMSConfig.celery_broker, include=['services.api.jobs.tasks'])
#The below line is for Docker
celery_app = Celery('services.api.jobs', broker='redis://ice-redis-msa:6379', include=['services.api.jobs.tasks'])
#The below line is for local (VM)
#celery_app = Celery('services.api.jobs', broker= 'redis://localhost:6379/0', include=['services.api.jobs.tasks'])
