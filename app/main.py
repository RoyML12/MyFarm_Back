import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers.auth_router import router as auth_router
from app.routers.conversation_router import router as conversation_router
from app.routers.favorite_router import router as favorite_router
from app.routers.message_router import router as message_router
from app.routers.product_router import router as product_router

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

app = FastAPI(
    title=os.getenv('APP_NAME', 'MyFarm API'),
    version='1.0.0',
    description='Backend FastAPI para MyFarm',
)

raw_origins = os.getenv('CORS_ALLOW_ORIGINS', 'http://localhost:5173')
allow_origins = [item.strip() for item in raw_origins.split(',') if item.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

UPLOADS_DIR = BASE_DIR / 'uploads'
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount('/uploads', StaticFiles(directory=str(UPLOADS_DIR)), name='uploads')


@app.on_event('startup')
def on_startup():
    init_db()


@app.get('/')
def root():
    return {
        'message': 'MyFarm FastAPI Backend activo',
        'docs': '/docs',
        'redoc': '/redoc',
        'health': '/health',
    }


@app.get('/health')
def health():
    return {'status': 'ok'}


app.include_router(auth_router, prefix='/api/v1')
app.include_router(product_router, prefix='/api/v1')
app.include_router(favorite_router, prefix='/api/v1')
app.include_router(conversation_router, prefix='/api/v1')
app.include_router(message_router, prefix='/api/v1')
