from pydantic import BaseModel, Field
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from llama_index.core.program import MultiModalLLMCompletionProgram
from llama_index.core import SimpleDirectoryReader
from llama_index.core.output_parsers import PydanticOutputParser

import os


class AnalysisResponse(BaseModel):
    """Response model for image analysis"""
    context: str = Field(description="Small explanation of the image")
    food: str | None = Field(default=None, description="'yes' if the image contains food, otherwise None")
    summary: str | None = Field(default=None, description="Summary of the food image if applicable")
    calories: int | None = Field(default=None, description="Approximate calories in the food")
    recipe: dict | None = Field(default=None, description="Detailed recipe including ingredients and instructions")
    error: str | None = Field(default=None, description="Error message if not a food image")

def analyzeImage(image_path: str) -> AnalysisResponse:
    try:
        print(f"Path: {image_path}")
        reader = SimpleDirectoryReader(input_files=[image_path], filename_as_id=True)
        documents = reader.load_data()
        image_document = documents[0]
        prompt_template_str = """\
Analyze this image carefully and determine:

if this is a food or not, if not then the response should be

{
    "context": "small explanation of the image",
    "error": "NOT AN IMAGE"
}

if this is a food then response should be

{
    "context": "small explanation of the image",
    "food": "yes",
    "summary": "summary of the image",
    "calories": "approximate calories as integer",
    "recipe": {
        "ingredients": ["list of ingredients with quantities"],
        "instructions": ["step by step cooking instructions"],
        "cooking_time": "approximate cooking time in minutes",
        "difficulty_level": "easy/medium/hard"
    }
}
"""
        mllm = OpenAIMultiModal(
            model='gpt-4o-mini',
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        llm_program = MultiModalLLMCompletionProgram.from_defaults(
            output_parser=PydanticOutputParser(AnalysisResponse),
            image_documents=[image_document],
            prompt_template_str=prompt_template_str,
            multi_modal_llm=mllm,
            verbose=True,
        )

        medical_data = llm_program()
        print(medical_data)

        response = AnalysisResponse(
            context=medical_data.context,
            food=medical_data.food if hasattr(medical_data, 'food') else None,
            summary=medical_data.summary if hasattr(medical_data, 'summary') else None,
            calories=medical_data.calories if hasattr(medical_data, 'calories') else None,
            recipe=medical_data.recipe if hasattr(medical_data, 'recipe') else None,
            error=medical_data.error if hasattr(medical_data, 'error') else None
        )
        print(f"Analysis response is: {response}")
        return response
    except Exception as e:
        print(f"Error analyzing image: {e}")
        return AnalysisResponse(
            context="Failed to process image",
            error="NOT AN IMAGE"
        )