from fastapi import APIRouter

router = APIRouter(
    prefix="/posts",
    tags=["Post"]
)


@router.get("/")
def create_post():
    return {"message": "Post created"}