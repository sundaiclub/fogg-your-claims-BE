from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from ai21 import AI21Client

app = FastAPI()



@app.get("/", response_class=PlainTextResponse)
def read_root():
    return "Hello, this is a simple FastAPI endpoint returning plain text!"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
