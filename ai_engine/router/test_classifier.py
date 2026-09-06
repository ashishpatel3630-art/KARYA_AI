from router.classifier import TaskClassifier


classifier = TaskClassifier()

test_prompts = [
    "Explain predictive maintenance.",
    "Analyze this engineering drawing.",
    "Calculate the total maintenance cost.",
]


for prompt in test_prompts:
    policy = classifier.classify(prompt)

    print(f"\nPROMPT: {prompt}")
    print(f"TASK TYPE: {policy.task_type}")
    print(f"MODEL TYPE: {policy.model_type}")
    print(f"VISION REQUIRED: {policy.requires_vision}")
    print(f"TOOLS REQUIRED: {policy.requires_tools}")
