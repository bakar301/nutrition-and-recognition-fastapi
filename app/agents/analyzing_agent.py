from contextlib import asynccontextmanager
from typing import AsyncGenerator
import os

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool, ToolMetadata
from llama_index.llms.openai import OpenAI

from app.tools.analyze_image import analyzeImage

from app.state import AnalyzerState

from app.schemas.analyzing_agent_schema import AnalyzingAgentSchema

class AnalyzingAgent:
    def __init__(self, state: AnalyzerState):
        self.state = state
        self.tools = [
            FunctionTool(
                fn=lambda *args, **kwargs: analyzeImage(self.state, *args, **kwargs),
                metadata=ToolMetadata(
                    name="analyze_image",
                    description="Analyze the image and return the food details",
                    fn_schema=AnalyzingAgentSchema
                ),
            )
        ]
        self.context = """
        You are a nutritionist and you have been asked to analyze the image and determine if it is a food or not.
        You must use the the tool `analyze_image` to analyze the image and provide the details.
        """

    @asynccontextmanager
    async def get_llm(self) -> AsyncGenerator:
        """Create a new LLM instance for each request."""
        llm = OpenAI(
            model='gpt-4o-mini',
            api_key=os.getenv("OPENAI_API_KEY")
        )
        try:
            yield llm
        finally:
            pass

    async def execute(self, task: str):
        """Async execution of blog generation."""
        try:
            async with self.get_llm() as llm:
                agent = ReActAgent.from_tools(
                    tools=self.tools,
                    llm=llm,
                    verbose=True,
                    max_iterations=1000,
                    context=self.context,
                )

                await agent.achat(task)
                
                return {
                    "status": "success",
                    "response": self.state.get_analysis_result()
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }