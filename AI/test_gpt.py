
from openai import OpenAI

# 1) Put your Hugging Face access token here
HF_API_KEY = "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"

# 2) Create a client that talks to Hugging Face router, not OpenAI
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_API_KEY,
)

def main():
    # This is a small chat-style model that HF docs use as an example
    model_id = "katanemo/Arch-Router-1.5B:hf-inference"

    completion = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "user", "content": "What is the sqrre root of 16?"}
        ],
        max_tokens=128,
    )

    print("AI:", completion.choices[0].message.content)

if __name__ == "__main__":
    main()
