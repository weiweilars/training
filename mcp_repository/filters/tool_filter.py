"""
Tool Filtering System - Matches tools to agent descriptions and capabilities
"""

import re
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass
import yaml
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from registry.mcp_registry import MCPRegistry, ToolDefinition, MCPServer

# Import retriever for semantic similarity
try:
    from retrieval.tool_retriever import ToolRetrieverManager, ToolSimilarityResult
    RETRIEVER_AVAILABLE = True
except ImportError:
    RETRIEVER_AVAILABLE = False
    print("Warning: Tool retriever not available")


@dataclass
class AgentCard:
    """Represents an agent with its capabilities and requirements"""
    name: str
    description: str
    capabilities: List[str]
    required_tools: List[str]  # Specific tool names required
    tool_categories: List[str]  # Categories of tools needed
    keywords: List[str]  # Keywords for matching tools
    metadata: Dict = None

    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'AgentCard':
        """Load agent card from YAML file"""
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            capabilities=data.get('capabilities', []),
            required_tools=data.get('required_tools', []),
            tool_categories=data.get('tool_categories', []),
            keywords=data.get('keywords', []),
            metadata=data.get('metadata', {})
        )


class ToolFilter:
    """Filters and matches tools based on agent requirements with semantic retrieval"""

    def __init__(self, registry: MCPRegistry, use_semantic_retrieval: bool = True):
        self.registry = registry
        self.use_semantic_retrieval = use_semantic_retrieval and RETRIEVER_AVAILABLE
        self.retriever_manager = None

        if self.use_semantic_retrieval:
            try:
                self.retriever_manager = ToolRetrieverManager("spacy")
                self.retriever_manager.index_tools_from_registry(registry)
                print("✓ Semantic retrieval enabled with spaCy")
            except Exception as e:
                print(f"Warning: Failed to initialize semantic retrieval: {e}")
                self.use_semantic_retrieval = False

    def extract_keywords_from_text(self, text: str) -> Set[str]:
        """Extract relevant keywords from description text"""
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been'}

        # Convert to lowercase and split
        words = re.findall(r'\b[a-z]+\b', text.lower())

        # Filter out stop words and short words
        keywords = {word for word in words if word not in stop_words and len(word) > 3}

        return keywords

    def calculate_relevance_score(self, tool: ToolDefinition, agent: AgentCard) -> float:
        """Calculate how relevant a tool is to an agent (0-1 score)"""
        score = 0.0
        max_score = 0.0

        # Direct tool name match (highest weight)
        if tool.name in agent.required_tools:
            score += 10.0
        max_score += 10.0

        # Category match (high weight)
        matching_categories = set(tool.categories) & set(agent.tool_categories)
        if matching_categories:
            score += 5.0 * len(matching_categories)
        max_score += 5.0 * max(len(agent.tool_categories), 1)

        # Keyword match in tool name (medium weight)
        tool_name_keywords = self.extract_keywords_from_text(tool.name)
        agent_keywords = set(agent.keywords)
        name_keyword_matches = tool_name_keywords & agent_keywords
        if name_keyword_matches:
            score += 3.0 * len(name_keyword_matches)
        max_score += 3.0 * max(len(agent_keywords), 1)

        # Keyword match in tool description (lower weight)
        desc_keywords = self.extract_keywords_from_text(tool.description)
        desc_keyword_matches = desc_keywords & agent_keywords
        if desc_keyword_matches:
            score += 1.0 * len(desc_keyword_matches)
        max_score += 1.0 * max(len(agent_keywords), 1)

        # Description relevance (using agent description)
        agent_desc_keywords = self.extract_keywords_from_text(agent.description)
        desc_relevance = desc_keywords & agent_desc_keywords
        if desc_relevance:
            score += 0.5 * len(desc_relevance)
        max_score += 0.5 * max(len(agent_desc_keywords), 1)

        # Capability matching
        for capability in agent.capabilities:
            cap_keywords = self.extract_keywords_from_text(capability)
            if cap_keywords & desc_keywords or cap_keywords & tool_name_keywords:
                score += 2.0
        max_score += 2.0 * max(len(agent.capabilities), 1)

        # Normalize score
        return min(score / max(max_score, 1), 1.0)

    def filter_tools_for_agent(self, agent: AgentCard,
                              min_score: float = 0.3,
                              max_tools: int = None) -> List[Tuple[str, ToolDefinition, float]]:
        """
        Filter tools from all servers based on agent requirements

        Returns: List of (server_id, tool, score) tuples sorted by relevance
        """
        matched_tools = []

        # Check all servers and their tools
        for server_id, server in self.registry.servers.items():
            for tool in server.tools:
                score = self.calculate_relevance_score(tool, agent)

                if score >= min_score:
                    matched_tools.append((server_id, tool, score))

        # Sort by score (highest first)
        matched_tools.sort(key=lambda x: x[2], reverse=True)

        # Limit number of tools if specified
        if max_tools:
            matched_tools = matched_tools[:max_tools]

        return matched_tools

    def filter_tools_semantic(self, agent: AgentCard,
                            top_k: int = 20,
                            threshold: float = 0.3) -> List[Tuple[str, ToolDefinition, float]]:
        """
        Filter tools using semantic similarity

        Args:
            agent: Agent card with description and requirements
            top_k: Maximum number of tools to return
            threshold: Minimum similarity threshold

        Returns:
            List of (server_id, tool, similarity_score) tuples
        """
        if not self.use_semantic_retrieval or not self.retriever_manager:
            print("Semantic retrieval not available, falling back to keyword-based filtering")
            return self.filter_tools_for_agent(agent)

        # Create comprehensive query from agent information
        query_parts = [agent.description]

        if agent.capabilities:
            query_parts.extend(agent.capabilities)

        if agent.keywords:
            query_parts.extend(agent.keywords)

        query = " ".join(query_parts)

        # Retrieve similar tools
        similar_tools = self.retriever_manager.retrieve_for_agent_description(
            query, top_k=top_k, threshold=threshold
        )

        # Convert to expected format
        results = []
        for result in similar_tools:
            # Find the tool and server
            tool_found = False
            for server_id, server in self.registry.servers.items():
                for tool in server.tools:
                    if tool.unique_id == result.tool_unique_id:
                        results.append((server_id, tool, result.similarity_score))
                        tool_found = True
                        break
                if tool_found:
                    break

        return results

    def filter_tools_hybrid(self, agent: AgentCard,
                          semantic_weight: float = 0.7,
                          keyword_weight: float = 0.3,
                          top_k: int = 20) -> List[Tuple[str, ToolDefinition, float]]:
        """
        Hybrid filtering combining semantic and keyword-based approaches

        Args:
            agent: Agent card
            semantic_weight: Weight for semantic similarity
            keyword_weight: Weight for keyword matching
            top_k: Maximum number of tools

        Returns:
            List of (server_id, tool, combined_score) tuples
        """
        if not self.use_semantic_retrieval:
            return self.filter_tools_for_agent(agent, max_tools=top_k)

        # Get semantic results
        semantic_results = self.filter_tools_semantic(agent, top_k=top_k*2)
        semantic_scores = {
            (server_id, tool.unique_id): score
            for server_id, tool, score in semantic_results
        }

        # Get keyword-based results
        keyword_results = self.filter_tools_for_agent(agent, max_tools=top_k*2)
        keyword_scores = {
            (server_id, tool.unique_id): score
            for server_id, tool, score in keyword_results
        }

        # Combine scores
        all_tools = set(semantic_scores.keys()) | set(keyword_scores.keys())
        combined_results = []

        for server_id, tool_id in all_tools:
            # Get tool reference
            tool = None
            for sid, server in self.registry.servers.items():
                if sid == server_id:
                    for t in server.tools:
                        if t.unique_id == tool_id:
                            tool = t
                            break
                    break

            if tool:
                semantic_score = semantic_scores.get((server_id, tool_id), 0.0)
                keyword_score = keyword_scores.get((server_id, tool_id), 0.0)

                # Normalize scores to 0-1 range if needed
                semantic_score = min(semantic_score, 1.0)
                keyword_score = min(keyword_score, 1.0)

                combined_score = (
                    semantic_weight * semantic_score +
                    keyword_weight * keyword_score
                )

                combined_results.append((server_id, tool, combined_score))

        # Sort by combined score
        combined_results.sort(key=lambda x: x[2], reverse=True)

        return combined_results[:top_k]

    def get_required_servers(self, agent: AgentCard) -> Set[str]:
        """Get the minimum set of servers needed to provide all required tools"""
        required_servers = set()
        matched_tools = self.filter_tools_for_agent(agent)

        # First, ensure all explicitly required tools are found
        for required_tool in agent.required_tools:
            tool_found = False
            for server_id, tool, score in matched_tools:
                if tool.name == required_tool:
                    required_servers.add(server_id)
                    tool_found = True
                    break

            if not tool_found:
                print(f"Warning: Required tool '{required_tool}' not found in any server")

        # Add servers for high-scoring tools
        for server_id, tool, score in matched_tools:
            if score >= 0.5:  # Only include high-relevance tools
                required_servers.add(server_id)

        return required_servers

    def create_filtered_server_config(self, agent: AgentCard) -> Dict[str, List[ToolDefinition]]:
        """
        Create a configuration of servers and their filtered tools for an agent

        Returns: Dictionary mapping server_id to list of relevant tools
        """
        server_tools = {}
        matched_tools = self.filter_tools_for_agent(agent)

        for server_id, tool, score in matched_tools:
            if server_id not in server_tools:
                server_tools[server_id] = []
            server_tools[server_id].append(tool)

        return server_tools

    def generate_agent_report(self, agent: AgentCard) -> str:
        """Generate a detailed report of tool matches for an agent"""
        report = []
        report.append(f"Tool Matching Report for Agent: {agent.name}")
        report.append("=" * 60)
        report.append(f"Description: {agent.description}")
        report.append(f"Required Tools: {', '.join(agent.required_tools)}")
        report.append(f"Tool Categories: {', '.join(agent.tool_categories)}")
        report.append(f"Keywords: {', '.join(agent.keywords)}")
        report.append("")

        matched_tools = self.filter_tools_for_agent(agent)

        if not matched_tools:
            report.append("No matching tools found!")
        else:
            report.append(f"Found {len(matched_tools)} matching tools:")
            report.append("-" * 40)

            current_server = None
            for server_id, tool, score in matched_tools:
                if server_id != current_server:
                    server = self.registry.get_server(server_id)
                    report.append(f"\nServer: {server.name} ({server_id})")
                    current_server = server_id

                score_bar = "█" * int(score * 10) + "░" * (10 - int(score * 10))
                report.append(f"  - {tool.name}: {tool.description}")
                report.append(f"    Score: {score:.2f} [{score_bar}]")
                report.append(f"    Categories: {', '.join(tool.categories)}")

        report.append("\n" + "=" * 60)
        required_servers = self.get_required_servers(agent)
        report.append(f"Required Servers: {', '.join(required_servers)}")

        return "\n".join(report)


def create_example_agent_cards():
    """Create example agent cards for testing"""

    # Job Requisition Agent
    job_req_agent = AgentCard(
        name="Job Requisition Agent",
        description="Manages job requisitions, creates job postings, and handles position requirements",
        capabilities=[
            "Create and manage job requisitions",
            "Define job requirements and qualifications",
            "Publish job postings"
        ],
        required_tools=["create_job_requisition"],
        tool_categories=["hr", "recruitment", "requisition"],
        keywords=["job", "requisition", "position", "posting", "requirement"]
    )

    # Resume Screening Agent
    screening_agent = AgentCard(
        name="Resume Screening Agent",
        description="Screens and evaluates candidate resumes against job requirements",
        capabilities=[
            "Parse and analyze resumes",
            "Match candidates to job requirements",
            "Score and rank candidates"
        ],
        required_tools=["screen_resume"],
        tool_categories=["hr", "recruitment", "screening"],
        keywords=["resume", "cv", "screening", "evaluation", "candidate", "qualification"]
    )

    # Interview Scheduling Agent
    scheduling_agent = AgentCard(
        name="Interview Scheduling Agent",
        description="Coordinates and schedules interviews between candidates and interviewers",
        capabilities=[
            "Schedule interviews",
            "Coordinate calendars",
            "Send interview invitations",
            "Handle rescheduling"
        ],
        required_tools=["schedule_interview", "send_notification"],
        tool_categories=["hr", "recruitment", "scheduling", "communication"],
        keywords=["interview", "schedule", "calendar", "meeting", "coordination", "invitation"]
    )

    # Analytics Agent
    analytics_agent = AgentCard(
        name="Recruitment Analytics Agent",
        description="Generates reports and analyzes recruitment metrics and performance",
        capabilities=[
            "Generate recruitment reports",
            "Analyze hiring metrics",
            "Track KPIs",
            "Provide insights"
        ],
        required_tools=["generate_report", "analyze_metrics"],
        tool_categories=["analytics", "reporting", "hr"],
        keywords=["report", "analytics", "metrics", "kpi", "performance", "data", "insights"]
    )

    return [job_req_agent, screening_agent, scheduling_agent, analytics_agent]


if __name__ == "__main__":
    # Create registry with example servers
    from registry.mcp_registry import create_example_servers
    registry = create_example_servers()

    # Create tool filter
    filter_system = ToolFilter(registry)

    # Test with example agents
    agents = create_example_agent_cards()

    for agent in agents:
        print("\n" + "="*80)
        print(filter_system.generate_agent_report(agent))

    # Test filtered server configuration
    print("\n" + "="*80)
    print("Filtered Server Configuration for Interview Scheduling Agent:")
    config = filter_system.create_filtered_server_config(agents[2])
    for server_id, tools in config.items():
        print(f"\n{server_id}:")
        for tool in tools:
            print(f"  - {tool.name}")