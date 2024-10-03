from notdiamond import NotDiamond

client = NotDiamond()

result, _, provider = client.chat.completions.create(
    messages=[{"role": "user", "content": message}],
    model=[
        'openai/gpt-4o',
        'openai/gpt-4o-mini',
        'anthropic/claude-3-5-sonnet-20240620',
        'perplexity/llama-3.1-sonar-large-128k-online'
    ],
    tradeoff='cost'
)

print("LLM called: ", provider.model)
print("LLM output: ", result.content)