import os
import json
import pandas as pd
from datasets import Dataset
import time
from ragas import evaluate
from ragas.metrics import (
    context_recall,
    faithfulness,
    answer_relevancy,
    context_precision, 
    FactualCorrectness,
    answer_similarity,
    AnswerAccuracy,
    BleuScore,
    RougeScore,
    ExactMatch,
    StringPresence,
    ContextRelevance,
    ResponseGroundedness
)
from src.pipeline import get_rag_chain
from tqdm import tqdm

def run_ragas_evaluation(model_name, answer_delay=30, eval_delay=30, eval_json="eval_questions.json"):
    SUBJECT = "Machine Learning"
    SUBJECT_KEY = SUBJECT.replace(" ", "_").lower()
    OUTPUT_DIR = "outputs/ragas_eval"
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    OUTPUT_BASENAME = f"{SUBJECT_KEY}_{model_name}_results"
    OUTPUT_JSON = os.path.join(OUTPUT_DIR, f"{OUTPUT_BASENAME}.json")
    OUTPUT_CSV = os.path.join(OUTPUT_DIR, f"{OUTPUT_BASENAME}.csv")

    # Check for existing .json and return if exists
    if os.path.exists(OUTPUT_JSON):
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            results = json.load(f)
        return results

    # ---- Actual evaluation (copied from your latest script, no subject argument needed) ----
    def load_eval_questions(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            questions = json.load(f)
        for i, q in enumerate(questions):
            q['id'] = i + 1
        return questions

    def generate_answers(questions, llm_backend, subject, delay=30):
        chroma_dir = f"outputs/chroma_{subject.replace(' ', '_').lower()}"
        rag_chain = get_rag_chain(chroma_persist_dir=chroma_dir, llm_backend=llm_backend)
        for idx, q in enumerate(tqdm(questions, desc="Generating Answers")):
            q['answer'] = rag_chain.invoke(q['question'])
            print(f"[INFO] Answer generated for Q{idx+1}/{len(questions)}. Sleeping for {delay} seconds...")
            if idx < len(questions) - 1:
                time.sleep(delay)
        return questions

    questions = load_eval_questions(eval_json)
    questions = generate_answers(questions, llm_backend=model_name, subject=SUBJECT, delay=answer_delay)
    df = pd.DataFrame(questions)[['id', 'question', 'contexts', 'answer', 'ground_truth']]
    metrics = [context_recall, faithfulness, answer_relevancy, context_precision,
               FactualCorrectness(), answer_similarity, AnswerAccuracy(), BleuScore(), RougeScore(),
               ExactMatch(), StringPresence(), ContextRelevance(), ResponseGroundedness()]
    metric_results = []
    print("\n[INFO] Running RAGAS evaluation per-question with delay...")
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Evaluating Questions"):
        single_row_ds = Dataset.from_pandas(pd.DataFrame([row]))
        result = evaluate(single_row_ds, metrics=metrics)
        if hasattr(result, "scores") and isinstance(result.scores, pd.DataFrame):
            metric_row = result.scores.iloc[0].to_dict()
        else:
            metric_row = result.to_pandas().iloc[0].to_dict()
        metric_results.append(metric_row)
        print(f"[INFO] Evaluation done for Q{row['id']}. Sleeping for {eval_delay} seconds...")
        if idx < len(df) - 1:
            time.sleep(eval_delay)
    metrics_df = pd.DataFrame(metric_results)
    final_df = pd.concat([df, metrics_df], axis=1)
    final_df.to_json(OUTPUT_JSON, orient="records", indent=2, force_ascii=False)
    final_df.to_csv(OUTPUT_CSV, index=False)
    print(f"[INFO] Per-question evaluation saved to {OUTPUT_JSON}")
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        results = json.load(f)
    return results
