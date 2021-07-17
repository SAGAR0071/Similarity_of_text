From python:3
WORKDIR usr/src/app1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_md-2.0.0/en_core_web_md-2.0.0.tar.gz
RUN pip install -U spacy && python -m spacy download en
COPY . .
CMD ["python","app.py"]
