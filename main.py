from urllib import response
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import List

from ExcelAgent.api import message, checks

app_name = "Excel-Agent Server"

app = FastAPI(title=app_name)

origins = [
    # "http://localhost:5000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.middleware("http")(catch_global_exceptions)

app.include_router(message.router, tags=["Message"])
app.include_router(checks.router, tags=["Health Check"])

@app.get("/")
def root():
	return JSONResponse(content={"detail": app_name, "status": 200})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
