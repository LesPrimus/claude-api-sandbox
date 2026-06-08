"""
Claude API Python SDK — exploration sandbox.
Run individual exercises directly, e.g.:
    python topics/basic_messages/01_hello_world.py
"""

TOPICS = {
    "basic_messages": [
        "01_hello_world.py      — send a message, inspect the response",
        "02_system_prompt.py    — give Claude a persona via the system param",
        "03_multi_turn.py       — maintain context across multiple turns",
    ],
    "streaming": [
        "01_low_level.py        — stream=True, iterate raw SSE events",
        "02_stream_helper.py    — messages.stream() context manager + text_stream",
    ],
    "token_counting": [
        "01_count_before_request.py — estimate tokens before sending",
    ],
    "tool_use": [
        "01_beta_tool_decorator.py  — @beta_tool + automatic tool_runner loop",
        "02_manual_loop.py          — raw JSON schema tools, manual agentic loop",
    ],
    "thinking": [
        "01_adaptive.py         — adaptive thinking blocks + effort control",
    ],
    "structured_outputs": [
        "01_json_schema.py      — output_config.format with a JSON schema",
    ],
    "error_handling": [
        "01_error_types.py      — typed exceptions (BadRequestError, RateLimitError…)",
    ],
    "async_usage": [
        "01_async_basic.py      — AsyncAnthropic with asyncio",
        "02_concurrent.py       — parallel requests with asyncio.gather()",
    ],
    "client_config": [
        "01_retries_timeouts.py — max_retries, timeout, with_options()",
        "02_raw_response.py     — with_raw_response, headers, request-id",
    ],
    "batches": [
        "01_create_and_poll.py  — batch requests at 50% cost, poll for results",
    ],
    "files_api": [
        "01_upload_and_use.py   — upload a file, reference by file_id, delete",
    ],
}

if __name__ == "__main__":
    print("Claude API Python SDK — sandbox index\n")
    for topic, exercises in TOPICS.items():
        print(f"topics/{topic}/")
        for ex in exercises:
            print(f"    {ex}")
        print()
    print("Run any exercise directly: python topics/<topic>/<exercise>.py")
