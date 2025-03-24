# hybrid_numeric_semantic.py

import datetime
import pandas as pd
from sentence_transformers import SentenceTransformer
from chromadb import Client
from chromadb.errors import InvalidCollectionException


def main():
    """
    Demonstration of a minimal "hybrid" approach that combines:
      1) Semantic retrieval from ChromaDB.
      2) Basic numeric filtering/analysis with Pandas.
    """

    # --------------------------------------------------
    # 1) Connect to ChromaDB
    # --------------------------------------------------
    chroma_client = Client()

    # Name of the collection we want to use:
    collection_name = "financial_docs"

    try:
        # Try to get the existing collection
        collection = chroma_client.get_collection(name=collection_name)
        print(f"Found collection: {collection_name}")
    except InvalidCollectionException:
        # If not found: create the collection with that name
        print(f"Collection '{collection_name}' not found. Creating one now...")
        collection = chroma_client.create_collection(name=collection_name)

        # (Optional) Insert documents right here if needed, for example:
        # collection.add(
        #     documents=["Sample text doc..."],
        #     metadatas=[{"source": "example"}],
        #     ids=["doc_001"]
        # )

    # --------------------------------------------------
    # 2) Semantic Retrieval
    # --------------------------------------------------
    model_name = "all-MiniLM-L6-v2"
    model = SentenceTransformer(model_name)

    user_query = "Show me TSLA related entries in March-April 2022."
    query_embedding = model.encode(user_query)

    # NOTE: For a single query, pass [query_embedding] as a list of length 1:
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=10
    )

    # The "results" dict has nested lists. For a single query, you'll typically do:
    #   results['ids'][0]        -> list of doc IDs for that single query
    #   results['documents'][0]  -> list of doc texts
    #   results['metadatas'][0]  -> list of metadata dicts
    #
    # If the collection is empty, these lists will be empty or not present.
    # We'll handle it gently:
    doc_ids = []
    if "ids" in results and len(results["ids"]) > 0:
        doc_ids = results["ids"][0]  # first (and only) query

    print("==== SEMANTIC RETRIEVAL ====")
    print(f"User query: {user_query}")
    print(f"Retrieved Document IDs from ChromaDB: {doc_ids}\n")

    # --------------------------------------------------
    # 3) Numeric Analysis with Pandas
    # --------------------------------------------------
    csv_file_path = "daily_stock_prices_5y_cleaned.csv"
    df = pd.read_csv(csv_file_path, parse_dates=["Date"])

    start_date = "2022-03-01"
    end_date = "2022-04-30"
    mask = (
            (df["Company"] == "TSLA") &
            (df["Date"] >= start_date) &
            (df["Date"] <= end_date)
    )
    filtered_df = df[mask]

    mean_close_price = filtered_df["Close"].mean()
    total_volume = filtered_df["Volume"].sum()

    print("==== NUMERIC ANALYSIS (TSLA, Mar-Apr 2022) ====")
    print(f"Rows found: {len(filtered_df)}")
    print(f"Average Closing Price: {mean_close_price:.2f}")
    print(f"Total Volume: {total_volume}\n")

    # --------------------------------------------------
    # 4) HYBRID INTEGRATION EXAMPLE
    # --------------------------------------------------
    # We'll just simulate doc_ids like "TSLA_YYYY-MM-DD"
    pretend_doc_ids = ["TSLA_2022-03-21", "TSLA_2022-04-05"]

    parsed_dates = []
    for doc_id in pretend_doc_ids:
        # doc_id might be "TSLA_YYYY-MM-DD":
        _, date_str = doc_id.split("_", 1)
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        parsed_dates.append(date_obj)

    # Now match the rows in 'filtered_df' whose Date matches the doc_ids:
    hybrid_mask = filtered_df["Date"].dt.date.isin(parsed_dates)
    hybrid_df = filtered_df[hybrid_mask]

    print("==== HYBRID INTEGRATION EXAMPLE ====")
    print(f"Fake doc_ids used: {pretend_doc_ids}")
    print("Matching rows in the numeric dataset:")
    print(hybrid_df)

    print("\nDone! This demonstrates a minimal semantic + numeric integration.")


if __name__ == "__main__":
    main()
