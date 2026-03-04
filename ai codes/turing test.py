import random

# Simple AI responses
AI_RESPONSES = [
    "That's interesting. Can you tell me more?",
    "Why do you think that?",
    "I agree with you.",
    "That sounds exciting!",
    "I'm not sure, but I think it's possible."
]

def ai_response():
    return random.choice(AI_RESPONSES)

def human_response():
    return input("Human, type your response: ")

def turing_test():
    print("=== Turing Test Simulation ===")
    question = input("Judge, enter your question: ")

    print("\n--- Responses ---")
    
    # Randomly assign order
    if random.choice([True, False]):
        print("Response A:", ai_response())
        print("Response B:", human_response())
        ai_position = "A"
    else:
        print("Response A:", human_response())
        print("Response B:", ai_response())
        ai_position = "B"

    guess = input("\nJudge, which response is AI? (A/B): ")

    if guess.upper() == ai_position:
        print("Correct! You identified the AI.")
    else:
        print("Wrong! AI fooled you.")

turing_test()
