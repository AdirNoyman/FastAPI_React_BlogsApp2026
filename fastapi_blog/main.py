from fastapi import FastAPI, HTTPException, Request, status, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os


app = FastAPI()

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


# # Custom 404 error handler
# @app.exception_handler(StarletteHTTPException)
# async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    # if exc.status_code == 404:
    #     return templates.TemplateResponse(
    #         request,
    #         "404.html",
    #         {"request": request},
    #         status_code=404
    #     )
#     # For other HTTP exceptions, re-raise them
#     raise exc


posts: list[dict] = [
    {
        "id": 1,
        "author": "CoreyMSchafer",
        "title": "Why I Love FastAPI",
        "content": "FastAPI has quickly become my favorite Python web framework. The automatic docs, type hints, and async support make it a joy to work with. If you haven't tried it yet, I highly recommend giving it a shot!",
        "date_posted": "December 31, 2025",
    },
    {
        "id": 2,
        "author": "GoodBoyBronx",
        "title": "Corey Schafer Has the Best YouTube Tutorials!",
        "content": "I just finished watching Corey's FastAPI series and I learned so much. His teaching style is clear, concise, and easy to follow. Highly recommend his channel to anyone looking to learn Python!",
        "date_posted": "December 30, 2025",
    },
    {
        "id": 3,
        "author": "PoppyTheCoder",
        "title": "Async/Await Finally Clicked",
        "content": "After struggling with async programming for months, it finally clicked for me. The key insight was understanding the event loop and how coroutines yield control. Now my APIs are lightning fast!",
        "date_posted": "December 27, 2025",
    },
]

# Templates routes


@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"request": request, "posts": posts, "title": "Home"})


@app.get("/posts/{post_id}", include_in_schema=False)
def post_details(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            title = post["title"][:30] + \
                "..." if len(post["title"]) > 30 else post["title"]
            return templates.TemplateResponse(request, "post.html", {"request": request, "post": post, "title": title})
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Post not found")


@app.get("/posts/{post_id}/edit", include_in_schema=False)
def post_edit_form(request: Request, post_id: int):
    post = next((p for p in posts if p.get("id") == post_id), None)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found")
    return templates.TemplateResponse(request, "edit_post.html", {"request": request, "post": post, "title": f"Edit {post['title']}"})


@app.post("/posts/{post_id}", include_in_schema=False)
async def update_post(request: Request, post_id: int):
    form_data = await request.form()
    post = next((p for p in posts if p.get("id") == post_id), None)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found")

    post["title"] = form_data.get("title")
    post["content"] = form_data.get("content")
    post["author"] = form_data.get("author")

    return RedirectResponse(url=f"/posts/{post_id}", status_code=303)


@app.delete("/posts/{post_id}")
async def delete_post(post_id: int):
    global posts
    post = next((p for p in posts if p.get("id") == post_id), None)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found")

    posts = [p for p in posts if p.get("id") != post_id]
    return {"success": True}


# API routes
@app.get("/api/posts")
def get_posts():
    return posts


@app.get("/api/posts/{post_id}")
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Post not found")


# Serve React app in production
frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")

if os.path.exists(frontend_dist):
    app.mount(
        "/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_react_app(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        index_path = os.path.join(frontend_dist, "index.html")
        return FileResponse(index_path)


## StarletteHTTPException Handler
@app.exception_handler(StarletteHTTPException)
def general_http_exception_handler(request: Request, exception: StarletteHTTPException):
    message = (
        exception.detail
        if exception.detail
        else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=exception.status_code,
            content={"detail": message},
        )
    if exception.status_code == 404:
        return templates.TemplateResponse(
            request,
            "404.html",
            {"request": request},
            status_code=404
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )


### RequestValidationError Handler
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )
    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )