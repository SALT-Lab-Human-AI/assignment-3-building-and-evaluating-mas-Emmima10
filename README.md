[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/r1tAQ0HC)

# Multi-Agent Research System - Assignment 3

A multi-agent system for deep research on HCI topics, featuring orchestrated agents, safety guardrails, and LLM-as-a-Judge evaluation.
## Demo Videos

### 1. Multi Agent
A short walkthrough of the multi-agent system and its interactions.  
Watch: [Multi Agent Demo](https://drive.google.com/file/d/1kfWyUvoks8Mog5NVmy-8FHEcWnlfXPan/view?usp=sharing)

### 2. Safety
Demonstration of safety features and failure cases.  
Watch: [Safety Demo](https://drive.google.com/file/d/1bhE4FRKHtjSPo2JSIcTSmKi6z42TcTov/view?usp=sharing)

### 3. LLM as a Judge
Example of using an LLM to adjudicate and score inputs.  
Watch: [LLM as a Judge Demo](https://drive.google.com/file/d/1TDw9Bhk32qgYwy5x2ksdP5tkxVOTBXyF/view?usp=sharing)


## Overview

This template provides a starting point for building a multi-agent research assistant system. The system uses multiple specialized agents to:
- Plan research tasks
- Gather evidence from academic papers and web sources
- Synthesize findings into coherent responses
- Evaluate quality and verify accuracy
- Ensure safety through guardrails

## Project Structure

```
.
├── src/
│   ├── agents/              # Agent implementations
│   │   ├── base_agent.py    # Base agent class
│   │   ├── planner_agent.py # Task planning agent
│   │   ├── researcher_agent.py # Evidence gathering agent
│   │   ├── critic_agent.py  # Quality verification agent
│   │   └── writer_agent.py  # Response synthesis agent
│   ├── guardrails/          # Safety guardrails
│   │   ├── safety_manager.py # Main safety coordinator
│   │   ├── input_guardrail.py # Input validation
│   │   └── output_guardrail.py # Output validation
│   ├── tools/               # Research tools
│   │   ├── web_search.py    # Web search integration
│   │   ├── paper_search.py  # Academic paper search
│   │   └── citation_tool.py # Citation formatting
│   ├── evaluation/          # Evaluation system
│   │   ├── judge.py         # LLM-as-a-Judge implementation
│   │   └── evaluator.py     # System evaluator
│   ├── ui/                  # User interfaces
│   │   ├── cli.py           # Command-line interface
│   │   └── streamlit_app.py # Web interface
│   └── orchestrator.py      # Agent orchestration
├── data/
│   └── example_queries.json # Example test queries
├── logs/                    # Log files (created at runtime)
├── outputs/                 # Evaluation results (created at runtime)
├── config.yaml              # System configuration
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── main.py                 # Main entry point
```

## Setup Instructions

### 1. Prerequisites

- Python 3.9 or higher
- `uv` package manager (recommended) or `pip`
- Virtual environment

### 2. Installation

#### Installing uv (Recommended)

`uv` is a fast Python package installer and resolver. Install it first:

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Alternative: Using pip
pip install uv
```

#### Setting up the Project

Clone the repository and navigate to the project directory:

```bash
cd is-492-assignment-3
```

**Option A: Using uv (Recommended - Much Faster)**

```bash
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate     # On Windows

# Install dependencies
uv pip install -r requirements.txt
```

**Option B: Using standard pip**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate   # On macOS/Linux
# OR
venv\Scripts\activate      # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Security Setup (Important!)

**Before committing any code**, set up pre-commit hooks to prevent API key leaks:

```bash
# Quick setup - installs hooks and runs security checks
./scripts/install-hooks.sh

# Or manually
pre-commit install
```

This will automatically scan for hardcoded API keys and secrets before each commit. See `SECURITY_SETUP.md` for full details.

### 4. API Keys Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
# Required: At least one LLM API
GROQ_API_KEY=your_groq_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here

# Recommended: At least one search API
TAVILY_API_KEY=your_tavily_api_key_here
# OR
BRAVE_API_KEY=your_brave_api_key_here

# Optional: For academic paper search
SEMANTIC_SCHOLAR_API_KEY=your_key_here
```

#### Getting API Keys

- **Groq** (Recommended for students): [https://console.groq.com](https://console.groq.com) - Free tier available
- **OpenAI**: [https://platform.openai.com](https://platform.openai.com) - Paid, requires credits
- **Tavily**: [https://www.tavily.com](https://www.tavily.com) - Student free quota available
- **Brave Search**: [https://brave.com/search/api](https://brave.com/search/api)
- **Semantic Scholar**: [https://www.semanticscholar.org/product/api](https://www.semanticscholar.org/product/api) - Free tier available

### 5. Configuration

Edit `config.yaml` to customize your system:

- Choose your research topic
- **Configure agent prompts** (see below)
- Set model preferences (Groq vs OpenAI)
- Define safety policies
- Configure evaluation criteria

#### Customizing Agent Prompts

You can customize agent behavior by setting the `system_prompt` in `config.yaml`:

```yaml
agents:
  planner:
    system_prompt: |
      You are an expert research planner specializing in HCI.
      Focus on recent publications and seminal works.
      After creating the plan, say "PLAN COMPLETE".
```

**Important**: Custom prompts must include handoff signals:
- **Planner**: Must include `"PLAN COMPLETE"`
- **Researcher**: Must include `"RESEARCH COMPLETE"`  
- **Writer**: Must include `"DRAFT COMPLETE"`
- **Critic**: Must include `"APPROVED - RESEARCH COMPLETE"` or `"NEEDS REVISION"`

Leave `system_prompt: ""` (empty) to use the default prompts.

## Implementation Guide

This template provides the structure - you need to implement the core functionality. Here's what needs to be done:

### Phase 1: Core Agent Implementation

1. **Implement Agent Logic** (in `src/agents/`)
   - [ ] Complete `planner_agent.py` - Integrate LLM to break down queries
   - [ ] Complete `researcher_agent.py` - Integrate search APIs (Tavily, Semantic Scholar)
   - [ ] Complete `critic_agent.py` - Implement quality evaluation logic
   - [ ] Complete `writer_agent.py` - Implement synthesis with proper citations

2. **Implement Tools** (in `src/tools/`)
   - [ ] Complete `web_search.py` - Integrate Tavily or Brave API
   - [ ] Complete `paper_search.py` - Integrate Semantic Scholar API
   - [ ] Complete `citation_tool.py` - Implement APA citation formatting

### Phase 2: Orchestration

Choose your preferred framework to implement the multi-agent system. The current assignment template code uses AutoGen, but you can also choose to use other frameworks as you prefer (e.g., LangGraph and Crew.ai).


3. **Update `orchestrator.py`**
   - Integrate your chosen framework
   - Implement the workflow: plan → research → write → critique → revise
   - Add error handling

### Phase 3: Safety Guardrails

4. **Implement Guardrails** (in `src/guardrails/`)
   - [ ] Choose framework: Guardrails AI or NeMo Guardrails
   - [ ] Define safety policies in `safety_manager.py`
   - [ ] Implement input validation in `input_guardrail.py`
   - [ ] Implement output validation in `output_guardrail.py`
   - [ ] Set up safety event logging

### Phase 4: Evaluation

5. **Implement LLM-as-a-Judge** (in `src/evaluation/`)
   - [ ] Complete `judge.py` - Integrate LLM API for judging
   - [ ] Define evaluation rubrics for each criterion
   - [ ] Implement score parsing and aggregation

6. **Create Test Dataset**
   - [ ] Add more test queries to `data/example_queries.json`
   - [ ] Define expected outputs or ground truths where possible
   - [ ] Cover different query types and topics

### Phase 5: User Interface

7. **Complete UI** (choose one or both)
   - [ ] Finish CLI implementation in `src/ui/cli.py`
   - [ ] Finish web UI in `src/ui/streamlit_app.py`
   - [ ] Display agent traces clearly
   - [ ] Show citations and sources
   - [ ] Indicate safety events

## Running the System

### Command Line Interface

```bash
python main.py --mode cli
```

### Web Interface

```bash
python main.py --mode web
# OR directly:
streamlit run src/ui/streamlit_app.py
```

The web interface includes:
- **Home Page**: Interactive query interface with agent traces, citations, and safety events
- **📊 Evaluation Results**: Comprehensive dashboard for LLM-as-a-Judge evaluation metrics
  - Summary view with overall performance metrics
  - Detailed query-by-query results
  - Raw judge outputs with complete prompts and reasoning

**Viewing Evaluation Results:**
1. Run evaluations first: `python -m src.evaluation.evaluator`
2. Launch the UI: `streamlit run src/ui/streamlit_app.py`
3. Navigate to "📊 Evaluation Results" in the sidebar
4. Explore the three tabs: Summary, Detailed Results, and Raw Judge Outputs

See [`EVALUATION_UI_GUIDE.md`](EVALUATION_UI_GUIDE.md) for detailed instructions on using the evaluation UI.

### Running Evaluation

```bash
python main.py --mode evaluate
```

This will:
- Load test queries from `data/example_queries.json`
- Run each query through your system
- Evaluate outputs using LLM-as-a-Judge
- Generate report in `outputs/`

## Testing

Run tests (if you create them):

```bash
pytest tests/
```

## Reproducing Evaluation Results

This section provides step-by-step instructions to reproduce the results reported in the technical report (`TECHNICAL_REPORT.md`).

### Prerequisites for Reproduction

Ensure you have completed the setup steps above, specifically:
- ✅ Python environment activated
- ✅ All dependencies installed
- ✅ API keys configured in `.env` file
- ✅ `config.yaml` matches the evaluation configuration

### Exact Configuration Used

The evaluation results in the technical report were generated with the following configuration:

**Model Configuration:**
```yaml
models:
  default:
    provider: "openai"
    name: "gpt-4o-mini"
    temperature: 0.7
    max_tokens: 512
  judge:
    provider: "openai"
    name: "gpt-4o-mini"
    temperature: 0.3
    max_tokens: 256
```

**Tool Configuration:**
```yaml
tools:
  web_search:
    enabled: true
    provider: "tavily"
    max_results: 3
  paper_search:
    enabled: true
    provider: "semantic_scholar"
    max_results: 5
```

**Safety Configuration:**
```yaml
safety:
  enabled: true
  framework: "guardrails"
  log_events: true
```

**Evaluation Configuration:**
```yaml
evaluation:
  enabled: true
  num_test_queries: 6
  criteria:
    - name: "relevance"
      weight: 0.25
    - name: "evidence_quality"
      weight: 0.25
    - name: "factual_accuracy"
      weight: 0.20
    - name: "safety_compliance"
      weight: 0.15
    - name: "clarity"
      weight: 0.15
```

### Step-by-Step Reproduction

#### Step 1: Verify Configuration

Ensure your `config.yaml` matches the configuration above:

```bash
# View current configuration
cat config.yaml  # On macOS/Linux
type config.yaml  # On Windows
```

#### Step 2: Verify Test Queries

The evaluation uses 6 queries from `data/example_queries.json`:

1. "What are the key principles of explainable AI for novice users?"
2. "How has AR usability evolved in the past 5 years?"
3. "What are ethical considerations in using AI for education?"
4. "Compare different approaches to measuring user experience in mobile applications"
5. "What are the latest developments in conversational AI for healthcare?"
6. "How do design patterns for accessibility differ across web and mobile platforms?"

Verify the file exists:
```bash
# Check test queries
cat data/example_queries.json  # On macOS/Linux
type data\example_queries.json  # On Windows
```

#### Step 3: Run Complete Evaluation

Execute the full evaluation pipeline:

```bash
python main.py --mode evaluate
```

**Expected Behavior:**
- Initializes AutoGen orchestrator
- Initializes SystemEvaluator
- Processes 6 queries sequentially (~10-15 minutes total)
- Each query goes through: Plan → Research → Write → Critique → Final Response
- LLM-as-judge evaluates each response
- Generates comprehensive reports

**What You'll See:**
```
======================================================================
RUNNING FULL SYSTEM EVALUATION
======================================================================

This will evaluate the system on test queries from data/example_queries.json
Evaluation results will be saved to outputs/

Processing Query 1/6: What are the key principles of explainable AI...
[Agent conversation logs]
Evaluating response...
Score: 0.750

Processing Query 2/6: How has AR usability evolved...
...

======================================================================
EVALUATION SUMMARY
======================================================================

Total Queries: 6
Successful: 6
Failed: 0
Success Rate: 100.00%

Overall Average Score: 0.724

Scores by Criterion:
  relevance: 0.850
  evidence_quality: 0.442
  factual_accuracy: 0.750
  safety_compliance: 1.000
  clarity: 0.675
```

#### Step 4: Locate Output Files

After evaluation completes, check the `outputs/` directory:

```bash
ls -lh outputs/  # On macOS/Linux
dir outputs\     # On Windows
```

**Generated Files (with timestamp):**
- `evaluation_YYYYMMDD_HHMMSS.json` - Detailed evaluation results (JSON format)
- `evaluation_report_YYYYMMDD_HHMMSS.md` - Human-readable markdown report
- `evaluation_summary_YYYYMMDD_HHMMSS.txt` - Quick summary text file

**Example:**
```
outputs/
├── evaluation_20251210_085149.json
├── evaluation_report_20251210_085149.md
└── evaluation_summary_20251210_085149.txt
```

#### Step 5: Verify Results

Compare your results with the reported values in `TECHNICAL_REPORT.md`:

**Expected Key Metrics:**
- Overall Average Score: **0.724** (±0.02 due to LLM variance)
- Success Rate: **100%** (6/6 queries)
- Safety Compliance: **1.000** (perfect)
- Relevance: **0.850** (±0.05)
- Evidence Quality: **0.442** (±0.08)
- Factual Accuracy: **0.750** (±0.05)
- Clarity: **0.675** (±0.05)

**View Detailed Results:**
```bash
# Quick summary
cat outputs/evaluation_summary_*.txt | tail -n 30

# Full report
cat outputs/evaluation_report_*.md

# JSON data (for analysis)
python -m json.tool outputs/evaluation_*.json | less
```

### Expected Variations

Due to the non-deterministic nature of LLMs, you may observe slight variations:

**Normal Variance:**
- Overall score: ±2-3% (e.g., 0.71-0.74 instead of 0.724)
- Individual criterion scores: ±5%
- Response length and phrasing will differ
- Source selection may vary

**Consistent Aspects:**
- Success rate should remain 100%
- Safety compliance should remain 1.000
- Query processing should complete without errors
- Evidence quality will likely be the weakest criterion
- Relevance and safety should be the strongest criteria

### Testing Safety Guardrails

To verify the safety guardrails are working as reported:

```bash
python test_safety.py
```

**Expected Output:**
```
======================================================================
TESTING SAFETY GUARDRAILS
======================================================================

1. Initializing SafetyManager...
✓ SafetyManager initialized successfully
  - Enabled: True
  - LLM Client: OpenAI
  - Topic: HCI Research

2. Testing SAFE input...
  Result: ✓ SAFE

3. Testing HARMFUL input...
  Result: ✗ UNSAFE (Expected)
  Violations found: 1

4. Testing PROMPT INJECTION...
  Result: ✗ UNSAFE (Expected)
  Violations found: 1

5. Testing OFF-TOPIC input...
  Result: ✗ UNSAFE (Expected - off-topic)
  Violations found: 1

6. Testing OUTPUT with PII...
  Result: ✗ UNSAFE (Expected - contains PII)
  Violations found: 3
```

### Troubleshooting Reproduction Issues

**Issue: Lower success rate than reported**
- Check API key validity (`OPENAI_API_KEY` in `.env`)
- Verify internet connectivity for API calls
- Check API rate limits/quotas
- Review error messages in output files

**Issue: Different scores**
- Verify `config.yaml` matches the configuration above
- Check model configuration (should be gpt-4o-mini)
- Ensure judge temperature is 0.3 (lower = more consistent)
- Note: ±5% variation is normal due to LLM non-determinism

**Issue: Evaluation hangs/times out**
- Check timeout setting in config (should be 180 seconds)
- Verify API response times
- Check network connection
- Review logs in `logs/system.log`

**Issue: API errors**
- Verify all required API keys are set
- Check API quota/rate limits
- Try with reduced `num_test_queries` (e.g., 3 instead of 6)
- Ensure APIs are accessible from your network

**Issue: Safety tests fail**
- Ensure `safety.enabled: true` in `config.yaml`
- Verify LLM client is initialized (should show "OpenAI")
- Check that `OPENAI_API_KEY` is valid
- Review `logs/safety_events.log`

### Analyzing Results

#### View Summary Statistics

```bash
# On Linux/macOS
grep -A 20 "EVALUATION SUMMARY" outputs/evaluation_summary_*.txt

# On Windows PowerShell
Select-String -Path outputs\evaluation_summary_*.txt -Pattern "EVALUATION SUMMARY" -Context 0,20
```

#### Extract Specific Metrics

```python
# Quick Python script to analyze results
import json

with open('outputs/evaluation_20251210_085149.json', 'r') as f:
    data = json.load(f)

print(f"Overall Score: {data['scores']['overall_average']:.3f}")
print(f"Success Rate: {data['summary']['success_rate']:.1%}")
print("\nScores by Criterion:")
for criterion, score in data['scores']['by_criterion'].items():
    print(f"  {criterion}: {score:.3f}")
```

#### Compare with Technical Report

The `TECHNICAL_REPORT.md` contains detailed analysis sections that should align with your results:
- Section 3.3: Overall Performance (should match)
- Section 3.4: Safety Evaluation (should be 100% compliance)
- Section 3.5: Error Analysis (should show 0 errors)
- Section 3.6: Performance Metrics

### Additional Testing

#### Test Single Query (Quick Validation)

```bash
python test_query.py
```

This runs a single query to verify the system is working before full evaluation.

#### Test Web Interface

```bash
streamlit run src/ui/streamlit_app.py
```

Then navigate to http://localhost:8501 and test interactively:
1. Try a safe HCI query
2. Try an unsafe query to test guardrails
3. View safety events in the sidebar
4. Check agent traces

### Version Information

The reported results were generated with:
- Python: 3.11+
- OpenAI API: gpt-4o-mini model
- AutoGen: 0.2.x
- Key dependencies: See `requirements.txt`

To ensure exact reproduction, use the same versions:
```bash
pip freeze > my_environment.txt
diff requirements.txt my_environment.txt
```

## Resources

### Documentation
- [uv Documentation](https://docs.astral.sh/uv/) - Fast Python package installer
- [AutoGen Documentation](https://microsoft.github.io/autogen/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Guardrails AI](https://docs.guardrailsai.com/)
- [NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/)
- [Tavily API](https://docs.tavily.com/)
- [Semantic Scholar API](https://api.semanticscholar.org/)
