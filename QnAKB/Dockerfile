FROM python:3.5

WORKDIR /qnakb

COPY . /qnakb

RUN python -m compileall -b /qnakb
RUN find . -type f -name '*.py' -delete

RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

RUN python -m nltk.downloader punkt \
  && python -m nltk.downloader stopwords \
  && python -m nltk.downloader words

EXPOSE 8090

ENTRYPOINT [ "python" ]

CMD [ "router.pyc" ]

