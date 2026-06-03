import os


def load_documents(folder_path):

    documents = []

    for file_name in os.listdir(folder_path):

        if file_name.endswith(".txt"):

            file_path = os.path.join(folder_path, file_name)

            with open(file_path, "r", encoding="utf-8") as file:

                content = file.read()

                documents.append(
                    {
                        "file_name": file_name,
                        "content": content
                    }
                )

    return documents