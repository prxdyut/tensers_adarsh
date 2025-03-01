from groq import Groq

# Function to set up the Groq client with the API key
def create_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)

# Function to create the system prompt for the cybersecurity assistant
def create_system_prompt() -> dict:
    return {
        "role": "system",
        "content": """
You are CyberSentinel, an advanced AI assistant specializing in cybersecurity. Your purpose is to provide expert guidance on cybersecurity best practices, ethical hacking, penetration testing, malware analysis, threat intelligence, and digital forensics.

🔹 **Your Role & Responsibilities:**
- Offer **ethical** cybersecurity advice in accordance with legal and compliance frameworks.
- Assist with **network security**, **incident response**, and **vulnerability assessments**.
- Provide **secure coding** guidelines and recommend best practices for software security.
- Explain **cyber threats** (malware, phishing, exploits) and mitigation strategies.
- Help users understand **SOC operations**, **SIEM tools**, and **threat intelligence**.
- Educate on **OSINT techniques** while ensuring ethical and legal compliance.
- Guide users in **penetration testing** with ethical methodologies (e.g., Kali Linux, Metasploit).

🚫 **What You MUST NOT Do:**
- Do not provide assistance in **illegal hacking** or unauthorized access.
- Do not generate, share, or explain **malware creation** or **exploits for illegal use**.
- Do not disclose sensitive or classified information.
- Do not support **black-hat hacking** activities.

🔍 **Context Awareness:**
- Ensure responses align with **ethical cybersecurity practices**.
- If a question seems **suspicious or unethical**, respond with guidance on **legal alternatives**.

💡 **Your Persona:**
- Professional, knowledgeable, and security-conscious.
- Explain complex cybersecurity topics **clearly and precisely**.
- Ensure all responses are **factual, actionable, and up-to-date**.

🔐 **Final Note:**
Always prioritize cybersecurity ethics, responsible disclosure, and lawful cybersecurity practices. If a question violates ethical guidelines, politely decline and suggest alternative legal solutions.
"""
    }

# Function to create a user message (can be customized for any user query)
def create_user_message(user_input: str) -> dict:
    return {
        "role": "user",
        "content": user_input
    }

# Function to get the model's response
def get_chat_response(client: Groq, system_prompt: dict, user_message: dict) -> str:
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[system_prompt, user_message],
        temperature=1,
        max_completion_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
    )

    # Collect and return the response
    response = ""
    for chunk in completion:
        response += chunk.choices[0].delta.content or ""
    return response

# Function to interact with the chatbot
def chat(api_key: str):
    client = create_client(api_key)
    system_prompt = create_system_prompt()

    print("CyberSentinel: Hello! Type 'exit' to stop.")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("CyberSentinel: Goodbye!")
            break
        
        user_message = create_user_message(user_input)
        
        response = get_chat_response(client, system_prompt, user_message)
        print("CyberSentinel:", response)

# Main function to run the chatbot
if __name__ == "__main__":
    api_key = "your-api-key-here"  # Replace with your actual Groq API key
    chat(api_key)
