from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/double/{number}")
async def say_hello(number: int):
    return {"message": f"Result: {number * 2}"}
