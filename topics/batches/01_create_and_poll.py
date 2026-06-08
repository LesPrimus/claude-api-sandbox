"""
Exercise: Message Batches
Create a batch of requests, poll until processing_status == 'ended',
then iterate results. Batches run at 50% cost vs standard API.
"""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# TODO: create a batch with multiple requests, poll for completion,
#       iterate results and print each custom_id + response text


if __name__ == "__main__":
    pass
