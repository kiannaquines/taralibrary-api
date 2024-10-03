from fastapi import FastAPI
from view import router as views_router

app = FastAPI()
app.include_router(views_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)