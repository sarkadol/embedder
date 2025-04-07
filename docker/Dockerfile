FROM python:3.10-slim
COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y git gcc wget curl && apt-get clean && pip install openai && \
    pip install -r requirements.txt && pip install --upgrade --no-deps openai && rm requirements.txt && rm -rf ~/.cache
COPY main.py main.py
COPY custom_embedder.py custom_embedder.py
COPY app.py /usr/local/lib/python3.10/site-packages/embedbase/app.py
COPY postgres_db.py /usr/local/lib/python3.10/site-packages/embedbase/database/postgres_db.py
COPY openai.py /usr/local/lib/python3.10/site-packages/embedbase/embedding/openai.py
COPY docker-entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["embedbase"]
