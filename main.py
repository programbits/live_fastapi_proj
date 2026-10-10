from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
import schemas
from auth import create_token, verify_credentials, verify_token
from database import Base, SessionLocal, engine


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Run after startup, when Render's persistent disk is mounted.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Blog API",
    description=(
        "A simple blog CRUD API. Reading blogs is public; creating, updating, "
        "and deleting blogs requires an access token."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", tags=["Health"])
def home():
    return {"message": "Blog API is running", "docs": "/docs", "health": "/health"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.post("/login", tags=["Authentication"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not verify_credentials(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_token({"sub": form_data.username}),
        "token_type": "bearer",
        "expires_in_minutes": 30,
    }


@app.post(
    "/blogs",
    response_model=schemas.BlogResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Blogs"],
)
def create_blog(
    blog: schemas.BlogCreate,
    db: Session = Depends(get_db),
    _user: dict = Depends(verify_token),
):
    new_blog = models.Blog(title=blog.title, content=blog.content)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.get("/blogs", response_model=schemas.BlogListResponse, tags=["Blogs"])
def get_blogs(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=5, ge=1, le=100),
    search: str = Query(default="", max_length=200),
    db: Session = Depends(get_db),
):
    query = db.query(models.Blog)
    if search.strip():
        query = query.filter(models.Blog.title.ilike(f"%{search.strip()}%"))

    total = query.count()
    blogs = query.order_by(models.Blog.id.desc()).offset((page - 1) * limit).limit(limit).all()
    return {"page": page, "limit": limit, "total": total, "data": blogs}


@app.get("/blogs/{blog_id}", response_model=schemas.BlogResponse, tags=["Blogs"])
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog


@app.put("/blogs/{blog_id}", response_model=schemas.BlogResponse, tags=["Blogs"])
def update_blog(
    blog_id: int,
    blog: schemas.BlogCreate,
    db: Session = Depends(get_db),
    _user: dict = Depends(verify_token),
):
    existing_blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if existing_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    existing_blog.title = blog.title
    existing_blog.content = blog.content
    db.commit()
    db.refresh(existing_blog)
    return existing_blog


@app.delete("/blogs/{blog_id}", tags=["Blogs"])
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    _user: dict = Depends(verify_token),
):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    db.delete(blog)
    db.commit()
    return {"message": "Blog deleted successfully", "id": blog_id}
