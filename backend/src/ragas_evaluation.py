import json
import pandas as pd
from ragas import evaluate
from datasets import Dataset
from src.pipeline import get_rag_chain, get_retriever, load_chroma_vectorstore, get_fastembed_embedding
from dotenv import load_dotenv
import math
import logging

load_dotenv()

# Add numpy for complete nan/inf handling
import numpy as np

def load_eval_questions(json_path="eval_questions.json"):
    with open(json_path, 'r', encoding='utf-8') as f:
        return pd.DataFrame(json.load(f))

def fill_contexts_and_answers(df, subject, model_name):
    chroma_dir = f"outputs/chroma_{subject.replace(' ', '_').lower()}"
    # Load embedding and vectorstore
    embed_model = get_fastembed_embedding()
    vectorstore = load_chroma_vectorstore(embed_model, persist_directory=chroma_dir)
    retriever = get_retriever(vectorstore, k=2)
    rag_chain = get_rag_chain(chroma_persist_dir=chroma_dir, llm_backend=model_name)
    
    for i, row in df.iterrows():
        question = row['question']
        # Use .invoke() for new LangChain retriever, fallback for older versions
        try:
            retrieval_result = retriever.invoke(question)
        except Exception:
            retrieval_result = retriever.get_relevant_documents(question)
        contexts = [doc.page_content for doc in retrieval_result]
        df.at[i, 'contexts'] = contexts
        answer = rag_chain.invoke(question)
        df.at[i, 'answer'] = answer
    return df

def nan_to_none(obj, _found=[False]):
    """Recursively convert NaN/Inf (both Python and numpy) in any nested structure to None."""
    if isinstance(obj, dict):
        return {k: nan_to_none(v, _found) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [nan_to_none(x, _found) for x in obj]
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            _found[0] = True
            return None
        return obj
    elif isinstance(obj, np.floating):
        if np.isnan(obj) or np.isinf(obj):
            _found[0] = True
            return None
        return float(obj)
    else:
        return obj

def check_for_nan(obj, path="root"):
    """Recursively check for any NaN/Inf values and print their paths."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            check_for_nan(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for idx, x in enumerate(obj):
            check_for_nan(x, f"{path}[{idx}]")
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            print(f"!!! NaN/Inf at {path}: {obj}")
    elif isinstance(obj, np.floating):
        if np.isnan(obj) or np.isinf(obj):
            print(f"!!! np.NaN/np.Inf at {path}: {obj}")

def run_ragas_evaluation(df):
    print(df[["question", "ground_truth", "contexts", "answer"]])
    print(df["contexts"].apply(lambda x: type(x)))
    ds = Dataset.from_pandas(df)
    metrics = evaluate(ds)
    return metrics

def evaluate_ragas(subject, model_name, eval_json="eval_questions.json"):
    df = load_eval_questions(eval_json)
    df = fill_contexts_and_answers(df, subject, model_name)
    for idx, row in df.iterrows():
        print(f"\nQ{idx+1}:")
        print(f"  Contexts: {row['contexts']}")
        print(f"  Answer: {row['answer']}")
        print(f"  Ground Truth: {row['ground_truth']}")
    metrics = run_ragas_evaluation(df)
    # Deep clean before returning!
    replaced = [False]
    metrics_clean = nan_to_none(metrics, replaced)
    # Debug: show sanitized JSON string in logs, check for remaining NaNs/Infs
    check_for_nan(metrics_clean)
    try:
        json_str = json.dumps(metrics_clean)
        logging.warning("RAGAS metrics cleaned and serializable.")
    except Exception as e:
        logging.error(f"Serialization still fails: {e}")
        print(metrics_clean)  # Print full output for troubleshooting
        raise
    if replaced[0]:
        logging.warning("NaN or Infinity found and replaced with None in metrics output!")
    return metrics_clean
