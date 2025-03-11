from fastapi import FastAPI
from app.routes import image_router

app = FastAPI(title="Nutrition Recognition API")

# Include the image routes
app.include_router(image_router, tags=["images"], prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Nutrition Recognition API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
