import os
# Assuming the correct package is `openai` or another library
# import groq  # replace with the correct library import
from groq import Groq
# Fetch the API key from environment variables
api_key = os.getenv("GROQ_API_KEY1")

# Assuming this is the correct way to instantiate the client
client = Groq(api_key=api_key)  # Replace `Groq` with the actual client class name

message_content = "What is the capital of France?"

# Create the chat completion request
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": message_content,
        }
    ],
    model="llama-3.1-8b-instant",  # Verify that this model name is correct and available
)

# Access the result
ans = chat_completion['choices'][0]['message']['content']

# Print the answer
print(ans)
    