from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.agents.analyzing_agent import AnalyzingAgent
import aiofiles
import os
import uuid
from pathlib import Path

from app.state import AnalyzerState

router = APIRouter()


async def get_regen_state():
    """Dependency to get AnalyzerState instance."""
    return AnalyzerState()


async def get_regen_agent(state: AnalyzerState = Depends(get_regen_state)):
    """Dependency to get RegenAgent instance with state."""
    return AnalyzingAgent(state)


@router.post("/upload-image/")
async def upload_image(
    image: UploadFile = File(...), agent: AnalyzingAgent = Depends(get_regen_agent)
):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    temp_file_path = None
    try:
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Generate unique filename with UUID
        file_extension = Path(image.filename).suffix
        unique_filename = f"{str(uuid.uuid4())}{file_extension}"
        temp_file_path = os.path.abspath(os.path.join(upload_dir, unique_filename))

        # Save the file
        async with aiofiles.open(temp_file_path, "wb") as out_file:
            content = await image.read()
            await out_file.write(content)

        agent.state.set_path(temp_file_path)
        
        response = await agent.execute(f"given your context, analyze the image, the absolute path of the image is {agent.state.get_path()}")

        print(f"image path: {temp_file_path}")
        response_data = {
            "original_filename": image.filename,
            "saved_filename": unique_filename,
            "response": response,
            "content_type": image.content_type,
        }

        # Clean up: Remove the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)

        return response_data

    except Exception as e:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=500, detail=str(e))
