# PM-modeling-app/PM-modeling-app/README.md

# FastAPI Cloud Run Application

This project is a FastAPI application designed to generate maps based on date ranges using a prediction model. It is containerized for deployment on Google Cloud Run.

## Project Structure

```
PM-modeling-app
├── src
│   ├── main.py          # FastAPI application setup and API endpoints
│   ├── predict.py       # Prediction logic used by the FastAPI application
│   └── __init__.py      # Marks the directory as a Python package
├── Dockerfile            # Instructions for building the Docker image
├── .dockerignore         # Files and directories to ignore when building the Docker image
├── requirements.txt      # Python dependencies required for the application
├── .env                  # Environment variables for configuration
└── README.md             # Documentation for the project
```

## Prerequisites

- Python 3.7 or higher
- Docker
- Google Cloud SDK (for deployment)

## Installation

1. Clone the repository:

   ```
   git clone <repository-url>
   cd PM-modeling-app
   ```

2. Create a virtual environment and activate it (optional):

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

## Running the Application Locally

To run the FastAPI application locally, use the following command:

```
uvicorn src.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to access the API documentation.

## Building the Docker Image

To build the Docker image, run the following command in the project root directory:

```
docker build -t PM-modeling-app .
```

## Running the Docker Container

To run the Docker container locally, use:

```
docker run -p 8080:8080 PM-modeling-app
```

Visit `http://localhost:8080/docs` to access the API documentation.

## Deploying to Google Cloud Run

1. Authenticate with Google Cloud:

   ```
   gcloud auth login
   ```

2. Set your project ID:

   ```
   gcloud config set project <your-project-id>
   ```

3. Deploy the application:

   ```
   gcloud run deploy PM-modeling-app --image gcr.io/<your-project-id>/PM-modeling-app --platform managed
   ```

Follow the prompts to complete the deployment.

## License

This project is licensed under the MIT License. See the LICENSE file for details.