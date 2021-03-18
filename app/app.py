from fastapi import FastAPI, Request, Response
from starlette.middleware.cors import CORSMiddleware
from app.core.errors import catch_exceptions_middleware
from app.db.base import SessionLocal, engine
from app.db.models import Base
from app.core.config import host, port, debug, project_name, version
from app.api import router
import uvicorn

Base.metadata.create_all(bind=engine)


app = FastAPI(title=project_name, debug=debug, version=version)

# 普通异常全局捕获
app.middleware('http')(catch_exceptions_middleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response


app.include_router(router, prefix='/api')

if __name__ == '__main__':
    uvicorn.run(
        app="app:app",
        host=host,
        port=port,
        reload=debug,
        workers=4
    )
