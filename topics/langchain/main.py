from langchain.agents import create_agent
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Contact(BaseModel):
    name: str
    email: str


agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    system_prompt="Format the given text as a contact card.",
    response_format=Contact,
)

if __name__ == '__main__':
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Hi my name is John and I live in New York City. and my email is: foo@email.com"}]},
    )

    print(result["structured_response"])
