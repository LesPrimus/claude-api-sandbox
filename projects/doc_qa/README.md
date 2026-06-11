# Project 2 — Document Q&A

Upload a document **once**, then ask many questions about it without re-uploading
each time. This is what the Files API is for: you get back a `file_id` and
reference it in subsequent message requests via a `document` content block.

## Exercises

- Files API (`client.beta.files.upload`)
- Document content blocks (`{"type": "document", "source": {"type": "file", ...}}`)
- The `files-api-2025-04-14` beta header

## What to build

Create `projects/doc_qa/doc_qa.py` with two functions:

```python
def upload_document(client, path) -> str:
    """Upload a file and return its file_id."""

def ask(client, file_id: str, question: str, *, model: str = "claude-opus-4-8") -> str:
    """Ask a question about the uploaded document; return Claude's text answer."""
```

### Contract

`upload_document`:
- Call `client.beta.files.upload(...)` with the given path.
- Return the uploaded file's `.id`.

`ask`:
- Call `client.beta.messages.create(...)` with `betas=["files-api-2025-04-14"]`.
- The user message content must include:
  - a `document` block whose `source` is `{"type": "file", "file_id": <file_id>}`, and
  - a `text` block carrying the `question`.
- Return the text of the first `text` content block in the response.

> The tests assert that the `file_id` you were given actually appears in the
> document block sent to the API, and that the beta header is set.

## Run the tests

```bash
uv run pytest projects/doc_qa/ -v
```

## Stretch goals

- Enable citations (`"citations": {"enabled": True}` on the document block) and
  print the cited spans.
- Delete the file when done (`client.beta.files.delete(file_id)`).
- Loop over a list of questions reusing the same `file_id`.