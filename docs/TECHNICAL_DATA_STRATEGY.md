# Technical Data Strategy: SUPAA Custom Model (EN-JP Tutor)

## 1. Overview
This document defines the data strategy for developing and improving the SUPAA proprietary models, specifically focusing on the fine-tuning of Gemma4 for pedagogical language instruction in the English-Japanese (EN-JP) domain.

## 2. Data Lifecycle

### 2.1. Collection (Data Flywheel)
We capture high-quality interaction trajectories from the SUPAA Tutor platform.
- **Source:** Real student interactions and pedagogical feedback loops.
- **Format:** JSONL trajectories containing conversational messages, vocabulary lookups, and grammar corrections.
- **Metadata:** Success/failure labels, user retention metrics, and execution metrics (latency).

### 2.2. Synthetic Data Generation
To bootstrap performance in specific grammar or vocabulary tasks, we use a "Teacher-Student" distillation approach.
- **Teacher Models:** GPT-4o, Claude 3.5 Sonnet.
- **Goal:** Generate complex language teaching scenarios covering JLPT N5 to N1 levels.
- **Implementation Script:** `scripts/generate_teaching_data.py`
- **Filtering:** Automated validation to ensure synthetic data quality.

### 2.3. Processing & Labeling
- **Reasoning Extraction:** Using larger models to retroactively "reason" over successful pedagogical interventions to create COT (Chain of Thought) training pairs.
- **DPO Pairing:** Creating preference pairs (win/loss) based on student comprehension feedback.

## 3. Use-Case Examples for Custom Model

### 3.1. Pedagogical Correction
- **Scenario:** A student makes a grammatical error in Japanese. The Tutor must identify it and explain it clearly without giving away the answer immediately.
- **Training Goal:** Minimize direct answers, maximize guided discovery.
- **Data Example:**
  - `Input`: "I eat apple. -> 私はりんご食べる。"
  - `Output`: Reasoning map indicating the missing particle 'を' + specific tool calls or guided questions to prompt the student.

## 4. Technical Architecture
- **Storage:** GCP BigQuery for structured telemetry; GCS for raw JSONL trajectories.
- **Training Pipeline:** Automated fine-tuning runs on compute instances using `scripts/finetune_gemma.py` and `scripts/gemma4_adapter.py`.
- **Evaluation:** Benchmarked on standard NLP tasks and custom pedagogical efficacy suites via `scripts/gemma4_evaluation.py`.

## 5. Privacy & Security
- **Anonymization:** Mandatory PII stripping from all student data.
- **Sovereignty:** All data remains within the `super-power-agents` GCP perimeter.
- **Consent:** Clear user opt-in for data usage in model improvement.

## 6. Technical End-Goals (Metrics)
To ensure the Tutor model meets production standards, we target the following metrics:
- **Pedagogical Accuracy:** >95% accuracy in grammar identification.
- **Inference Latency:** < 300ms total latency for real-time conversational flow.
