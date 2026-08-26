from app.services.llm.openrouter_provider import OpenRouterProvider
from app.schemas.master_decision import MasterDecision


def main():

    provider = OpenRouterProvider()

    result = provider.generate(
        system_prompt=(
            "You are a software factory master agent. "
            "Return a valid decision."
        ),
        input_context={
            "project": {
                "id": 3,
                "name": "AI Software Factory Demo"
            },
            "tasks": [
                {
                    "id": 12,
                    "status": "pending",
                    "required_role": "architect"
                }
            ],
            "agents": [
                {
                    "id": 2,
                    "role": "architect",
                    "status": "idle"
                }
            ]
        },
        response_model=MasterDecision
    )

    print("Model:", result["model"])
    print("Raw response:")
    print(result["raw_response"])
    print("Input tokens:", result["input_tokens"])
    print("Output tokens:", result["output_tokens"])


if __name__ == "__main__":
    main()