from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from azure.storage.blob import BlobServiceClient
import os
import subprocess
from dotenv import load_dotenv
app = FastAPI()

@app.get("/")
async def root():
    return RedirectResponse(url="/static/index.html")

static_dir = os.path.abspath("static")
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)
load_dotenv("keys.env")

AZURE_CONN_STR = os.getenv("AZURE_CONN_STR")
CONTAINER_NAME = os.getenv("CONTAINER_NAME")



try:
    blob_service = BlobServiceClient.from_connection_string(AZURE_CONN_STR)
    print("Azur connection successful")
except Exception as e:
    print(f"Azur connection fail: {str(e)}")
    blob_service = None

@app.post("/analyze")
async def full_analysis(file: UploadFile = File(...)):
    try:
        blob_client = blob_service.get_blob_client(container=CONTAINER_NAME, blob=file.filename)
        file_content = await file.read()
        blob_client.upload_blob(file_content, overwrite=True)

        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(file_content)

        analysis_result = run_sonar_analysis()
        return {
            "status": "success",
            "sonar_results": analysis_result,
            "file_url": blob_client.url
        }
    except Exception as e:
        return {"error": str(e)}

def run_sonar_analysis():
    config_path = os.path.abspath("sonar-project.properties")
    command = f"sonar-scanner -Dproject.settings={config_path}"
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Analysis failed: {e.stderr}"