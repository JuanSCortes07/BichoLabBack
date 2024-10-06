from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.routes import router as api_router
from app.auth import SECRET_KEY

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)  # Set your secret key

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=5000, reload=True)
