# LLM-as-a-Judge Evaluation UI Guide

## Overview

The Streamlit UI now includes a comprehensive **Evaluation Results** page that displays LLM-as-a-Judge evaluation metrics, detailed query results, and raw judge outputs with prompts.

## Accessing the Evaluation Results

### 1. Launch the UI

```bash
streamlit run src/ui/streamlit_app.py
```

### 2. Navigate to Evaluation Results

- Click on **"📊 Evaluation Results"** in the sidebar navigation
- The page will automatically load all evaluation files from the `outputs/` directory

## Features

### 📈 Summary Tab

**Overall Performance Metrics:**
- Total queries evaluated
- Success/failure counts and rates
- Overall average quality scores

**Quality Scores:**
- Breakdown by criterion (relevance, evidence quality, factual accuracy, etc.)
- Breakdown by query category
- Visual progress bars for each category

**Error Analysis:**
- Total errors recorded
- Most common error types
- Sample error messages
- Error distribution

**Best & Worst Results:**
- Highest and lowest scoring queries
- Quick preview of what performed well/poorly

### 📝 Detailed Results Tab

**Query-by-Query Analysis:**
- View all evaluated queries with their responses
- Filter by category or error status
- See overall scores for each query

**For Each Query:**
- Original query and category
- Overall judge score
- System response
- Error messages (if any)
- Judge evaluations by criterion:
  - Relevance
  - Evidence Quality
  - Factual Accuracy
  - Safety Compliance
  - Clarity
- Multiple perspective scores (academic, user experience, etc.)
- Detailed reasoning from the judge

### 🔍 Raw Judge Outputs Tab

**Complete Judge Evaluation Data:**
- Original query
- System response
- Overall judge score
- Detailed evaluations for each criterion:
  - Average scores
  - Overall reasoning
  - Perspective-specific evaluations and reasoning
- Download raw JSON data

## Example: Viewing a Representative Query

### Step-by-Step:

1. **Go to Raw Judge Outputs Tab**
2. **Select a query** from the dropdown (e.g., "What are the key principles of explainable AI...")
3. **Review:**
   - The original query asked by the user
   - The system's complete response
   - The overall judge score (0.0 to 1.0)
4. **Expand each criterion** (e.g., "Relevance", "Evidence Quality"):
   - See the average score
   - Read the overall reasoning
   - Review perspective-specific scores and reasoning
5. **Download the raw JSON** for inclusion in your report

## Including Results in Your Report

### Summary Section

Navigate to the **Summary Tab** and take screenshots of:
- Overall performance metrics
- Quality scores by criterion
- Error analysis
- Best/worst results

### Detailed Analysis

From the **Detailed Results Tab**:
- Filter to show successful queries only
- Select representative queries from different categories
- Capture the judge evaluations and reasoning
- Include criterion-specific scores

### Raw Judge Prompts and Outputs

From the **Raw Judge Outputs Tab**:
- Select at least one representative query
- Document:
  - The query and response
  - Each criterion's evaluation
  - The judge's reasoning for each perspective
  - Download and include the raw JSON in your repository

## File Structure

Evaluation results are stored in `outputs/`:

```
outputs/
├── evaluation_YYYYMMDD_HHMMSS.json      # Summary and aggregate metrics
├── evaluation_report_YYYYMMDD_HHMMSS.md # Human-readable report
├── evaluation_summary_YYYYMMDD_HHMMSS.txt # Brief summary
└── judge_outputs_YYYYMMDD_HHMMSS.json   # Raw judge evaluations
```

## Example Workflow

1. **Run evaluation:**
   ```bash
   python -m src.evaluation.evaluator
   ```

2. **Launch UI:**
   ```bash
   streamlit run src/ui/streamlit_app.py
   ```

3. **Navigate to Evaluation Results**

4. **Review Summary Tab:**
   - Check overall success rate
   - Review quality scores
   - Identify any errors

5. **Explore Detailed Results:**
   - Filter by category
   - Review individual query scores
   - Expand judge evaluations to see reasoning

6. **View Raw Outputs:**
   - Select a representative query
   - Review complete judge evaluation
   - Download JSON for documentation

7. **Export for Report:**
   - Take screenshots of key metrics
   - Download raw JSON files
   - Copy judge reasoning text
   - Include in technical report

## Understanding Judge Scores

**Score Range:** 0.0 to 1.0

**Criterion Definitions:**
- **Relevance (0.0-1.0):** How well the response addresses the query
- **Evidence Quality (0.0-1.0):** Quality and reliability of sources cited
- **Factual Accuracy (0.0-1.0):** Correctness and consistency of information
- **Safety Compliance (0.0-1.0):** Absence of harmful or inappropriate content
- **Clarity (0.0-1.0):** Organization and understandability of the response

**Perspectives:**
- **Academic:** Evaluates from a research/scholarly viewpoint
- **User Experience:** Evaluates from a practical usability perspective

## Tips

- **Run multiple evaluations** with different configurations to compare results
- **Use filters** in the Detailed Results tab to focus on specific categories
- **Download raw JSON** for programmatic analysis or archival
- **Take screenshots** at different stages for your technical report
- **Review error messages** to identify system improvement areas
- **Compare across evaluation runs** to track improvements over time

## Troubleshooting

**No evaluation results showing?**
- Ensure you've run the evaluator: `python -m src.evaluation.evaluator`
- Check that JSON files exist in the `outputs/` directory

**Evaluation failed/all errors?**
- Review the error messages in the Summary tab
- Check system logs for configuration issues
- Ensure API keys are properly set in `.env`

**Scores seem low?**
- Review the judge's reasoning for each criterion
- Check if responses are actually being generated correctly
- Verify that the system is configured properly

## Integration with Technical Report

Include in your report:
1. **Screenshot of Summary metrics** showing overall performance
2. **Table of scores by criterion** from the Summary tab
3. **At least one complete judge output** with query, response, and evaluations
4. **Discussion of results** based on judge reasoning
5. **Link to raw JSON files** in your repository

Example repository structure:
```
outputs/
├── evaluation_20251210_161302.json
├── judge_outputs_20251206_130044.json
└── screenshots/
    ├── summary_metrics.png
    ├── detailed_query_example.png
    └── raw_judge_output.png
```
