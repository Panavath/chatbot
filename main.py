from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings

from app.api.v1.router import router

from app.database.models.base_model import Base
from app.database import engine, SessionLocal

from app import logger

templates = Jinja2Templates(directory=Path(__file__).parent / "app" / "templates")

#lifespan event handler for a FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
    
    #create database if not exist 
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise e

    yield

    #close database connection
    try:
        engine.dispose()
        logger.info("Closing database connection")
    except Exception as e:
        logger.error(f"Error closing database connection: {str(e)}")

app = FastAPI(
    #set API Title
    title   = settings.API_NAME
    #Define API Version
    , version       = settings.API_VERSION
    #Specifies the OpenAPI schema URL
    , openapi_url   = f"{settings.API_V1_STR}/openapi.json"
    #Enables Swagger UI 
    , docs_url      = "/docs"
    #Enables ReDoc documentation 
    , redoc_url     = "/redoc"
    #Registers the lifespan handler for managing database setup and teardown.
    , lifespan      = lifespan
)
#serves static files (e.g., images, CSS, JavaScript) from the "app/assets" directory
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "app" / "assets"), name="static")

#Registers a router (router) to organize API endpoints.
app.include_router(router=router, prefix=settings.API_V1_STR)

# Chat UI route
@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request, 
            "app_name": settings.API_NAME
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        #script name, "app" is the FastAPI instance.
        "main:app"  
        #Binds the app to a specific hostname/IP                
        , host     = settings.HOST  
        # Runs on the given port
        , port     = settings.PORT  
        #Enables hot-reloading 
        , reload   = True 
        #Runs with 4 worker processes handling multiple requests        
        , workers  = 4     
        #Sets logging level to "info"        
        , log_level= "info"
    )