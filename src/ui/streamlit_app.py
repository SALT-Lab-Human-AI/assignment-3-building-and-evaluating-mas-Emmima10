"""
Streamlit Web Interface
Web UI for the multi-agent research system.

Run with: streamlit run src/ui/streamlit_app.py
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import yaml
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

from src.autogen_orchestrator import AutoGenOrchestrator

# Load environment variables
load_dotenv()


def load_config():
    """Load configuration file."""
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}


def initialize_session_state():
    """Initialize Streamlit session state."""
    if 'history' not in st.session_state:
        st.session_state.history = []

    if 'orchestrator' not in st.session_state:
        config = load_config()
        # Initialize AutoGen orchestrator
        try:
            st.session_state.orchestrator = AutoGenOrchestrator(config)
        except Exception as e:
            st.error(f"Failed to initialize orchestrator: {e}")
            st.session_state.orchestrator = None

    if 'show_traces' not in st.session_state:
        st.session_state.show_traces = False

    if 'show_safety_log' not in st.session_state:
        st.session_state.show_safety_log = False


def process_query(query: str, max_rounds: int = 10) -> Dict[str, Any]:
    """
    Process a query through the orchestrator.
    
    Args:
        query: Research query to process
        
    Returns:
        Result dictionary with response, citations, and metadata
    """
    orchestrator = st.session_state.orchestrator
    
    if orchestrator is None:
        return {
            "query": query,
            "error": "Orchestrator not initialized",
            "response": "Error: System not properly initialized. Please check your configuration.",
            "citations": [],
            "metadata": {}
        }
    
    try:
        # Process query through AutoGen orchestrator (synchronous)
        # Use reduced max_rounds for faster processing
        result = orchestrator.process_query(query, max_rounds=max_rounds)
        
        # Check for errors
        if "error" in result:
            return result
        
        # Extract citations from conversation history
        citations = extract_citations(result)
        
        # Extract agent traces for display
        agent_traces = extract_agent_traces(result)
        
        # Format metadata
        metadata = result.get("metadata", {})
        metadata["agent_traces"] = agent_traces
        metadata["citations"] = citations
        metadata["critique_score"] = calculate_quality_score(result)
        
        # Extract safety events
        safety_events = result.get("safety_events", [])
        metadata["safety_events"] = safety_events
        
        return {
            "query": query,
            "response": result.get("response", ""),
            "citations": citations,
            "metadata": metadata,
            "safety_events": safety_events
        }
        
    except Exception as e:
        return {
            "query": query,
            "error": str(e),
            "response": f"An error occurred: {str(e)}",
            "citations": [],
            "metadata": {"error": True}
        }


def extract_citations(result: Dict[str, Any]) -> list:
    """Extract citations from research result with better formatting."""
    citations = []
    seen_urls = set()
    
    # Look through conversation history for citations
    for msg in result.get("conversation_history", []):
        content = msg.get("content", "")
        
        # Ensure content is a string (handle cases where it might be a list or other type)
        if isinstance(content, list):
            content = " ".join(str(item) for item in content)
        elif not isinstance(content, str):
            content = str(content) if content else ""
        
        # Find URLs in content
        import re
        urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', content)
        
        # Find citation patterns like [Source: Title] or (Author, Year)
        citation_patterns = re.findall(r'\[Source: ([^\]]+)\]', content)
        apa_patterns = re.findall(r'\(([A-Z][a-z]+(?:\s+et\s+al\.)?,\s+\d{4})\)', content)
        
        for url in urls:
            if url not in seen_urls:
                seen_urls.add(url)
                citations.append({
                    "type": "url",
                    "content": url,
                    "display": url
                })
        
        for citation in citation_patterns:
            if citation not in [c.get("content", "") for c in citations]:
                citations.append({
                    "type": "source",
                    "content": citation,
                    "display": citation
                })
        
        for apa_cite in apa_patterns:
            if apa_cite not in [c.get("content", "") for c in citations]:
                citations.append({
                    "type": "apa",
                    "content": apa_cite,
                    "display": f"({apa_cite})"
                })
    
    return citations[:15]  # Limit to top 15


def extract_agent_traces(result: Dict[str, Any]) -> Dict[str, list]:
    """Extract agent execution traces from conversation history."""
    traces = {}
    
    for msg in result.get("conversation_history", []):
        agent = msg.get("source", "Unknown")
        content = msg.get("content", "")
        
        # Ensure content is a string
        if isinstance(content, list):
            content = " ".join(str(item) for item in content)
        elif not isinstance(content, str):
            content = str(content) if content else ""
        
        content = content[:200]  # First 200 chars
        
        if agent not in traces:
            traces[agent] = []
        
        traces[agent].append({
            "action_type": "message",
            "details": content
        })
    
    return traces


def calculate_quality_score(result: Dict[str, Any]) -> float:
    """Calculate a quality score based on various factors."""
    score = 5.0  # Base score
    
    metadata = result.get("metadata", {})
    
    # Add points for sources
    num_sources = metadata.get("num_sources", 0)
    score += min(num_sources * 0.5, 2.0)
    
    # Add points for critique
    if metadata.get("critique"):
        score += 1.0
    
    # Add points for conversation length (indicates thorough discussion)
    num_messages = metadata.get("num_messages", 0)
    score += min(num_messages * 0.1, 2.0)
    
    return min(score, 10.0)  # Cap at 10


def display_response(result: Dict[str, Any]):
    """
    Display query response with enhanced formatting, citations, and safety events.
    """
    # Check for errors
    if "error" in result:
        st.error(f"Error: {result['error']}")
        return

    # Check for safety blocking
    metadata = result.get("metadata", {})
    safety_events = result.get("safety_events", [])
    
    if metadata.get("safety_blocked"):
        st.error("⚠️ **Response Blocked by Safety System**")
        violations = metadata.get("safety_violations", [])
        for violation in violations:
            st.warning(f"  • {violation.get('reason', 'Unknown violation')} (Severity: {violation.get('severity', 'unknown')})")
        return

    # Display response
    st.markdown("### Response")
    response = result.get("response", "")
    
    # Ensure response is a string
    if isinstance(response, list):
        response = " ".join(str(item) for item in response)
    elif not isinstance(response, str):
        response = str(response) if response else ""
    
    st.markdown(response)

    # Display citations with clickable links
    citations = result.get("citations", [])
    if citations:
        with st.expander("📚 Citations & Sources", expanded=False):
            for i, citation in enumerate(citations, 1):
                if isinstance(citation, dict):
                    cite_type = citation.get("type", "url")
                    cite_display = citation.get("display", citation.get("content", ""))
                    cite_content = citation.get("content", "")
                    
                    if cite_type == "url":
                        st.markdown(f"**[{i}]** [{cite_display}]({cite_content})")
                    else:
                        st.markdown(f"**[{i}]** {cite_display}")
                else:
                    # Legacy format (string)
                    if citation.startswith("http"):
                        st.markdown(f"**[{i}]** [{citation}]({citation})")
                    else:
                        st.markdown(f"**[{i}]** {citation}")

    # Display metadata metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sources Used", metadata.get("num_sources", 0))
    with col2:
        score = metadata.get("critique_score", 0)
        st.metric("Quality Score", f"{score:.2f}")
    with col3:
        num_messages = metadata.get("num_messages", 0)
        st.metric("Agent Messages", num_messages)

    # Safety events (if any, but not blocking)
    if safety_events:
        with st.expander("🛡️ Safety Events", expanded=False):
            for event in safety_events:
                event_type = event.get("type", "unknown")
                is_safe = event.get("safe", True)
                violations = event.get("violations", [])
                
                if not is_safe:
                    st.warning(f"**{event_type.upper()}** - {len(violations)} violation(s) detected")
                    for violation in violations:
                        severity = violation.get("severity", "unknown")
                        reason = violation.get("reason", "Unknown")
                        st.text(f"  • [{severity.upper()}] {reason}")
                else:
                    st.success(f"**{event_type.upper()}** - Safety check passed")

    # Agent traces
    if st.session_state.show_traces:
        agent_traces = metadata.get("agent_traces", {})
        if agent_traces:
            display_agent_traces(agent_traces)
    
    # Export buttons
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Export JSON"):
            export_conversation_json(result)
    with col2:
        if st.button("📄 Export Markdown"):
            export_response_markdown(result)
    with col3:
        if st.button("📊 Export Evaluation"):
            # This would trigger evaluation if implemented
            st.info("Evaluation export coming soon")


def display_agent_traces(traces: Dict[str, Any]):
    """
    Display agent execution traces with improved formatting.
    """
    with st.expander("🔍 Agent Traces", expanded=False):
        # Show workflow visualization
        st.markdown("**Workflow:** Planner → Researcher → Writer → Critic")
        st.divider()
        
        for agent_name, actions in traces.items():
            st.markdown(f"### {agent_name}")
            for i, action in enumerate(actions, 1):
                action_type = action.get("action_type", "unknown")
                details = action.get("details", "")
                
                with st.container():
                    st.markdown(f"**Step {i}:** {action_type}")
                    if isinstance(details, str) and len(details) > 0:
                        # Show preview with expandable full content
                        preview = details[:150] + "..." if len(details) > 150 else details
                        st.text(preview)
                        if len(details) > 150:
                            with st.expander("View full content"):
                                st.text(details)
                    st.divider()


def display_sidebar():
    """Display sidebar with settings and statistics."""
    with st.sidebar:
        st.title("⚙️ Settings")

        # Show traces toggle
        st.session_state.show_traces = st.checkbox(
            "Show Agent Traces",
            value=st.session_state.show_traces
        )

        # Show safety log toggle
        st.session_state.show_safety_log = st.checkbox(
            "Show Safety Log",
            value=st.session_state.show_safety_log
        )

        st.divider()

        st.title("📊 Statistics")

        # Get actual statistics
        st.metric("Total Queries", len(st.session_state.history))
        
        # Get safety stats from orchestrator
        safety_events_count = 0
        if st.session_state.orchestrator and st.session_state.orchestrator.safety_manager:
            stats = st.session_state.orchestrator.safety_manager.get_safety_stats()
            safety_events_count = stats.get("total_events", 0)
        st.metric("Safety Events", safety_events_count)

        st.divider()

        # Clear history button
        if st.button("Clear History"):
            st.session_state.history = []
            st.rerun()

        # About section
        st.divider()
        st.markdown("### About")
        config = load_config()
        system_name = config.get("system", {}).get("name", "Research Assistant")
        topic = config.get("system", {}).get("topic", "General")
        st.markdown(f"**System:** {system_name}")
        st.markdown(f"**Topic:** {topic}")


def display_history():
    """Display query history."""
    if not st.session_state.history:
        return

    with st.expander("📜 Query History", expanded=False):
        for i, item in enumerate(reversed(st.session_state.history), 1):
            timestamp = item.get("timestamp", "")
            query = item.get("query", "")
            st.markdown(f"**{i}.** [{timestamp}] {query}")


def export_conversation_json(result: Dict[str, Any]):
    """Export conversation as JSON."""
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"conversation_{timestamp}.json"
    filepath = output_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(result, f, indent=2)
    
    st.success(f"✅ Exported to {filepath}")
    st.download_button(
        label="📥 Download JSON",
        data=json.dumps(result, indent=2),
        file_name=filename,
        mime="application/json"
    )


def export_response_markdown(result: Dict[str, Any]):
    """Export response as Markdown."""
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"response_{timestamp}.md"
    filepath = output_dir / filename
    
    markdown_content = f"""# Research Response

**Query:** {result.get('query', 'Unknown')}

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Response

{result.get('response', '')}

## Citations

"""
    
    citations = result.get("citations", [])
    for i, citation in enumerate(citations, 1):
        if isinstance(citation, dict):
            cite_display = citation.get("display", citation.get("content", ""))
            cite_content = citation.get("content", "")
            if citation.get("type") == "url":
                markdown_content += f"{i}. [{cite_display}]({cite_content})\n"
            else:
                markdown_content += f"{i}. {cite_display}\n"
        else:
            if citation.startswith("http"):
                markdown_content += f"{i}. [{citation}]({citation})\n"
            else:
                markdown_content += f"{i}. {citation}\n"
    
    metadata = result.get("metadata", {})
    markdown_content += f"\n## Metadata\n\n"
    markdown_content += f"- Sources Used: {metadata.get('num_sources', 0)}\n"
    markdown_content += f"- Agent Messages: {metadata.get('num_messages', 0)}\n"
    markdown_content += f"- Quality Score: {metadata.get('critique_score', 0):.2f}\n"
    
    with open(filepath, 'w') as f:
        f.write(markdown_content)
    
    st.success(f"✅ Exported to {filepath}")
    st.download_button(
        label="📥 Download Markdown",
        data=markdown_content,
        file_name=filename,
        mime="text/markdown"
    )


def load_evaluation_results():
    """Load all evaluation results from the outputs directory."""
    outputs_dir = Path("outputs")
    evaluation_files = list(outputs_dir.glob("evaluation_*.json"))
    judge_files = list(outputs_dir.glob("judge_outputs_*.json"))
    
    evaluations = []
    for file in sorted(evaluation_files, reverse=True):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                evaluations.append({
                    "filename": file.name,
                    "timestamp": data.get("timestamp", "Unknown"),
                    "data": data
                })
        except Exception as e:
            st.error(f"Error loading {file.name}: {e}")
    
    judge_outputs = []
    for file in sorted(judge_files, reverse=True):
        try:
            with open(file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    # Multiple judge outputs
                    for item in data:
                        judge_outputs.append({
                            "filename": file.name,
                            "data": item
                        })
                else:
                    # Single judge output
                    judge_outputs.append({
                        "filename": file.name,
                        "data": data
                    })
        except Exception as e:
            st.error(f"Error loading {file.name}: {e}")
    
    return evaluations, judge_outputs


def display_evaluation_page():
    """Display the evaluation results page."""
    st.title("📊 LLM-as-a-Judge Evaluation Results")
    st.markdown("View comprehensive evaluation metrics and judge outputs from system runs.")
    
    # Load evaluation data
    evaluations, judge_outputs = load_evaluation_results()
    
    if not evaluations and not judge_outputs:
        st.warning("No evaluation results found. Run evaluations first using `python -m src.evaluation.evaluator`")
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📈 Summary", "📝 Detailed Results", "🔍 Raw Judge Outputs"])
    
    with tab1:
        display_evaluation_summary(evaluations)
    
    with tab2:
        display_detailed_evaluations(evaluations)
    
    with tab3:
        display_judge_outputs(judge_outputs)


def display_evaluation_summary(evaluations):
    """Display evaluation summary metrics."""
    if not evaluations:
        st.info("No evaluation summaries available.")
        return
    
    # Select evaluation run
    eval_options = [f"{e['timestamp']} ({e['filename']})" for e in evaluations]
    selected_idx = st.selectbox("Select Evaluation Run:", range(len(eval_options)), 
                                 format_func=lambda x: eval_options[x])
    
    eval_data = evaluations[selected_idx]["data"]
    
    # Debug: Show what we loaded
    st.write(f"DEBUG: Loaded file: {evaluations[selected_idx]['filename']}")
    st.write(f"DEBUG: Overall average from data: {eval_data.get('scores', {}).get('overall_average', 'NOT FOUND')}")
    
    st.markdown("### Overall Performance")
    
    # Display summary metrics
    summary = eval_data.get("summary", {})
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Queries", summary.get("total_queries", 0))
    with col2:
        st.metric("Successful", summary.get("successful", 0))
    with col3:
        st.metric("Failed", summary.get("failed", 0))
    with col4:
        success_rate = summary.get("success_rate", 0) * 100
        st.metric("Success Rate", f"{success_rate:.1f}%")
    
    st.divider()
    
    # Display scores
    st.markdown("### Quality Scores")
    scores = eval_data.get("scores", {})
    overall_avg = scores.get("overall_average", 0)
    
    st.metric("Overall Average Score", f"{overall_avg:.2f} / 1.0")
    
    # By criterion
    by_criterion = scores.get("by_criterion", {})
    if by_criterion:
        st.markdown("#### Scores by Criterion")
        cols = st.columns(len(by_criterion))
        for i, (criterion, score) in enumerate(by_criterion.items()):
            with cols[i]:
                st.metric(criterion.replace("_", " ").title(), f"{score:.2f}")
    
    # By category
    by_category = scores.get("by_category", {})
    if by_category:
        st.markdown("#### Scores by Category")
        for category, score in by_category.items():
            st.progress(score, text=f"{category}: {score:.2f}")
    
    st.divider()
    
    # Error analysis
    st.markdown("### Error Analysis")
    error_analysis = eval_data.get("error_analysis", {})
    
    if error_analysis.get("total_errors", 0) > 0:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Errors", error_analysis.get("total_errors", 0))
        with col2:
            error_types = error_analysis.get("error_types", {})
            most_common = max(error_types.items(), key=lambda x: x[1]) if error_types else ("None", 0)
            st.metric("Most Common Error", f"{most_common[0]} ({most_common[1]})")
        
        # Sample errors
        sample_errors = error_analysis.get("sample_errors", [])
        if sample_errors:
            with st.expander("Sample Errors", expanded=False):
                for i, error in enumerate(sample_errors[:5], 1):
                    st.error(f"{i}. {error}")
    else:
        st.success("✅ No errors recorded!")
    
    # Best and worst results
    st.divider()
    st.markdown("### Best & Worst Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        best_result = eval_data.get("best_result")
        if best_result:
            st.markdown("#### 🏆 Best Result")
            st.metric("Score", f"{best_result.get('overall_score', 0):.2f}")
            st.text(f"Query: {best_result.get('query', 'Unknown')[:100]}...")
        else:
            st.info("No best result available")
    
    with col2:
        worst_result = eval_data.get("worst_result")
        if worst_result:
            st.markdown("#### ⚠️ Worst Result")
            st.metric("Score", f"{worst_result.get('overall_score', 0):.2f}")
            st.text(f"Query: {worst_result.get('query', 'Unknown')[:100]}...")
        else:
            st.info("No worst result available")


def display_detailed_evaluations(evaluations):
    """Display detailed evaluation results for each query."""
    if not evaluations:
        st.info("No detailed evaluations available.")
        return
    
    # Select evaluation run
    eval_options = [f"{e['timestamp']} ({e['filename']})" for e in evaluations]
    selected_idx = st.selectbox("Select Evaluation Run:", range(len(eval_options)), 
                                 format_func=lambda x: eval_options[x], key="detailed_select")
    
    eval_data = evaluations[selected_idx]["data"]
    detailed_results = eval_data.get("detailed_results", [])
    
    if not detailed_results:
        st.warning("No detailed results available.")
        return
    
    st.markdown(f"### Showing {len(detailed_results)} Query Results")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.selectbox("Filter by Category:", 
                                       ["All"] + list(set(r.get("category", "unknown") for r in detailed_results)))
    with col2:
        filter_error = st.checkbox("Show only errors")
    
    # Apply filters
    filtered_results = detailed_results
    if filter_category != "All":
        filtered_results = [r for r in filtered_results if r.get("category") == filter_category]
    if filter_error:
        filtered_results = [r for r in filtered_results if "error" in r]
    
    st.markdown(f"**Showing {len(filtered_results)} results**")
    
    # Display each result
    for i, result in enumerate(filtered_results, 1):
        with st.expander(f"Query {i}: {result.get('query', 'Unknown')[:80]}..."):
            # Query info
            st.markdown(f"**Category:** {result.get('category', 'Unknown')}")
            
            # Score - check both locations for overall_score
            overall_score = result.get("overall_score", 0)
            if overall_score == 0 and "evaluation" in result:
                overall_score = result["evaluation"].get("overall_score", 0)
            st.metric("Overall Score", f"{overall_score:.2f}")
            
            # Response
            st.markdown("#### Response")
            response = result.get("response", "No response")
            st.text_area("Response Text", response, height=150, key=f"response_{i}", disabled=True, label_visibility="collapsed")
            
            # Error if present
            if "error" in result:
                st.error(f"❌ Error: {result['error']}")
            
            # Judge evaluations - check both locations
            judge_evals = result.get("judge_evaluations", {})
            if not judge_evals and "evaluation" in result:
                # Try getting from nested evaluation object
                eval_data = result["evaluation"]
                judge_evals = eval_data.get("criterion_scores", {})
            
            if judge_evals:
                st.markdown("#### Judge Evaluations")
                
                for criterion, eval_data in judge_evals.items():
                    # Handle both 'average_score' and 'score' field names
                    avg_score = eval_data.get("average_score") or eval_data.get("score", 0)
                    
                    with st.container():
                        st.markdown(f"**{criterion.replace('_', ' ').title()}:** {avg_score:.2f}")
                        
                        # Overall reasoning
                        reasoning = eval_data.get("reasoning", "")
                        if reasoning:
                            st.caption(f"💭 {reasoning[:200]}...")
                        
                        # Perspectives
                        perspectives = eval_data.get("perspectives", [])
                        if perspectives:
                            for p in perspectives:
                                perspective_name = p.get("perspective", "Unknown")
                                score = p.get("score", 0)
                                p_reasoning = p.get("reasoning", "")
                                
                                with st.expander(f"📊 {perspective_name.title()} Perspective (Score: {score:.2f})"):
                                    st.write(p_reasoning)
                
                st.divider()


def display_judge_outputs(judge_outputs):
    """Display raw judge outputs with prompts."""
    if not judge_outputs:
        st.info("No judge outputs available.")
        return
    
    st.markdown("### Raw Judge Prompts and Outputs")
    st.markdown("View the actual prompts sent to the LLM judge and its raw responses.")
    
    # Select a judge output to display
    st.markdown(f"**Total Judge Outputs:** {len(judge_outputs)}")
    
    selected_idx = st.selectbox("Select Query to View:", 
                                range(len(judge_outputs)),
                                format_func=lambda x: f"Query: {judge_outputs[x]['data'].get('query', 'Unknown')[:60]}...")
    
    judge_data = judge_outputs[selected_idx]["data"]
    
    # Display query
    st.markdown("#### Original Query")
    st.info(judge_data.get("query", "Unknown"))
    
    # Display response
    st.markdown("#### System Response")
    response = judge_data.get("response", "No response")
    st.text_area("System Response Text", response, height=200, disabled=True, label_visibility="collapsed")
    
    # Display overall score
    overall_score = judge_data.get("overall_score", 0)
    st.metric("Overall Judge Score", f"{overall_score:.2f}")
    
    st.divider()
    
    # Display judge evaluations
    judge_evals = judge_data.get("judge_evaluations", {})
    
    if judge_evals:
        st.markdown("#### Judge Evaluations by Criterion")
        
        for criterion, eval_data in judge_evals.items():
            with st.expander(f"🔍 {criterion.replace('_', ' ').title()}", expanded=False):
                avg_score = eval_data.get("average_score", 0)
                st.metric("Average Score", f"{avg_score:.2f}")
                
                # Overall reasoning
                st.markdown("**Overall Reasoning:**")
                st.write(eval_data.get("reasoning", "No reasoning provided"))
                
                st.divider()
                
                # Perspectives
                perspectives = eval_data.get("perspectives", [])
                for p in perspectives:
                    st.markdown(f"##### {p.get('perspective', 'Unknown').title()} Perspective")
                    st.metric("Score", f"{p.get('score', 0):.2f}")
                    st.markdown("**Reasoning:**")
                    st.write(p.get("reasoning", "No reasoning provided"))
                    st.divider()
    
    # Download button for raw JSON
    st.markdown("#### Export Raw Data")
    json_str = json.dumps(judge_data, indent=2)
    st.download_button(
        label="📥 Download Raw JSON",
        data=json_str,
        file_name=f"judge_output_{judge_outputs[selected_idx]['filename']}",
        mime="application/json"
    )


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="Multi-Agent Research Assistant",
        page_icon="🤖",
        layout="wide"
    )

    initialize_session_state()
    
    # Navigation
    page = st.sidebar.radio("Navigation", ["🏠 Home", "📊 Evaluation Results"])
    
    if page == "📊 Evaluation Results":
        display_evaluation_page()
        return

    # Header
    st.title("🤖 Multi-Agent Research Assistant")
    st.markdown("Ask me anything about your research topic!")

    # Sidebar
    display_sidebar()

    # Main area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Query input
        query = st.text_area(
            "Enter your research query:",
            height=100,
            placeholder="e.g., What are the latest developments in explainable AI for novice users?"
        )

        # Submit button
        if st.button("🔍 Search", type="primary", use_container_width=True):
            if query.strip():
                # Create a progress container
                progress_container = st.container()
                with progress_container:
                    status_text = st.empty()
                    status_text.info("🔄 Initializing agents...")
                    
                with st.spinner("Processing your query (this may take 1-3 minutes)..."):
                    try:
                        # Process query (synchronous) with reduced rounds for faster response
                        status_text.info("🔍 Gathering research sources...")
                        result = process_query(query, max_rounds=5)  # Limit to 5 rounds for faster processing
                        status_text.empty()
                    except Exception as e:
                        status_text.error(f"❌ Error: {str(e)}")
                        result = {
                            "query": query,
                            "error": str(e),
                            "response": f"An error occurred: {str(e)}",
                            "citations": [],
                            "metadata": {"error": True}
                        }

                    # Add to history
                    st.session_state.history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "query": query,
                        "result": result
                    })

                    # Display result
                    st.divider()
                    display_response(result)
            else:
                st.warning("Please enter a query.")

        # History
        display_history()

    with col2:
        st.markdown("### 💡 Example Queries")
        examples = [
            "What are the key principles of user-centered design?",
            "Explain recent advances in AR usability research",
            "Compare different approaches to AI transparency",
            "What are ethical considerations in AI for education?",
        ]

        for example in examples:
            if st.button(example, use_container_width=True):
                st.session_state.example_query = example
                st.rerun()

        # If example was clicked, populate the text area
        if 'example_query' in st.session_state:
            st.info(f"Example query selected: {st.session_state.example_query}")
            del st.session_state.example_query

        st.divider()

        st.markdown("### ℹ️ How It Works")
        st.markdown("""
        1. **Planner** breaks down your query
        2. **Researcher** gathers evidence
        3. **Writer** synthesizes findings
        4. **Critic** verifies quality
        5. **Safety** checks ensure appropriate content
        """)

    # Safety log (if enabled)
    if st.session_state.show_safety_log:
        st.divider()
        st.markdown("### 🛡️ Safety Event Log")
        
        # Get safety events from orchestrator if available
        if st.session_state.orchestrator and st.session_state.orchestrator.safety_manager:
            safety_manager = st.session_state.orchestrator.safety_manager
            events = safety_manager.get_safety_events()
            stats = safety_manager.get_safety_stats()
            
            if events:
                st.metric("Total Safety Events", stats.get("total_events", 0))
                st.metric("Violations", stats.get("violations", 0))
                
                with st.expander("View All Events", expanded=False):
                    for event in events[-10:]:  # Last 10 events
                        event_type = event.get("type", "unknown")
                        is_safe = event.get("safe", True)
                        timestamp = event.get("timestamp", "Unknown")
                        violations = event.get("violations", [])
                        
                        status = "✅ Safe" if is_safe else "⚠️ Violation"
                        st.markdown(f"**{timestamp}** - {event_type.upper()} - {status}")
                        if violations:
                            for v in violations:
                                st.text(f"  • {v.get('reason', 'Unknown')}")
            else:
                st.info("No safety events recorded.")
        else:
            st.info("Safety manager not available.")


if __name__ == "__main__":
    main()
