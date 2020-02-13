FROM python:3.6

COPY . /app_docker

RUN python3 -m compileall -b app_docker

WORKDIR /app_docker

RUN find . -type f -name '*.py' -delete
ENV PATH=/root/.local/bin:$PATH

RUN pip install --default-timeout=100 --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

#RUN python -m nltk.downloader punkt \
#  && python -m nltk.downloader stopwords \
#  && python -m spacy download en


EXPOSE 8082
