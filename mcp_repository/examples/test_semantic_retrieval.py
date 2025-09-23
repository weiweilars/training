#!/usr/bin/env python3
"""
Test Semantic Tool Retrieval System
"""

import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from registry.mcp_registry_extended import ExtendedMCPRegistry, ToolDefinition, MCPServer, ServerType
from filters.tool_filter import ToolFilter, AgentCard
from retrieval.tool_retriever import ToolRetrieverManager


def create_comprehensive_test_registry():
    """Create a registry with diverse tools for testing semantic retrieval"""
    registry = ExtendedMCPRegistry()

    # HR & Recruitment Tools
    hr_tools = [
        ToolDefinition(
            name="create_job_posting",
            description="Create and publish job postings for open positions",
            categories=["hr", "recruitment", "posting"],
            keywords=["job", "position", "hiring", "recruitment", "posting", "create"],
            server_id="hr_system"
        ),
        ToolDefinition(
            name="screen_candidates",
            description="Automatically screen and evaluate candidate applications using AI",
            categories=["hr", "recruitment", "screening", "ai"],
            keywords=["candidate", "screening", "evaluation", "ai", "resume", "cv"],
            server_id="hr_system"
        ),
        ToolDefinition(
            name="schedule_interviews",
            description="Schedule and coordinate interviews between candidates and hiring managers",
            categories=["hr", "recruitment", "scheduling"],
            keywords=["interview", "schedule", "calendar", "coordination", "meeting"],
            server_id="hr_system"
        ),
        ToolDefinition(
            name="send_offer_letter",
            description="Generate and send job offer letters to successful candidates",
            categories=["hr", "recruitment", "communication"],
            keywords=["offer", "letter", "communication", "hiring", "contract"],
            server_id="hr_system"
        )
    ]

    hr_server = MCPServer(
        name="HR Management System",
        description="Comprehensive HR and recruitment platform",
        version="2.0.0",
        tools=hr_tools,
        server_type=ServerType.HTTP,
        endpoint="http://hr.company.com:8080"
    )

    # Analytics & Reporting Tools
    analytics_tools = [
        ToolDefinition(
            name="generate_recruitment_metrics",
            description="Generate comprehensive recruitment analytics and KPI reports",
            categories=["analytics", "reporting", "hr", "metrics"],
            keywords=["report", "analytics", "metrics", "kpi", "recruitment", "data"],
            server_id="analytics_platform"
        ),
        ToolDefinition(
            name="analyze_hiring_funnel",
            description="Analyze recruitment funnel performance and conversion rates",
            categories=["analytics", "hr", "funnel"],
            keywords=["funnel", "conversion", "analysis", "hiring", "performance"],
            server_id="analytics_platform"
        ),
        ToolDefinition(
            name="create_dashboard",
            description="Create interactive dashboards for data visualization",
            categories=["analytics", "visualization", "dashboard"],
            keywords=["dashboard", "visualization", "charts", "interactive", "data"],
            server_id="analytics_platform"
        ),
        ToolDefinition(
            name="export_data",
            description="Export data in various formats (CSV, Excel, JSON)",
            categories=["analytics", "data", "export"],
            keywords=["export", "data", "csv", "excel", "json", "download"],
            server_id="analytics_platform"
        )
    ]

    analytics_server = MCPServer(
        name="Analytics Platform",
        description="Advanced analytics and business intelligence platform",
        version="3.1.0",
        tools=analytics_tools,
        server_type=ServerType.HTTP,
        endpoint="http://analytics.internal:8100"
    )

    # Communication & Notification Tools
    comm_tools = [
        ToolDefinition(
            name="send_email",
            description="Send professional emails to candidates and team members",
            categories=["communication", "email"],
            keywords=["email", "send", "message", "communication", "notification"],
            server_id="communication_service"
        ),
        ToolDefinition(
            name="send_sms",
            description="Send SMS notifications for urgent communications",
            categories=["communication", "sms", "mobile"],
            keywords=["sms", "text", "mobile", "notification", "urgent"],
            server_id="communication_service"
        ),
        ToolDefinition(
            name="create_notification",
            description="Create and manage in-app notifications and alerts",
            categories=["communication", "notification", "alerts"],
            keywords=["notification", "alert", "in-app", "message", "system"],
            server_id="communication_service"
        ),
        ToolDefinition(
            name="manage_templates",
            description="Create and manage email and message templates",
            categories=["communication", "templates", "management"],
            keywords=["template", "email", "message", "manage", "customize"],
            server_id="communication_service"
        )
    ]

    comm_server = MCPServer(
        name="Communication Service",
        description="Multi-channel communication and notification system",
        version="1.5.0",
        tools=comm_tools,
        server_type=ServerType.HTTP,
        endpoint="http://comm.internal:8200"
    )

    # Document & File Management Tools
    doc_tools = [
        ToolDefinition(
            name="create_document",
            description="Create and format professional documents",
            categories=["documents", "creation", "formatting"],
            keywords=["document", "create", "format", "professional", "text"],
            server_id="document_service"
        ),
        ToolDefinition(
            name="convert_files",
            description="Convert files between different formats (PDF, Word, etc.)",
            categories=["documents", "conversion", "files"],
            keywords=["convert", "file", "pdf", "word", "format", "transformation"],
            server_id="document_service"
        ),
        ToolDefinition(
            name="store_files",
            description="Securely store and organize files in cloud storage",
            categories=["documents", "storage", "cloud"],
            keywords=["store", "cloud", "storage", "organize", "secure", "files"],
            server_id="document_service"
        )
    ]

    doc_server = MCPServer(
        name="Document Service",
        description="Document creation and file management system",
        version="2.2.0",
        tools=doc_tools,
        server_type=ServerType.HTTP,
        endpoint="http://docs.internal:8300"
    )

    # Add all servers to registry
    registry.servers["hr_system"] = hr_server
    registry.servers["analytics_platform"] = analytics_server
    registry.servers["communication_service"] = comm_server
    registry.servers["document_service"] = doc_server

    return registry


def test_semantic_retrieval():
    """Test semantic tool retrieval with various agent descriptions"""
    print("SEMANTIC TOOL RETRIEVAL TEST")
    print("="*60)

    # Create test registry
    registry = create_comprehensive_test_registry()

    # Initialize filter with semantic retrieval
    print("\nInitializing semantic retrieval system...")
    filter_system = ToolFilter(registry, use_semantic_retrieval=True)

    # Test cases with different agent descriptions
    test_agents = [
        AgentCard(
            name="Recruitment Specialist",
            description="I help companies find and hire the best talent by managing the entire recruitment process from posting jobs to making offers",
            capabilities=["Post job openings", "Screen candidates", "Coordinate interviews", "Send offers"],
            required_tools=[],
            tool_categories=["hr", "recruitment"],
            keywords=["hiring", "recruitment", "candidates", "jobs"]
        ),

        AgentCard(
            name="HR Analytics Expert",
            description="I analyze recruitment data to provide insights on hiring performance, funnel conversion rates, and team productivity metrics",
            capabilities=["Generate reports", "Analyze data", "Create visualizations", "Track KPIs"],
            required_tools=[],
            tool_categories=["analytics", "hr"],
            keywords=["analytics", "reports", "metrics", "data", "visualization"]
        ),

        AgentCard(
            name="Communication Manager",
            description="I handle all candidate communications including emails, SMS notifications, and creating professional message templates",
            capabilities=["Send emails", "Send notifications", "Manage templates", "Coordinate communications"],
            required_tools=[],
            tool_categories=["communication"],
            keywords=["email", "communication", "notification", "templates", "messages"]
        ),

        AgentCard(
            name="Onboarding Coordinator",
            description="I manage new employee onboarding by creating documents, converting files, and organizing paperwork for new hires",
            capabilities=["Create documents", "Convert files", "Organize paperwork", "Store files"],
            required_tools=[],
            tool_categories=["documents", "hr"],
            keywords=["documents", "onboarding", "paperwork", "files", "new hire"]
        ),

        AgentCard(
            name="Full-Stack Recruiter",
            description="I handle the complete recruitment lifecycle from posting jobs and screening candidates to analyzing performance and communicating with stakeholders",
            capabilities=["End-to-end recruitment", "Performance analysis", "Stakeholder communication"],
            required_tools=[],
            tool_categories=["hr", "recruitment", "analytics", "communication"],
            keywords=["recruitment", "lifecycle", "analysis", "communication", "performance"]
        )
    ]

    # Test each agent with different retrieval methods
    for agent in test_agents:
        print(f"\n{'-'*60}")
        print(f"Agent: {agent.name}")
        print(f"Description: {agent.description}")
        print(f"{'-'*60}")

        # 1. Semantic retrieval
        print(f"\n1. SEMANTIC RETRIEVAL:")
        semantic_results = filter_system.filter_tools_semantic(agent, top_k=5, threshold=0.2)

        if semantic_results:
            for i, (server_id, tool, score) in enumerate(semantic_results, 1):
                print(f"   {i}. {tool.name} (from {server_id})")
                print(f"      Score: {score:.3f}")
                print(f"      Description: {tool.description}")
        else:
            print("   No semantic matches found")

        # 2. Keyword-based retrieval (traditional)
        print(f"\n2. KEYWORD-BASED RETRIEVAL:")
        keyword_results = filter_system.filter_tools_for_agent(agent, max_tools=5)

        if keyword_results:
            for i, (server_id, tool, score) in enumerate(keyword_results, 1):
                print(f"   {i}. {tool.name} (from {server_id})")
                print(f"      Score: {score:.3f}")
                print(f"      Description: {tool.description}")
        else:
            print("   No keyword matches found")

        # 3. Hybrid approach
        print(f"\n3. HYBRID RETRIEVAL (70% semantic + 30% keyword):")
        hybrid_results = filter_system.filter_tools_hybrid(agent, top_k=5)

        if hybrid_results:
            for i, (server_id, tool, score) in enumerate(hybrid_results, 1):
                print(f"   {i}. {tool.name} (from {server_id})")
                print(f"      Combined Score: {score:.3f}")
                print(f"      Description: {tool.description}")
        else:
            print("   No hybrid matches found")


def test_retriever_switching():
    """Test switching between different retriever types"""
    print(f"\n\n{'='*60}")
    print("RETRIEVER SWITCHING TEST")
    print("="*60)

    # Test retriever manager
    manager = ToolRetrieverManager("spacy")

    print(f"Current retriever info:")
    info = manager.get_retriever_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    # Test switching (this will fail gracefully since embedding retriever is not implemented)
    print(f"\nTesting retriever switching...")
    try:
        manager.switch_retriever("embeddings")
        print("✓ Successfully switched to embedding retriever")
    except NotImplementedError:
        print("✗ Embedding retriever not implemented yet (expected)")
    except Exception as e:
        print(f"✗ Error switching retriever: {e}")


def test_performance_comparison():
    """Compare performance of different retrieval methods"""
    print(f"\n\n{'='*60}")
    print("PERFORMANCE COMPARISON")
    print("="*60)

    registry = create_comprehensive_test_registry()
    filter_system = ToolFilter(registry, use_semantic_retrieval=True)

    # Test agent for performance comparison
    test_agent = AgentCard(
        name="Test Agent",
        description="I need tools for recruitment management, candidate screening, and performance analytics",
        capabilities=["Recruit", "Screen", "Analyze"],
        required_tools=[],
        tool_categories=["hr", "analytics"],
        keywords=["recruitment", "screening", "analytics"]
    )

    import time

    # Measure semantic retrieval time
    start_time = time.time()
    semantic_results = filter_system.filter_tools_semantic(test_agent, top_k=10)
    semantic_time = time.time() - start_time

    # Measure keyword retrieval time
    start_time = time.time()
    keyword_results = filter_system.filter_tools_for_agent(test_agent, max_tools=10)
    keyword_time = time.time() - start_time

    # Measure hybrid retrieval time
    start_time = time.time()
    hybrid_results = filter_system.filter_tools_hybrid(test_agent, top_k=10)
    hybrid_time = time.time() - start_time

    print(f"Semantic Retrieval: {len(semantic_results)} results in {semantic_time:.4f}s")
    print(f"Keyword Retrieval:  {len(keyword_results)} results in {keyword_time:.4f}s")
    print(f"Hybrid Retrieval:   {len(hybrid_results)} results in {hybrid_time:.4f}s")

    # Show unique results from each method
    semantic_tools = {tool.unique_id for _, tool, _ in semantic_results}
    keyword_tools = {tool.unique_id for _, tool, _ in keyword_results}
    hybrid_tools = {tool.unique_id for _, tool, _ in hybrid_results}

    print(f"\nResult overlap:")
    print(f"  Semantic ∩ Keyword: {len(semantic_tools & keyword_tools)} tools")
    print(f"  Semantic ∩ Hybrid:  {len(semantic_tools & hybrid_tools)} tools")
    print(f"  Keyword ∩ Hybrid:   {len(keyword_tools & hybrid_tools)} tools")


def main():
    """Run all semantic retrieval tests"""
    try:
        test_semantic_retrieval()
        test_retriever_switching()
        test_performance_comparison()

        print(f"\n\n{'='*60}")
        print("SEMANTIC RETRIEVAL SUMMARY")
        print("="*60)
        print("✓ Independent tool retriever with spaCy similarity")
        print("✓ Semantic tool filtering based on agent descriptions")
        print("✓ Hybrid approach combining semantic + keyword matching")
        print("✓ Easy replacement interface for future embedding models")
        print("✓ Performance comparison between retrieval methods")

        print(f"\nKey Benefits:")
        print(f"  • Better matching based on semantic meaning")
        print(f"  • Finds relevant tools even without exact keyword matches")
        print(f"  • Modular design for easy model replacement")
        print(f"  • Backward compatibility with keyword-based filtering")

    except Exception as e:
        print(f"Error running tests: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()