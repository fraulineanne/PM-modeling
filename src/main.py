from pydantic import BaseModel
from fastapi import FastAPI
from predict import predict
from dotenv import load_dotenv
import os

load_dotenv(override=True)
SERVICE_ACCOUNT = os.environ["SERVICE_ACCOUNT"]
SERVICE_FILE = os.environ["SERVICE_FILE"]
PROJECT_NAME = os.environ["PROJECT_NAME"]
BUCKET_NAME = os.environ["BUCKET_NAME"]
PM25_MODEL = os.environ["PM25_MODEL"] 

app = FastAPI()

# Define request model
# class DateRange(BaseModel):
#     start_date: str  # Format: 'YYYY-MM-DD'
#     end_date: str    # Format: 'YYYY-MM-DD'

def predict_for_input_date(start_date, end_date):

    return predict(
        project=PROJECT_NAME, 
        bucket_name=BUCKET_NAME,
        from_date=start_date, to_date=end_date, 
        service_account=SERVICE_ACCOUNT, 
        service_file=SERVICE_FILE, 
        saved_model=PM25_MODEL
    )

@app.get("/")
async def root():
    return {"message": "Welcome to the PM25 Prediction API!"}

@app.get("/generate-map/")
async def generate_map(start_date: str, end_date: str):
    try:
        image_url = predict_for_input_date(start_date, end_date)
        return {"message": "Map generated successfully", "image_url": image_url}
    except Exception as e:
        return {"error": str(e)}
    except ValueError as e:
        return {"error": str(e)}


# Run the API server with: uvicorn main:app --reload
