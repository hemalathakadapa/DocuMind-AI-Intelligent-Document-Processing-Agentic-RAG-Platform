from src.rag_assistant import answer_question


questions = [
    "What is the company name of invoice INV-2026-0142?",
    "What is the subtotal of invoice INV-2026-0142?",
    "What is the total due of invoice INV-2026-0142?"
]


for question in questions:

    print("\nQuestion:", question)

    answer = answer_question(question)

    print("Answer:", answer)

    print("-" * 50)
