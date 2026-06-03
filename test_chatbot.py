from rag.chatbot import ask_question


question = "What is the SLA of Orders Pipeline?"

answer = ask_question(question)

print("\nAnswer:\n")

print(answer)