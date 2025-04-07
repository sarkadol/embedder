import os

from fastapi import Request
from fastapi.responses import JSONResponse

from embedbase import get_app
from embedbase.database.postgres_db import Postgres
from embedbase.embedding.openai import OpenAI
from embedbase.settings import get_settings_from_file
from custom_embedder import CustomEmbedder


settings = get_settings_from_file(os.path.join(".", "config.yaml"))

app = (
    get_app(settings)
   # .use_embedder(OpenAI(os.environ.get('OPENAI_APIKEY'), os.environ.get('OPENAI_ORGANISATION')))
    .use_embedder(CustomEmbedder(api_url="https://vllm.ai.e-infra.cz/v1/embeddings"))
    #.use_db(Postgres(conn_str=os.environ.get('POSTGRES_URL'), dimensions=os.environ.get('DIMENSIONS')))
    .use_db(Postgres(conn_str=os.environ.get('POSTGRES_URL'), dimensions=os.environ.get('DIMENSIONS')))
).run()

@app.exception_handler(Exception)
async def custom_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"message": "An error occurred in the server."},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        },
    )
