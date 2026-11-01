# RuleWatch on Render (free plan). The app is packed in app.zip; this unpacks and runs it.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 FASTEMBED_CACHE=/app/models \
    HF_HUB_DISABLE_SYMLINKS_WARNING=1 EMBED_THREADS=1 OMP_NUM_THREADS=1 MALLOC_ARENA_MAX=2 PORT=10000
WORKDIR /app

COPY app.zip /tmp/app.zip
RUN python -m zipfile -e /tmp/app.zip /app && rm /tmp/app.zip
RUN pip install --upgrade pip && pip install -r requirements.txt

# Download the multilingual search model once, at build time
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2', cache_dir='/app/models')"
RUN mkdir -p data/pdfs

EXPOSE 10000
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT} --workers 1"]
