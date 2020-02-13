FROM python:3.6

COPY . /MSA_Entity_Extraction

RUN python3 -m compileall -b /MSA_Entity_Extraction

WORKDIR /MSA_Entity_Extraction

RUN find . -type f -name '*.py' -delete
ENV PATH=/root/.local/bin:$PATH

RUN pip install --upgrade pip

RUN pip install --default-timeout=100 --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

RUN python -m spacy download en_core_web_sm \
    && python -m nltk.downloader stopwords \
    && python -m nltk.downloader punkt \
    && python -m nltk.downloader wordnet

EXPOSE 8000

