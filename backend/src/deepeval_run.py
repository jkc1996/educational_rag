import os
import sys
import json
import time
from dotenv import load_dotenv
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
    ToxicityMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    ContextualRelevancyMetric,
)
from deepeval.models import GPTModel
from deepeval.test_case import LLMTestCase
from deepeval import evaluate
from deepeval.evaluate import DisplayConfig

# === 1. Setup Paths and Models ===
load_dotenv()
EVAL_QUESTIONS_JSON = "ml_eval_questions.json"
ANSWERED_JSON_TEMPLATE = "ml_eval_answers_{backend}.json"
DEEPEVAL_RESULTS_TEMPLATE = "cache/deepeval_metrics_{backend}_{metric}.json"
os.makedirs("cache", exist_ok=True)

from src.pipeline import get_rag_chain, get_retriever, load_chroma_vectorstore, get_fastembed_embedding

# === 3. Helper to Generate Answers ===
def generate_answers_for_backend(json_path, backend, subject="Machine Learning", sleep_between=30):
    print(f"\n[INFO] Generating answers using {backend}...")
    with open(json_path, "r", encoding="utf-8") as f:
        original_questions = json.load(f)

    chroma_dir = f"outputs/chroma_{subject.replace(' ', '_').lower()}"
    embed_model = get_fastembed_embedding()
    vectorstore = load_chroma_vectorstore(embed_model, persist_directory=chroma_dir)
    retriever = get_retriever(vectorstore, k=2)
    rag_chain = get_rag_chain(chroma_persist_dir=chroma_dir, llm_backend=backend)

    updated_questions = []
    for i, q in enumerate(original_questions):
        q_input = q["input"]
        answer = rag_chain.invoke(q_input)
        q_new = dict(q)
        q_new["actual_output"] = answer
        updated_questions.append(q_new)
        print(f"[INFO] Answered Q{i+1}/{len(original_questions)}")
        if i < len(original_questions) - 1:
            print(f"    Sleeping {sleep_between}s to avoid backend rate limit...")
            time.sleep(sleep_between)

    out_path = ANSWERED_JSON_TEMPLATE.format(backend=backend)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(updated_questions, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Answers generated and saved to {out_path}")
    return out_path

def run_deepeval_all_metrics(answered_json_path, backend, metric_map, sleep_between=3):
    print(f"\n[INFO] Running DeepEval (all metrics) for {backend} answers...")
    with open(answered_json_path, "r", encoding="utf-8") as f:
        eval_data = json.load(f)

    # Model for judging
    judge_model = GPTModel(
        model="gpt-3.5-turbo",
        temperature=0,
        cost_per_input_token=0.000002,
        cost_per_output_token=0.000008
    )

    # Prepare metric classes ahead of time
    metrics = [(name, cls(model=judge_model)) for name, cls in metric_map]

    results = []
    for idx, row in enumerate(eval_data):
        row_result = {
            "input": row["input"],
            "actual_output": row["actual_output"],
            "expected_output": row.get("expected_output", ""),
            "context": row.get("context", []),
            "retrieval_context": row.get("retrieval_context", []),
            "metrics": {}
        }
        print(f"[INFO] Evaluating Q{idx+1}/{len(eval_data)}")
        for metric_name, metric in metrics:
            test_case = LLMTestCase(
                input=row["input"],
                actual_output=row["actual_output"],
                expected_output=row.get("expected_output", ""),
                context=row.get("context", []),
                retrieval_context=row.get("retrieval_context", [])
            )
            try:
                metrics_summary, test_results = evaluate([test_case], [metric], display_config=DisplayConfig(file_output_dir="cache/deepeval_local"))
                # === DEBUG: Print the test_results object and metrics_data
                print(f"  [{metric_name}] test_results[0]: {test_results[0]}")
                mdata_list = getattr(test_results[0], "metrics_data", None)
                print(f"      metrics_data: {mdata_list}")
                if mdata_list and len(mdata_list) > 0:
                    mdata = mdata_list[0]
                    metric_info = {
                        "score": getattr(mdata, "score", None),
                        "reason": getattr(mdata, "reason", None),
                        "pass": getattr(mdata, "success", None),
                        "threshold": getattr(mdata, "threshold", None),
                        "model": getattr(mdata, "evaluation_model", None),
                        # Raw for debugging, but stringified
                        "raw": str(mdata),
                    }
                else:
                    metric_info = {
                        "error": "No metric_data",
                        "raw": str(test_results[0])
                    }
                row_result["metrics"][metric_name] = metric_info
            except Exception as e:
                row_result["metrics"][metric_name] = {"error": str(e)}
                print(f"[WARN] {metric_name}: Skipping Q{idx+1}: {e}")
            print(f"    [{metric_name}] Done.")
            time.sleep(sleep_between)
        results.append(row_result)

    # --- Serialization helper ---
    def to_serializable(obj):
        if isinstance(obj, dict):
            return {k: to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [to_serializable(x) for x in obj]
        elif hasattr(obj, "__dict__"):
            return {k: to_serializable(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
        elif isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        elif hasattr(obj, "__str__"):
            return str(obj)
        else:
            return str(obj)

    out_path = f"cache/deepeval_metrics_{backend}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(to_serializable(results), f, indent=2, ensure_ascii=False)
    print(f"[INFO] All metrics results saved to {out_path}")
    return out_path

# === 5. Main CLI ===
if __name__ == "__main__":
    all_backends = ["groq"]  # Change as needed

    metric_map = [
        ("answer_relevancy", AnswerRelevancyMetric),
        ("faithfulness", FaithfulnessMetric),
        ("hallucination", HallucinationMetric),
        # ("toxicity", ToxicityMetric),
        # ("contextual_precision", ContextualPrecisionMetric),
        # ("contextual_recall", ContextualRecallMetric),
        # ("contextual_relevancy", ContextualRelevancyMetric),
    ]

    for backend in all_backends:
        answered_path = generate_answers_for_backend(EVAL_QUESTIONS_JSON, backend, sleep_between=30)
        run_deepeval_all_metrics(answered_path, backend, metric_map, sleep_between=25)

    print("\n[INFO] ALL DONE! Answers & DeepEval results are in 'cache/' (one file per backend).")
