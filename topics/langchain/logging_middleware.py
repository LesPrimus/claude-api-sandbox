"""Custom logging middleware for a LangChain v1 agent.

Run this and watch the hooks fire around each step of the agent loop:

    before_agent   -> once, when the run starts
      before_model -> before every model call
      after_model  -> after every model response
      wrap_tool_call -> around every tool call
    after_agent    -> once, when the run finishes

A `get_weather` tool is included so the loop runs more than one model call
(decide to call the tool -> read its result -> answer), which makes the
before_model / after_model pair fire twice.

    uv run python topics/langchain/logging_middleware.py
"""

from typing import Any, Callable

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, AgentState
from langchain.agents.middleware.types import ToolCallRequest
from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langgraph.runtime import Runtime

load_dotenv()


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"It's always sunny in {city}!"


class LoggingMiddleware(AgentMiddleware):
    """Prints a line every time the agent crosses a lifecycle boundary."""

    def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"[before_agent]  start  ({len(state['messages'])} message(s))")
        return None

    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"[before_model]  -> calling model ({len(state['messages'])} message(s))")
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        last = state["messages"][-1]
        if last.tool_calls:
            names = [tc["name"] for tc in last.tool_calls]
            print(f"[after_model]   <- model requested tool(s): {names}")
        else:
            print(f"[after_model]   <- model final text: {last.text!r}")
        return None

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage],
    ) -> ToolMessage:
        call = request.tool_call
        print(f"[wrap_tool_call] -> {call['name']}({call['args']})")
        result = handler(request)  # run the tool; skip this call to short-circuit
        print(f"[wrap_tool_call] <- {result.text!r}")
        return result

    def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"[after_agent]   done   ({len(state['messages'])} message(s) total)")
        return None


agent = create_agent(
    model="anthropic:claude-sonnet-4-6",
    tools=[get_weather],
    system_prompt="You are a helpful assistant. Use tools when needed.",
    middleware=[LoggingMiddleware()],
)


if __name__ == "__main__":
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "What's the weather in Rome?"}]}
    )
    print("\nFinal answer:", result["messages"][-1].text)