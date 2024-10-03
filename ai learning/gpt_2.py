from notdiamond.llms.config import LLMConfig
from notdiamond import NotDiamond

client = NotDiamond()

llms = [
    LLMConfig(
        provider="openai",
        model="gpt-3.5-turbo",
        api_key="sk-ebe7ae03475db03a3760cda0a0f0dc76892ba57d8cffa9f5",
        temperature=0.5,
        max_tokens=256,
        input_price= 1,  # USD cost per million tokens
        output_price= 0.5,  # USD cost per million tokens
        latency= 0.86,  # Time to first token in seconds
    ),
    LLMConfig(
        provider="anthropic",
        model="claude-3-opus-20240229",
        api_key="sk-ebe7ae03475db03a3760cda0a0f0dc76892ba57d8cffa9f5",
        temperature=0.8,
        max_tokens=256,
        input_price= 3,  # USD cost per million tokens
        output_price= 2,  # USD cost per million tokens
        latency= 1.24,  # Time to first token in seconds
    ),
]

result, session_id, provider = client.chat.completions.create(
    messages=[ 
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Concisely explain merge sort."}  # Adjust as desired
    ],
    model=llms,
)

print("Not Diamond session ID: ", session_id)
print("LLM called: ", provider.model)
print("LLM output: ", result.content)