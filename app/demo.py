import os
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent 

@tool("add", return_direct=True)
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

def main():
    llm = ChatOpenAI(
        model="qwen3-14b-claude-4.5-opus-high-reasoning-distill", 
        temperature=0.9,
        # base_url="https://api.openai.com/v1",
        base_url="http://127.0.0.1:1234/v1",
        api_key="empty",  # Set to empty string since the local server does not require an API key
        stream_usage=True
    )

    # llm.invoke("Hello, how are you?")

    messages = [
        (
            "system",
            "You are a helpful assistant that translates English to French. Translate the user sentence.",
        ),
        ("human", "I love programming."),
    ]

    ai_msg = llm.invoke(messages)

    print(ai_msg)

    agent_main = create_deep_agent(
        model=llm,
        tools=[]
        )

    result = agent_main.invoke({"messages": [("human", "I love programming.")]})
    print(result["messages"][-1].content)


    # Initialize the chat model with the specified provider and model name
    # chat_model = init_chat_model(
    #     provider=os.getenv("LLM_PROVIDER"),
    #     model=os.getenv("LLM_MODEL")
    # )

    # # Example conversation with the chat model
    # response = chat_model.chat("Hello, how are you?")
    # print(response)

if __name__ == "__main__":
    main()