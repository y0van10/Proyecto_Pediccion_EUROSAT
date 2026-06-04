import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
import logging
from services.model_service import ModelService
from utils.logger import setup_logger

# Configuration
PROJECT_NAME = "EuroSAT Satellite Classifier"
API_V1_STR = "/api/v1"

# CORS — read allowed origins from env; default allows all for local dev.
# In production set e.g. CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
_raw_origins = os.getenv("CORS_ORIGINS", "*")
CORS_ORIGINS = ["*"] if _raw_origins == "*" else [o.strip() for o in _raw_origins.split(",")]

# Initialize Logger
logger = setup_logger()

app = FastAPI(title=PROJECT_NAME, openapi_url=f"{API_V1_STR}/openapi.json")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Model Service
model_service = ModelService()

@app.get("/")
async def root():
    return {"message": "EuroSAT Satellite Classification API is running", "status": "healthy"}

@app.get(f"{API_V1_STR}/health")
async def health():
    """Health check endpoint for monitoring / load balancers."""
    return {
        "status": "healthy",
        "model_loaded": (model_service.satellite_model is not None) or (model_service.domain_model is not None),
    }

@app.post(f"{API_V1_STR}/predict")
async def predict(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    try:
        start_time = time.time()
        
        # Read image content
        image_bytes = await file.read()
        
        # Perform prediction
        prediction = model_service.predict(image_bytes)
        
        inference_time = round(time.time() - start_time, 4)
        
        logger.info(f"Prediction successful for {file.filename} - Class: {prediction['class']} (Domain: {prediction.get('domain')})")
        
        return {
            "domain": prediction.get("domain", "satellite"),
            "class": prediction["class"],
            "probability": prediction["probability"],
            "inference_time": inference_time,
            "filename": file.filename,
            "top_5": prediction.get("top_5", [])
        }
    except Exception as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
