from fastapi import FastAPI

app = FastAPI(title="EY Agentic Drug Platform")

@app.get("/health")
async def health():
    return {"status": "ok"}
