from fastapi import FastAPI


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Welcome to my app"}


@app.get("/custom")
def read_custom_message():
    return {"message": "This is a custom message!"}
