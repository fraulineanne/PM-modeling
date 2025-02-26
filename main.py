from fastapi import FastAPI
from pydantic import BaseModel
from predict import predict
import datetime

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
class DateRange(BaseModel):
    start_date: str  # Format: 'YYYY-MM-DD'
    end_date: str    # Format: 'YYYY-MM-DD'

def predict_for_input_date(start_date, end_date):
    # Convert to datetime
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

    return predict(
        project=PROJECT_NAME, 
        bucket_name=BUCKET_NAME,
        from_date=start_date, to_date=end_date, 
        service_account=SERVICE_ACCOUNT, 
        service_file=SERVICE_FILE, 
        saved_model=PM25_MODEL
    )
    
@app.post("/generate-map/")
async def generate_map(date_range: DateRange):
    try:
        image_url = predict_for_input_date(date_range.start_date, date_range.end_date)
        return {"message": "Map generated successfully", "image_url": image_url}
    except Exception as e:
        return {"error": str(e)}

# Run the API server with: uvicorn main:app --reload
