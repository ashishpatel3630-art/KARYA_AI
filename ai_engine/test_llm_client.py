from llm.client import OllamaClient
from llm.schemas import LLMMessage


client = OllamaClient()

print("Checking Ollama...")

if not client.health_check():
    print("❌ Ollama is not running.")
    raise SystemExit(1)

print("✅ Ollama is running.")

messages = [
    LLMMessage(
        role="user",
        content="Explain predictive maintenance in one simple paragraph.",
    )
]

print("\nGenerating response...\n")

response = client.generate(
    messages=messages,
    model="llama3.2",
    temperature=0.2,
)

print("KARYA AI RESPONSE:")
print(response)
