import ollama
import chromadb

EMBED_MODEL = "nomic-embed-text"

client = chromadb.PersistentClient(
    path="./knowledge_db"
)

collection = client.get_or_create_collection(
    name="knowledge"
)


def add_knowledge():
    documents = [
        "Generative AI is a type of artificial intelligence that can create new content such as text, images, audio, and code.",
        "RAG stands for Retrieval-Augmented Generation. It retrieves relevant information before generating an answer.",
        "Embeddings convert text into numerical vectors so that semantic similarity can be calculated.",
        "LangGraph is a framework for building stateful and controllable AI agent workflows.",
        "An AI agent can make decisions, use tools, and perform actions based on a user's goal."
    ]

    existing = collection.count()

    if existing == 0:
        for i, document in enumerate(documents):
            response = ollama.embed(
                model=EMBED_MODEL,
                input=document
            )

            embedding = response["embeddings"][0]

            collection.add(
                ids=[str(i)],
                embeddings=[embedding],
                documents=[document]
            )


def search_knowledge(question: str) -> str:
    add_knowledge()

    response = ollama.embed(
        model=EMBED_MODEL,
        input=question
    )

    query_embedding = response["embeddings"][0]

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=2
    )

    documents = results["documents"][0]

    if not documents:
        return "No relevant knowledge found."

    return "\n".join(documents)


if __name__ == "__main__":
    question = input("Search knowledge: ")

    result = search_knowledge(question)

    print("\nKnowledge:")
    print(result)