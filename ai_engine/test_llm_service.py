from llm.schemas import LLMMessage, LLMRequest
from llm.service import LLMService


service = LLMService()

request = LLMRequest(
    messages=[
        LLMMessage(
            role="user",
            content="What is predictive maintenance? Explain in 3 simple sentences.",
        )
    ]
)

print("Sending request to KARYA LLM Service...\n")

response = service.chat(request)

print("MODEL:")
print(response.model)

print("\nRESPONSE:")
print(response.content)
