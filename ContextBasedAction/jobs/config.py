from __future__ import absolute_import, unicode_literals
from util.config.idl_config import idl_config
from jobs.imports import PackageImporter
from celery import Celery
app = Celery('jobs', broker=idl_config.celery_broker, backend=idl_config.celery_backend, include=['jobs.tasks'])
app.conf.update(
    result_expires = 60*60*24
)

if __name__=='__main__':
    PackageImporter()
    app.start()