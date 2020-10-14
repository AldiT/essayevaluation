FROM python

COPY . /app

WORKDIR /app

RUN apt-get update

RUN apt-get -y install hunspell libhunspell-dev hunspell-en-gb hunspell-en-us netcat-openbsd

RUN pip install -r requirements.txt

RUN python -m spacy download en_core_web_sm

RUN python -m spacy download en_core_web_lg

