# Embedder
I am currently modifying and testing this embedder, so it gains better and more accurate results. In the end, it should enhance the chatbot on [e-Infra documentation](https://docs.cerit.io/en/docs/news).

Related project [questions_generator_GPT](https://github.com/sarkadol/questions_generator_GPT) - tool for generating questions using GPT models and testing this embedder.

# How to start
## Build docker

```shell
cd docker
docker build -t cerit.io/cerit/embedbase:v0.6 .
docker push cerit.io/cerit/embedbase:v0.6
```

## Run embed base

* Deploy all manifests, if needed, provide OPENAI API KEY secret, set `OPENAI_URL` and `OPENAI_MODEL` envs.
* Postgress database is needed, manifests assume cloudnativepg operator is deployed

## Insert Documents

Run `utils/embed.py` to embed documents into db. Export env `EMBEDURL` to point to embedbase URL. It expect fumadocs format of documents.

## Test embedding

```shell
curl  -X POST https://embedbase.dyn.cloud.e-infra.cz/v1/muni-documentation/search -H "Content-Type: application/json" -d '{"query": "Kdy byl schválen nový Studijní a zkušební řád Masarykovy univerzity Akademickým senátem MU?", "top_k": "5"}'
```

Replace the POST URL with your URL.
