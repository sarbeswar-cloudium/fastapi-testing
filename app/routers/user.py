from fastapi import APIRouter, Depends, status, HTTPException, File, Form, UploadFile
from app import schemas, models, utils, oauth2
from app.database import get_db
from sqlalchemy.orm import Session
from datetime import datetime
from app.email import fastmail
from fastapi_mail import MessageSchema, MessageType
import random
import shutil
import os

router = APIRouter(
    prefix="/users",
    tags=['User']
)


@router.post("/", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):
    # hashed password
    user.password = utils.get_password_hash(user.password)
    new_user = models.User(
        name = user.name,
        email = user.email,
        address = user.address,
        password = user.password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/{id}", response_model=schemas.UserOut)
def show_user(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found!")
    
    return user

@router.post("/photo")
async def profile_photo(file: UploadFile = File(...)):
    file_types = ['image/jpeg', 'image/jpg', 'image/png']
    contents = await file.read()
    filename = file.filename
    extension = os.path.splitext(filename)[1]
    content_type = file.content_type
    # size = len(contents)
    size = file.size

    if content_type not in file_types:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"{content_type} are not allowed!")
    
    if size > 2000000:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"Size is too large, limit 2MB!")
    
    new_filename =  f"{datetime.now().strftime("%Y%m%d%H%M%S")}{random.randint(1, 1000000)}{extension}"

    dir_path = "uploads"

    if not os.path.exists(dir_path):
       os.mkdir(dir_path)

    with open(f"uploads/{new_filename}", "wb") as buffer:
        await file.seek(0)
        shutil.copyfileobj(file.file, buffer)
        # buffer.write(contents)

    return {"message": "Profile photo uploaded!"}


@router.post("/email")
async def send_email():
    list = ["sarbeswar.dev@gmail.com"]

    html = """
    <p>Thanks for using Fastapi-mail</p>
    """


    message = MessageSchema(
        subject="Fastapi-Mail module testing going correct",
        recipients=list,
        body=html,
        subtype=MessageType.html)
    
    await fastmail.send_message(message)
    # return JSONResponse(status_code=200, content={"message": "email has been sent"})

    return {"message": "Email sent!"}