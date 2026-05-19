import os
import anthropic

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

messages = []

def add_user_input(messages, user_input):
    messages.append({"role": "user", "content": user_input})
    
def chat(messages):
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=messages,
    )    
    return message.content[0].text

def add_assistant_message(messages, assistant_message):
    messages.append({"role": "user", "content": assistant_message})
    

# Use a 'while True' loop to run the chatbot forever
while True:
    # Get user input
    user_input = input("> ")
    print(">", user_input)
    
    # Add user input to the list of messages
    add_user_input (messages, user_input)
    
    # call Claude with the 'chat' function
    answer = chat(messages)
    
    # Add generated text to the list of messages
    add_assistant_message(messages, answer)
    # Print the generated text
    print("---")
    print(answer)
    print("---")
    
    