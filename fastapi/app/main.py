from fastapi import FastAPI, HTTPException, Request, File, UploadFile
from starlette.responses import Response, FileResponse
from PIL import Image

import io

from app.db.models import UserAnswer
from app.api import api

app = FastAPI()

@app.get("/image")
async def main():
    return FileResponse("your_image.jpeg")

@app.post("/putObject")
async def put_object(request: Request, application: str, file: UploadFile = File(...)) -> str:
    request_object_content = await file.read()
    img = Image.open(io.BytesIO(request_object_content))

@app.get("/")
def root():
    return {"message": "Fast API in Python"}


@app.get("/user")
def read_user():
    return api.read_user()


@app.get("/question/{position}", status_code=200)
def read_questions(position: int, response: Response):
    question = api.read_questions(position)

    if not question:
        raise HTTPException(status_code=400, detail="Error")

    return question


@app.get("/alternatives/{question_id}")
def read_alternatives(question_id: int):
    return api.read_alternatives(question_id)


@app.post("/answer", status_code=201)
def create_answer(payload: UserAnswer):
    payload = payload.dict()

    return api.create_answer(payload)


@app.get("/result/{user_id}")
def read_result(user_id: int):
    return api.read_result(user_id)

# return a jpeg image thats at fastapi/data/sama_bb.jpeg
@app.get("/image_sama/")
def image_sama():
    return FileResponse("data/sama_bb.jpeg", media_type='image/jpeg')
