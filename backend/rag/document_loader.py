from pathlib import Path
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader
)


def load_documents():

    documents = []

    project_root = Path(__file__).resolve().parents[2]

    knowledge_base = project_root / "knowledge_base" / "policies"

    print(f"\nScanning: {knowledge_base}\n")

    for file in knowledge_base.rglob("*"):

        print("Found:", file)

        if not file.is_file():
            continue

        try:

            print(f"Trying to load {file.name}")

            if file.suffix.lower() == ".pdf":

                loader = PyPDFLoader(str(file))

            elif file.suffix.lower() == ".docx":

                loader = Docx2txtLoader(str(file))

            else:
                continue

            docs = loader.load()

            print(
                f"SUCCESS -> {file.name} : {len(docs)} pages"
            )

            documents.extend(docs)

        except Exception as e:

            print(f"FAILED -> {file.name}")
            print(e)

    print(f"\nTotal Loaded Documents: {len(documents)}")

    return documents