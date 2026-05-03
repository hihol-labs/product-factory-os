from fastapi import FastAPI

app = FastAPI(title="PFO SaaS")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

