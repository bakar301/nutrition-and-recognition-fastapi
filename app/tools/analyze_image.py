from pydantic import BaseModel, Field
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from llama_index.core.program import MultiModalLLMCompletionProgram
from llama_index.core import SimpleDirectoryReader
from llama_index.core.output_parsers import PydanticOutputParser

from app.state import AnalyzerState

import os


class AnalysisResponse(BaseModel):
    """Response model for image analysis"""
    context: str = Field(description="Small explanation of the image")
    name: str | None = Field(default=None, description="'yes' name of the object or thing in this image or if in  image they are human then tell their gender,  otherwise if they cntain food anykind of food then tell their food name or they contain any kind of thing like electronice or something tell their name,otherwise None")
    food: str | None = Field(default=None, description="'yes' if the image contains food, otherwise None")
    color: str | None = Field(default=None, description="'yes' if the image contains color, otherwise None")
    summary: str | None = Field(default=None, description="Summary of the food image if applicable")
    calories: int | None = Field(default=None, description="Approximate calories in the food")
    recipe: dict | None = Field(default=None, description="Detailed recipe including ingredients and instructions")
    error: str | None = Field(default=None, description="Error message if not a food image")

def analyzeImage(state: AnalyzerState, image_path: str) -> AnalysisResponse:
    try:
        print(f"Path: {image_path}")
        reader = SimpleDirectoryReader(input_files=[image_path], filename_as_id=True)
        documents = reader.load_data()
        image_document = documents[0]
        prompt_template_str = """\
Analyze this image carefully and determine if it contains food or not.

If this is NOT a food image, respond with:
{   
    "name": "yes" if the image contains a name or if in  image they are human then tell their gender or if they are other thing then tell their name, otherwise None,
    "context": "small explanation of the image",
    "error": "respective error message",
    "summary": "summary of the image",
    "color":"color of the image",
}

If this IS a food image, respond with:
{
    "context": "small explanation of the image",
    "name": "yes" if the image contains a name or if in  image they are human then tell their gender, otherwise if they cntain food anykind of food then tell their food name or they contain any kind of thing like electronice or something tell their name,otherwise None,
    "food": "yes",
    "color":""color of the image",
    "summary": "summary of the image",
    "calories": approximate_calories_as_integer,
    "recipe": {
        "ingredients": ["ingredient1 with quantity", "ingredient2 with quantity"],
        "instructions": ["step1", "step2", "step3"],
        "cooking_time": "30",
        "difficulty_level": "easy/medium/hard"
    }
}

Keep the response concise and ensure all JSON fields are properly formatted.
"""
        mllm = OpenAIMultiModal(
            model='gpt-4o-mini',  # Updated to the correct model name
            api_key=os.environ.get("OPENAI_API_KEY"),
            max_new_tokens=4000  # Added max tokens to ensure complete response
        )
        
        llm_program = MultiModalLLMCompletionProgram.from_defaults(
            output_parser=PydanticOutputParser(AnalysisResponse),
            image_documents=[image_document],
            prompt_template_str=prompt_template_str,
            multi_modal_llm=mllm,
            verbose=True,
        )

        try:
            medical_data = llm_program()
            print("Raw LLM response:", medical_data)

            response = AnalysisResponse(
                context=getattr(medical_data, 'context', "No context provided"),
                name=getattr(medical_data, 'name', None),
                food=getattr(medical_data, 'food', None),
                color=getattr(medical_data, 'color', None),
                summary=getattr(medical_data, 'summary', None),
                calories=getattr(medical_data, 'calories', None),
                recipe=getattr(medical_data, 'recipe', None),
                error=getattr(medical_data, 'error', None)
            )
            print(f"Analysis response is: {response}")
            state.set_analysis_result(response.dict())  # Convert to dict before storing
            return response
            
        except Exception as e:
            print(f"Error processing LLM response: {e}")
            error_response = AnalysisResponse(
                context="Error processing image analysis",
                error=f"Failed to process image analysis: {str(e)}"
            )
            state.set_analysis_result(error_response.dict())  # Convert to dict before storing
            return error_response
            
    except Exception as e:
        print(f"Error analyzing image: {e}")
        error_response = AnalysisResponse(
            context="Failed to process image",
            error=f"Image processing error: {str(e)}"
        )
        state.set_analysis_result(error_response.dict())  # Convert to dict before storing
        return error_response