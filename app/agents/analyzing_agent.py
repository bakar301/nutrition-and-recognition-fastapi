from contextlib import asynccontextmanager
from typing import AsyncGenerator
import os

from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool, ToolMetadata
from llama_index.llms.openai import OpenAI

from app.state import AnalyzerState

class AnalyzingAgent:
    def __init__(self, state: AnalyzerState):
        self.state = state
        self.tools = [
            
        ]
        self.context = """
        You are a helpful assistant that can help with the regeneration of a paragraph of a blog post.
        - You can use read_paragraph tool to read the paragraph, read_paragraph tool does not take any parameters.
        - You can use write_content tool to write the content of a blog post, You must always use this tool to write the content of a blog post. This stores the content in the state.
        1. Tone: this would tell us the tone of the blog
        2. Intensity: This is the intensity of the tone that user 
           user is asking from you, for example if tone is 'humourous' and intensity is strong 
           then you must make it FILLED WITH HUMOUR
        3. Length: This is the length of the blog post that user is asking for, you must ensure that the blog post is 
           within +-20 words of the user's request, if it is not met, you must rewrite the paragraph to meet the user's request.
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
                    "response": self.state.get_content()
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }