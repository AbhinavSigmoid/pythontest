from rag.chatbot import ask_question

question = "What is the availability target mentioned in the PDF?"

answer = ask_question(question)

print(answer)