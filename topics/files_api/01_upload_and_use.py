"""
Exercise: Files API
Upload a file once, reference it by file_id across multiple messages,
then delete it when done.
"""

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic()

# TODO: upload a file, send a message referencing the file_id,
#       then clean up with files.delete()


if __name__ == "__main__":
    pass
