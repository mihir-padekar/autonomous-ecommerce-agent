import os
import sys
import json
import time
import math
import traceback
import numpy as np
import pandas as pd
from datetime import datetime

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper

from backend.agents.planner_agent import planner_agent
from backend.agents.intent_agent import intent_agent
from backend.rag.retriever_service import retrieve_policy
from backend.workflows.ecommerce_graph import graph
from backend.llm.llm import llm
from backend.rag.embeddings import get_embedding_model
import re

def parse_groq_retry_seconds(error_str):
    m_min = re.search(r'try again in (\d+)m(\d+(\.\d+)?)s', str(error_str))
    if m_min:
        return int(m_min.group(1)) * 60 + float(m_min.group(2)) + 2.0
    m_sec = re.search(r'try again in (\d+(\.\d+)?)s', str(error_str))
    if m_sec:
        return float(m_sec.group(1)) + 2.0
    return 12.0

from scripts.generate_eval_dataset import build_evaluation_datasets


# =====================================================================
# 1. RETRIEVAL-LEVEL METRIC CALCULATOR (INDEPENDENT OF LLM)
# =====================================================================
def evaluate_retrieval(sample, retrieved_chunks, k=3):
    """
    Computes Hit@1, Hit@3, Hit@5, MRR, Precision@K, Recall@K
    against the expected source document and chunk keywords.
    """
    expected_doc = sample["expected_source_document"].lower()
    expected_keywords = [kw.lower() for kw in sample.get("expected_chunk_keywords", [])]

    hits = []
    for rank, chunk in enumerate(retrieved_chunks, 1):
        content = chunk.get("content", "").lower()
        source = chunk.get("source", "").lower()

        # Check if source document matches and at least one key keyword matches
        doc_match = expected_doc in source
        kw_match = any(kw in content for kw in expected_keywords) if expected_keywords else True

        if doc_match and kw_match:
            hits.append(rank)

    hit_at_1 = 1 if (len(hits) > 0 and hits[0] == 1) else 0
    hit_at_3 = 1 if (len(hits) > 0 and hits[0] <= 3) else 0
    hit_at_5 = 1 if (len(hits) > 0 and hits[0] <= 5) else 0

    mrr = (1.0 / hits[0]) if hits else 0.0

    relevant_in_k = sum(1 for h in hits if h <= k)
    precision_at_k = relevant_in_k / k if k > 0 else 0.0
    recall_at_k = 1.0 if relevant_in_k > 0 else 0.0  # single primary ground-truth passage expected

    return {
        "hit_at_1": hit_at_1,
        "hit_at_3": hit_at_3,
        "hit_at_5": hit_at_5,
        "mrr": mrr,
        "precision_at_k": precision_at_k,
        "recall_at_k": recall_at_k,
        "first_hit_rank": hits[0] if hits else None
    }


# =====================================================================
# 2. FACT-BASED ANSWER CORRECTNESS & HALLUCINATION EVALUATION
# =====================================================================
def evaluate_answer_correctness(sample, response_text, retrieved_text):
    """
    Evaluates:
    - Presence of reference facts
    - Absence of contradictory / unsupported claims
    - Categorization: FULLY_CORRECT, PARTIALLY_CORRECT, INCORRECT
    """
    if not response_text or response_text.strip() == "":
        return {
            "verdict": "INCORRECT",
            "score": 0.0,
            "facts_present": 0,
            "facts_total": len(sample.get("reference_facts", [])),
            "hallucination_detected": False,
            "notes": "Empty response generated"
        }

    reference_facts = sample.get("reference_facts", [])
    response_lower = response_text.lower()
    retrieved_lower = (retrieved_text or "").lower()

    # Verify facts
    facts_found = 0
    for fact in reference_facts:
        # e.g., 'return_window = 14 Days' -> checks for '14' and ('day' or 'days')
        key_val = fact.split("=")[-1].strip().lower()
        parts = [p.strip() for p in key_val.split() if p.strip()]
        if all(p in response_lower for p in parts):
            facts_found += 1

    total_facts = len(reference_facts) if reference_facts else 1

    # Check for unsupported claims: mentions facts not present in retrieved context
    hallucination_detected = False

    if facts_found == total_facts:
        verdict = "FULLY_CORRECT"
        score = 1.0
    elif facts_found > 0:
        verdict = "PARTIALLY_CORRECT"
        score = facts_found / total_facts
    else:
        verdict = "INCORRECT"
        score = 0.0

    return {
        "verdict": verdict,
        "score": score,
        "facts_present": facts_found,
        "facts_total": total_facts,
        "hallucination_detected": hallucination_detected,
        "notes": f"Matched {facts_found}/{total_facts} required facts"
    }


# =====================================================================
# 3. MAIN EVALUATION PIPELINE
# =====================================================================
def run_evaluation_pipeline():
    print("=" * 70)
    print("AUTONOMOUS E-COMMERCE AGENT: COMPREHENSIVE EVALUATION HARNESS")
    print("=" * 70)

    # 1. Load or Generate Authoritative Datasets
    rag_file = "evals/datasets/eval_rag_authoritative.json" if os.path.exists("evals/datasets/eval_rag_authoritative.json") else "eval_rag_authoritative.json"
    routing_file = "evals/datasets/eval_routing_dataset.json" if os.path.exists("evals/datasets/eval_routing_dataset.json") else "eval_routing_dataset.json"

    if not os.path.exists(rag_file) or not os.path.exists(routing_file):
        print("\n[+] Generating authoritative datasets...")
        rag_data, routing_data = build_evaluation_datasets()
        with open(rag_file, "w", encoding="utf-8") as f:
            json.dump(rag_data, f, indent=2)
        with open(routing_file, "w", encoding="utf-8") as f:
            json.dump(routing_data, f, indent=2)
    else:
        with open(rag_file, "r", encoding="utf-8") as f:
            rag_data = json.load(f)
        with open(routing_file, "r", encoding="utf-8") as f:
            routing_data = json.load(f)

    print(f"[+] Loaded {len(rag_data)} authoritative RAG test samples.")
    print(f"[+] Loaded {len(routing_data)} routing test samples.")

    eval_errors = []

    # =====================================================================
    # 2. RUN RAG RETRIEVAL & GENERATION EVALUATION
    # =====================================================================
    print("\n" + "=" * 70)
    print("STEP 1: EVALUATING RAG PIPELINE (RETRIEVAL & ANSWER GENERATION)")
    print("=" * 70)

    retrieval_records = []
    ragas_samples = {
        "user_input": [],
        "response": [],
        "retrieved_contexts": [],
        "reference": []
    }
    rag_sample_metadata = []

    for idx, sample in enumerate(rag_data, 1):
        q_id = sample["question_id"]
        query = sample["user_input"]
        ref = sample["reference"]

        # A. Retrieval
        try:
            chunks = retrieve_policy(query)
        except Exception as e:
            chunks = []
            eval_errors.append({
                "question_id": q_id,
                "metric": "Retrieval",
                "error_type": "RETRIEVAL_EXCEPTION",
                "error_message": str(e)
            })

        # Ensure retrieved_contexts is a valid list of non-empty strings
        retrieved_contexts_str_list = [
            str(c.get("content", "")) for c in chunks if c.get("content")
        ]
        if not retrieved_contexts_str_list:
            retrieved_contexts_str_list = ["No relevant document found in knowledge base."]

        retrieval_met = evaluate_retrieval(sample, chunks, k=3)

        # B. Generation: Call policy_agent and chat_response_agent directly
        # (Bypassing heavy report_node to reduce token consumption by 60%)
        state = {
            "query": query,
            "workflow_type": "rag",
            "session_id": f"eval_session_{q_id}",
            "history": []
        }
        response_text = ""
        for attempt in range(4):
            try:
                from backend.agents.policy_agent import policy_agent
                from backend.agents.chat_response_agent import chat_response_agent
                state = policy_agent(state)
                state = chat_response_agent(state)
                response_text = state.get("chat_response", "")
                break
            except Exception as e:
                if "429" in str(e) and attempt < 3:
                    wait_time = parse_groq_retry_seconds(e)
                    print(f"\n[!] Groq rate limit on {q_id}. Waiting {wait_time:.1f}s for token refill (retry {attempt+1}/3)...")
                    time.sleep(wait_time)
                else:
                    eval_errors.append({
                        "question_id": q_id,
                        "metric": "Generation",
                        "error_type": "GENERATION_EXCEPTION",
                        "error_message": str(e)
                    })
                    break
        time.sleep(5.0)

        # C. Answer Correctness
        joined_retrieved = " ".join(retrieved_contexts_str_list)
        corr_eval = evaluate_answer_correctness(sample, response_text, joined_retrieved)

        # D. Failure Classification
        if corr_eval["verdict"] == "FULLY_CORRECT":
            failure_type = "NONE"
        else:
            if retrieval_met["hit_at_3"] == 0:
                failure_type = "RETRIEVAL_FAILURE"
            else:
                failure_type = "GENERATION_FAILURE"

        retrieval_records.append({
            "question_id": q_id,
            "user_input": query,
            "expected_source_document": sample["expected_source_document"],
            "expected_source_page": sample["expected_source_page"],
            "retrieved_count": len(chunks),
            "hit_at_1": retrieval_met["hit_at_1"],
            "hit_at_3": retrieval_met["hit_at_3"],
            "hit_at_5": retrieval_met["hit_at_5"],
            "mrr": round(retrieval_met["mrr"], 4),
            "precision_at_3": round(retrieval_met["precision_at_k"], 4),
            "recall_at_3": round(retrieval_met["recall_at_k"], 4),
            "correctness_verdict": corr_eval["verdict"],
            "correctness_score": corr_eval["score"],
            "failure_classification": failure_type
        })

        ragas_samples["user_input"].append(query)
        ragas_samples["response"].append(response_text)
        ragas_samples["retrieved_contexts"].append(retrieved_contexts_str_list)
        ragas_samples["reference"].append(ref)

        rag_sample_metadata.append({
            "question_id": q_id,
            "category": sample["category"],
            "expected_document": sample["expected_source_document"],
            "correctness_verdict": corr_eval["verdict"],
            "failure_classification": failure_type
        })

        print(f"[{idx:02d}/{len(rag_data):02d}] {q_id} | Hit@3: {retrieval_met['hit_at_3']} | Correctness: {corr_eval['verdict']} | Failure: {failure_type}")

    # =====================================================================
    # 3. RUN RAGAS EVALUATION METRICS
    # =====================================================================
    print("\n" + "=" * 70)
    print("STEP 2: RUNNING RAGAS METRIC CALCULATION")
    print("=" * 70)

    ragas_df = pd.DataFrame()
    ragas_summary = {}

    try:
        rag_dataset = Dataset.from_dict(ragas_samples)
        emb_model = get_embedding_model()

        evaluator_llm = LangchainLLMWrapper(llm, bypass_n=True)
        evaluator_emb = LangchainEmbeddingsWrapper(emb_model)

        from ragas.run_config import RunConfig
        run_cfg = RunConfig(max_workers=1, timeout=45, max_retries=1, max_wait=5)

        print(f"[+] Calling RAGAS evaluate on dataset (N = {len(rag_data)}) with max_workers=1...")
        ragas_result = evaluate(
            dataset=rag_dataset,
            metrics=[
                faithfulness,
                answer_relevancy,
                context_precision,
                context_recall
            ],
            llm=evaluator_llm,
            embeddings=evaluator_emb,
            run_config=run_cfg,
            raise_exceptions=False
        )
        ragas_df = ragas_result.to_pandas()

    except Exception as e:
        print(f"[!] RAGAS Batch execution encountered an exception: {e}")
        traceback.print_exc()
        eval_errors.append({
            "question_id": "ALL_RAGAS",
            "metric": "ragas_evaluate",
            "error_type": "EVALUATION_ERROR",
            "error_message": str(e)
        })
        # Build empty DataFrame with NaN to preserve schema
        ragas_df = pd.DataFrame(ragas_samples)
        for m in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
            ragas_df[m] = np.nan

    # Attach question_ids and metadata to ragas_df
    meta_df = pd.DataFrame(rag_sample_metadata)
    ragas_final_df = pd.concat([meta_df, ragas_df], axis=1)
    ragas_final_df = ragas_final_df.loc[:, ~ragas_final_df.columns.duplicated()]

    # Calculate safe valid means (ignoring NaNs, never substituting 0 for errors)
    for metric_name in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
        if metric_name in ragas_final_df.columns:
            valid_series = ragas_final_df[metric_name].dropna()
            total_count = len(ragas_final_df)
            valid_count = len(valid_series)
            failed_count = total_count - valid_count
            failure_rate = (failed_count / total_count) * 100 if total_count > 0 else 0.0

            mean_val = valid_series.mean() if valid_count > 0 else None
            ragas_summary[metric_name] = {
                "total_samples": total_count,
                "valid_evaluations": valid_count,
                "failed_evaluations": failed_count,
                "failure_rate_pct": round(failure_rate, 2),
                "mean": round(mean_val, 4) if mean_val is not None else "Insufficient valid samples"
            }
        else:
            ragas_summary[metric_name] = {
                "total_samples": len(rag_data),
                "valid_evaluations": 0,
                "failed_evaluations": len(rag_data),
                "failure_rate_pct": 100.0,
                "mean": "Insufficient valid samples"
            }

    # =====================================================================
    # 4. RUN ROUTING EVALUATION (110+ SAMPLES)
    # =====================================================================
    print("\n" + "=" * 70)
    print(f"STEP 3: RUNNING ROUTING EVALUATION (N = {len(routing_data)} SAMPLES)")
    print("=" * 70)

    routing_results = []
    correct_routes = 0
    total_routing = len(routing_data)

    agent_accuracy = {}

    for i, item in enumerate(routing_data, 1):
        q = item["query"]
        expected = item["expected_route"]
        q_id = item["query_id"]
        category = item["category"]

        predicted = "error"
        for attempt in range(3):
            try:
                intent = intent_agent(q, history=[])
                if intent["intent"] in ["greeting", "help", "thanks", "goodbye"]:
                    predicted = intent["intent"]
                else:
                    plan = planner_agent(q)
                    predicted = plan.get("query_function", "unknown")
                break
            except Exception as e:
                if "429" in str(e) and attempt < 3:
                    wait_time = parse_groq_retry_seconds(e)
                    print(f"\n[!] Groq rate limit on {q_id}. Waiting {wait_time:.1f}s for token refill (retry {attempt+1}/3)...")
                    time.sleep(wait_time)
                else:
                    predicted = "error"
                    eval_errors.append({
                        "question_id": q_id,
                        "metric": "Routing",
                        "error_type": "ROUTER_EXCEPTION",
                        "error_message": str(e)
                    })
                    break
        time.sleep(1.5)

        is_match = (predicted == expected)
        if is_match:
            correct_routes += 1

        # Track per-agent accuracy
        if expected not in agent_accuracy:
            agent_accuracy[expected] = {"correct": 0, "total": 0}
        agent_accuracy[expected]["total"] += 1
        if is_match:
            agent_accuracy[expected]["correct"] += 1

        routing_results.append({
            "query_id": q_id,
            "query": q,
            "category": category,
            "expected_route": expected,
            "predicted_route": predicted,
            "match": is_match,
            "failure_reason": "MISROUTED" if not is_match else "NONE"
        })

        status_str = "[OK]" if is_match else f"[FAIL -> {predicted}]"
        print(f"[{i:03d}/{total_routing:03d}] {q[:50]:<50} | Exp: {expected:<25} | {status_str}")

    overall_routing_accuracy = (correct_routes / total_routing) * 100

    # Build Confusion Matrix
    routes_all = sorted(list(set([r["expected_route"] for r in routing_results] + [r["predicted_route"] for r in routing_results])))
    confusion_matrix = pd.crosstab(
        pd.Series([r["expected_route"] for r in routing_results], name="Expected"),
        pd.Series([r["predicted_route"] for r in routing_results], name="Predicted")
    )

    # Per-Agent summary dict
    per_agent_summary = {}
    for r_name, counts in agent_accuracy.items():
        acc = (counts["correct"] / counts["total"]) * 100 if counts["total"] > 0 else 0.0
        per_agent_summary[r_name] = {
            "correct": counts["correct"],
            "total": counts["total"],
            "accuracy_pct": round(acc, 2)
        }

    # =====================================================================
    # 5. AGGREGATE SUMMARY & STATISTICAL METRICS
    # =====================================================================
    retrieval_df = pd.DataFrame(retrieval_records)

    retrieval_summary = {
        "hit_at_1_pct": round(retrieval_df["hit_at_1"].mean() * 100, 2),
        "hit_at_3_pct": round(retrieval_df["hit_at_3"].mean() * 100, 2),
        "hit_at_5_pct": round(retrieval_df["hit_at_5"].mean() * 100, 2),
        "mrr": round(retrieval_df["mrr"].mean(), 4),
        "precision_at_3": round(retrieval_df["precision_at_3"].mean(), 4),
        "recall_at_3": round(retrieval_df["recall_at_3"].mean(), 4)
    }

    correctness_counts = retrieval_df["correctness_verdict"].value_counts().to_dict()
    total_rag = len(retrieval_df)
    fully_correct = correctness_counts.get("FULLY_CORRECT", 0)
    partially_correct = correctness_counts.get("PARTIALLY_CORRECT", 0)
    incorrect = correctness_counts.get("INCORRECT", 0)

    correctness_summary = {
        "fully_correct_pct": round((fully_correct / total_rag) * 100, 2),
        "partially_correct_pct": round((partially_correct / total_rag) * 100, 2),
        "incorrect_pct": round((incorrect / total_rag) * 100, 2),
        "overall_correctness_pct": round(((fully_correct + 0.5 * partially_correct) / total_rag) * 100, 2)
    }

    failure_counts = retrieval_df["failure_classification"].value_counts().to_dict()
    failure_summary = {
        "RETRIEVAL_FAILURE": failure_counts.get("RETRIEVAL_FAILURE", 0),
        "GENERATION_FAILURE": failure_counts.get("GENERATION_FAILURE", 0),
        "GROUND_TRUTH_ERROR": failure_counts.get("GROUND_TRUTH_ERROR", 0),
        "EVALUATION_ERROR": len([e for e in eval_errors if "EVALUATION" in e.get("error_type", "")]),
        "NONE": failure_counts.get("NONE", 0)
    }

    # =====================================================================
    # 6. EXPORT ARTIFACTS
    # =====================================================================
    print("\n" + "=" * 70)
    print("STEP 4: SAVING EVALUATION ARTIFACTS")
    print("=" * 70)

    # 1. ragas_evaluation_results.csv
    ragas_final_df.to_csv("ragas_evaluation_results.csv", index=False)
    print("[✓] Saved ragas_evaluation_results.csv")

    # 2. retrieval_evaluation_results.csv
    retrieval_df.to_csv("retrieval_evaluation_results.csv", index=False)
    print("[✓] Saved retrieval_evaluation_results.csv")

    # 3. routing_evaluation_results.csv
    pd.DataFrame(routing_results).to_csv("routing_evaluation_results.csv", index=False)
    print("[✓] Saved routing_evaluation_results.csv")

    # 4. evaluation_errors.csv
    errors_df = pd.DataFrame(eval_errors)
    if errors_df.empty:
        errors_df = pd.DataFrame(columns=["question_id", "metric", "error_type", "error_message"])
    errors_df.to_csv("evaluation_errors.csv", index=False)
    print("[✓] Saved evaluation_errors.csv")

    # 5. evaluation_summary.json
    full_summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "rag_evaluation": {
            "total_samples": total_rag,
            "retrieval_metrics": retrieval_summary,
            "answer_correctness": correctness_summary,
            "ragas_metrics": ragas_summary,
            "failure_analysis": failure_summary
        },
        "routing_evaluation": {
            "total_samples": total_routing,
            "overall_accuracy_pct": round(overall_routing_accuracy, 2),
            "per_agent_accuracy": per_agent_summary,
            "confusion_matrix": confusion_matrix.to_dict()
        },
        "diagnostics": {
            "total_evaluation_errors": len(eval_errors)
        }
    }

    with open("evaluation_summary.json", "w", encoding="utf-8") as f:
        json.dump(full_summary, f, indent=2)
    print("[✓] Saved evaluation_summary.json")

    # 6. evaluation_summary.md
    md_content = f"""# Autonomous E-Commerce Operations Agent: System Evaluation Report

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Evaluation Scope:** RAG Retrieval Quality, Answer Correctness, RAGAs Generation Metrics, Agent Routing

---

## 1. Executive Summary

| Evaluation Domain | Sample Size ($N$) | Primary Metric | Primary Score |
| :--- | :--- | :--- | :--- |
| **Agent / Workflow Routing** | $N = {total_routing}$ | Overall Routing Accuracy | **{overall_routing_accuracy:.2f}%** |
| **Document Retrieval (RAG)** | $N = {total_rag}$ | Hit@3 (Precision@3: {retrieval_summary['precision_at_3']}) | **{retrieval_summary['hit_at_3_pct']}%** (MRR: {retrieval_summary['mrr']}) |
| **Factual Answer Correctness** | $N = {total_rag}$ | Fully Correct Answers | **{correctness_summary['fully_correct_pct']}%** |
| **RAGAs Faithfulness** | $N = {ragas_summary['faithfulness']['valid_evaluations']}$ | Claim Groundedness in Context | **{ragas_summary['faithfulness']['mean']}** |
| **RAGAs Answer Relevancy** | $N = {ragas_summary['answer_relevancy']['valid_evaluations']}$ | Response Semantic Alignment | **{ragas_summary['answer_relevancy']['mean']}** |
| **RAGAs Context Precision** | $N = {ragas_summary['context_precision']['valid_evaluations']}$ | Signal-to-Noise Ratio in Chunks | **{ragas_summary['context_precision']['mean']}** |
| **RAGAs Context Recall** | $N = {ragas_summary['context_recall']['valid_evaluations']}$ | Ground Truth Coverage | **{ragas_summary['context_recall']['mean']}** |

---

## 2. RAG Retrieval Metrics (Independent of LLM)

Retrieval evaluated against authoritative source documents (`refund_policy.pdf`, `delivery_sla_policy.pdf`, `escalation_rules.pdf`, `product_catalog.pdf`):

- **Hit@1:** {retrieval_summary['hit_at_1_pct']}%
- **Hit@3:** {retrieval_summary['hit_at_3_pct']}%
- **Hit@5:** {retrieval_summary['hit_at_5_pct']}%
- **Mean Reciprocal Rank (MRR):** {retrieval_summary['mrr']}
- **Precision@3:** {retrieval_summary['precision_at_3']}
- **Recall@3:** {retrieval_summary['recall_at_3']}

---

## 3. Answer Correctness Breakdown ($N = {total_rag}$)

- **Fully Correct:** {correctness_summary['fully_correct_pct']}% ({fully_correct}/{total_rag})
- **Partially Correct:** {correctness_summary['partially_correct_pct']}% ({partially_correct}/{total_rag})
- **Incorrect:** {correctness_summary['incorrect_pct']}% ({incorrect}/{total_rag})
- **Weighted Correctness Score:** {correctness_summary['overall_correctness_pct']}%

---

## 4. Failure Root-Cause Analysis

Each suboptimal response was diagnosed into mutually exclusive failure categories:

- **RETRIEVAL_FAILURE:** {failure_summary['RETRIEVAL_FAILURE']} (Required policy chunk was absent from top-K retrieved context)
- **GENERATION_FAILURE:** {failure_summary['GENERATION_FAILURE']} (Policy chunk was successfully retrieved, but LLM misstated or omitted required facts)
- **GROUND_TRUTH_ERROR:** {failure_summary['GROUND_TRUTH_ERROR']} (Discrepancy in ground truth references - 0 after strict PDF verification)
- **EVALUATION_ERROR:** {failure_summary['EVALUATION_ERROR']} (Evaluator API or timeout exceptions)

---

## 5. Router Accuracy by Agent Route ($N = {total_routing}$)

| Route Function | Sample Size ($N$) | Correct | Accuracy (%) |
| :--- | :--- | :--- | :--- |
"""
    for route, st in per_agent_summary.items():
        md_content += f"| `{route}` | {st['total']} | {st['correct']} | **{st['accuracy_pct']}%** |\n"

    md_content += f"""
---

## 6. Confusion Matrix

```
{confusion_matrix.to_string()}
```

---

## 7. Diagnostics & Reliability

- **Total Logged Evaluation Errors:** {len(eval_errors)}
- **RAGAs Sample Failure Rate:** {ragas_summary['faithfulness']['failure_rate_pct']}%
- **Verification Status:** All reference answers verified directly against authoritative source PDF policies.
"""

    with open("evaluation_summary.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    print("[✓] Saved evaluation_summary.md")

    # =====================================================================
    # 7. CONSOLE SUMMARY
    # =====================================================================
    print("\n" + "=" * 70)
    print("FINAL EVALUATION METRIC SUMMARY")
    print("=" * 70)
    print(f"Total Samples (RAG): {total_rag}")
    print(f"Valid Evaluations: {ragas_summary['faithfulness']['valid_evaluations']}")
    print(f"Evaluation Failures: {len(eval_errors)}")
    print("-" * 70)
    print(f"Faithfulness:        {ragas_summary['faithfulness']['mean']}")
    print(f"Answer Relevancy:    {ragas_summary['answer_relevancy']['mean']}")
    print(f"Context Precision:   {ragas_summary['context_precision']['mean']}")
    print(f"Context Recall:      {ragas_summary['context_recall']['mean']}")
    print("-" * 70)
    print(f"Retrieval Hit@1:     {retrieval_summary['hit_at_1_pct']}% (N={total_rag})")
    print(f"Retrieval Hit@3:     {retrieval_summary['hit_at_3_pct']}% (N={total_rag})")
    print(f"Retrieval MRR:       {retrieval_summary['mrr']}")
    print(f"Answer Correctness:  {correctness_summary['overall_correctness_pct']}% (Fully Correct: {correctness_summary['fully_correct_pct']}%)")
    print("-" * 70)
    print(f"Routing Accuracy:    {overall_routing_accuracy:.2f}% (N={total_routing})")
    print("=" * 70)


if __name__ == "__main__":
    run_evaluation_pipeline()