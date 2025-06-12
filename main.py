from fastapi import FastAPI
from app.routers import user, post, auth, scraper
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "https://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],    
)

# routes
app.include_router(user.router)
app.include_router(post.router)
app.include_router(auth.router)
app.include_router(scraper.router)


@app.get("/")
def root():
    return {"message": f"Hi, this is testing!"}
