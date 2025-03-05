from fastapi import FastAPI
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
from llama_index.core.llms import ChatMessage, MessageRole
import uvicorn

app = FastAPI()
llm = OpenAIMultiModal(
    api_base="https://api.groq.com/openai/v1",
    api_key="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",
)

@app.get("/")
def read_root():
    messages = [
        ChatMessage(role=MessageRole.ASSISTANT, content="What is your query?"),
        ChatMessage(role=MessageRole.USER, content="who are you?")
    ]
    
    response = llm.chat(messages=messages)
    print(response)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
