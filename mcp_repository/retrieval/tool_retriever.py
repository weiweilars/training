"""
Tool Retriever - Semantic similarity-based tool retrieval system
Independent module that can be replaced with embedding models later
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional, Protocol
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    import spacy
    from spacy.lang.en import English
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spaCy not available. Install with: pip install spacy")
    print("And download model with: python -m spacy download en_core_web_md")


@dataclass
class ToolSimilarityResult:
    """Result of tool similarity calculation"""
    tool_unique_id: str
    tool_name: str
    tool_description: str
    server_id: str
    server_name: str
    similarity_score: float
    matched_features: List[str]  # What features caused the match
    categories: List[str]
    keywords: List[str]


class ToolRetrieverInterface(Protocol):
    """Interface for tool retrievers - allows easy replacement"""

    def index_tools(self, tools_data: Dict[str, Any]) -> None:
        """Index tools for retrieval"""
        ...

    def retrieve_similar_tools(self,
                             query: str,
                             top_k: int = 10,
                             threshold: float = 0.3) -> List[ToolSimilarityResult]:
        """Retrieve tools similar to query"""
        ...

    def get_retriever_info(self) -> Dict[str, Any]:
        """Get information about the retriever"""
        ...


class SpacyToolRetriever:
    """
    Tool retriever using spaCy sentence similarity
    Can be easily replaced with embedding-based retrievers
    """

    def __init__(self, model_name: str = "en_core_web_md"):
        """
        Initialize spaCy retriever

        Args:
            model_name: spaCy model to use (needs word vectors)
        """
        self.model_name = model_name
        self.nlp = None
        self.indexed_tools = {}
        self.tool_docs = {}  # Cache of spaCy docs for tools

        self._load_model()

    def _load_model(self):
        """Load spaCy model"""
        if not SPACY_AVAILABLE:
            raise ImportError("spaCy not available. Install with: pip install spacy")

        try:
            self.nlp = spacy.load(self.model_name)
            if not self.nlp.has_pipe('sentencizer'):
                self.nlp.add_pipe('sentencizer')
        except OSError:
            print(f"spaCy model '{self.model_name}' not found.")
            print(f"Download with: python -m spacy download {self.model_name}")
            # Fallback to basic English model
            try:
                self.nlp = English()
                self.nlp.add_pipe('sentencizer')
                print("Using basic English model (no word vectors)")
            except Exception as e:
                raise RuntimeError(f"Failed to load any spaCy model: {e}")

    def index_tools(self, tools_data: Dict[str, Any]) -> None:
        """
        Index tools for semantic retrieval

        Args:
            tools_data: Dictionary with tool information from registry
        """
        self.indexed_tools = tools_data
        self.tool_docs = {}

        print(f"Indexing {len(tools_data)} tools with spaCy...")

        for tool_id, tool_info in tools_data.items():
            # Create searchable text from tool information
            searchable_text = self._create_searchable_text(tool_info)

            # Process with spaCy
            doc = self.nlp(searchable_text)
            self.tool_docs[tool_id] = {
                'doc': doc,
                'text': searchable_text,
                'tool_info': tool_info
            }

        print(f"✓ Indexed {len(self.tool_docs)} tools")

    def _create_searchable_text(self, tool_info: Dict[str, Any]) -> str:
        """Create searchable text from tool information"""
        text_parts = []

        # Tool name and description (high weight)
        text_parts.append(tool_info.get('name', ''))
        text_parts.append(tool_info.get('description', ''))

        # Categories and keywords
        categories = tool_info.get('categories', [])
        keywords = tool_info.get('keywords', [])

        if categories:
            text_parts.append(' '.join(categories))
        if keywords:
            text_parts.append(' '.join(keywords))

        # Server context
        server_name = tool_info.get('server_name', '')
        if server_name:
            text_parts.append(server_name)

        return ' '.join(filter(None, text_parts))

    def retrieve_similar_tools(self,
                             query: str,
                             top_k: int = 10,
                             threshold: float = 0.3) -> List[ToolSimilarityResult]:
        """
        Retrieve tools similar to query using spaCy similarity

        Args:
            query: Search query (agent description)
            top_k: Number of top results to return
            threshold: Minimum similarity threshold

        Returns:
            List of similar tools sorted by similarity score
        """
        if not self.tool_docs:
            return []

        # Process query with spaCy
        query_doc = self.nlp(query)

        similarities = []

        for tool_id, tool_data in self.tool_docs.items():
            tool_doc = tool_data['doc']
            tool_info = tool_data['tool_info']

            # Calculate similarity
            if query_doc.has_vector and tool_doc.has_vector:
                similarity = query_doc.similarity(tool_doc)
            else:
                # Fallback to token-based similarity if no vectors
                similarity = self._token_similarity(query_doc, tool_doc)

            if similarity >= threshold:
                # Identify what features matched
                matched_features = self._identify_matched_features(
                    query, tool_info, similarity
                )

                result = ToolSimilarityResult(
                    tool_unique_id=tool_id,
                    tool_name=tool_info['name'],
                    tool_description=tool_info['description'],
                    server_id=tool_info['server_id'],
                    server_name=tool_info['server_name'],
                    similarity_score=similarity,
                    matched_features=matched_features,
                    categories=tool_info.get('categories', []),
                    keywords=tool_info.get('keywords', [])
                )
                similarities.append(result)

        # Sort by similarity score (descending)
        similarities.sort(key=lambda x: x.similarity_score, reverse=True)

        return similarities[:top_k]

    def _token_similarity(self, doc1, doc2) -> float:
        """Fallback token-based similarity when no word vectors available"""
        tokens1 = set(token.lemma_.lower() for token in doc1 if not token.is_stop and not token.is_punct)
        tokens2 = set(token.lemma_.lower() for token in doc2 if not token.is_stop and not token.is_punct)

        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)

        return len(intersection) / len(union) if union else 0.0

    def _identify_matched_features(self, query: str, tool_info: Dict[str, Any], similarity: float) -> List[str]:
        """Identify what features caused the similarity match"""
        matched = []

        query_lower = query.lower()

        # Check direct matches
        if any(word in query_lower for word in tool_info['name'].lower().split()):
            matched.append('name_match')

        if any(word in query_lower for word in tool_info['description'].lower().split()[:10]):
            matched.append('description_match')

        # Check category matches
        for category in tool_info.get('categories', []):
            if category.lower() in query_lower:
                matched.append(f'category_{category}')

        # Check keyword matches
        for keyword in tool_info.get('keywords', []):
            if keyword.lower() in query_lower:
                matched.append(f'keyword_{keyword}')

        # Add similarity-based match if high score
        if similarity > 0.7:
            matched.append('high_semantic_similarity')
        elif similarity > 0.5:
            matched.append('medium_semantic_similarity')
        else:
            matched.append('low_semantic_similarity')

        return matched

    def get_retriever_info(self) -> Dict[str, Any]:
        """Get information about the retriever"""
        return {
            'type': 'spacy',
            'model': self.model_name,
            'has_vectors': self.nlp.vocab.vectors.size > 0 if self.nlp else False,
            'indexed_tools': len(self.indexed_tools),
            'capabilities': [
                'semantic_similarity',
                'token_matching',
                'category_matching',
                'keyword_matching'
            ]
        }


class ToolRetrieverManager:
    """
    Manager for tool retrievers - allows easy switching between different retrieval methods
    """

    def __init__(self, retriever_type: str = "spacy"):
        """
        Initialize retriever manager

        Args:
            retriever_type: Type of retriever to use ('spacy', 'embeddings', etc.)
        """
        self.retriever_type = retriever_type
        self.retriever = None
        self._initialize_retriever()

    def _initialize_retriever(self):
        """Initialize the appropriate retriever"""
        if self.retriever_type == "spacy":
            self.retriever = SpacyToolRetriever()
        else:
            raise ValueError(f"Unknown retriever type: {self.retriever_type}")

    def index_tools_from_registry(self, registry) -> None:
        """Index tools from MCP registry"""
        tools_data = registry.list_all_tools_with_ids()
        self.retriever.index_tools(tools_data)

    def retrieve_for_agent_description(self,
                                     agent_description: str,
                                     top_k: int = 10,
                                     threshold: float = 0.3) -> List[ToolSimilarityResult]:
        """
        Retrieve tools relevant to an agent description

        Args:
            agent_description: Description of what the agent does
            top_k: Number of top results
            threshold: Minimum similarity threshold

        Returns:
            List of relevant tools
        """
        if not self.retriever:
            return []

        return self.retriever.retrieve_similar_tools(
            query=agent_description,
            top_k=top_k,
            threshold=threshold
        )

    def switch_retriever(self, new_retriever_type: str, **kwargs):
        """
        Switch to a different retriever type

        Args:
            new_retriever_type: New retriever type
            **kwargs: Additional arguments for the new retriever
        """
        self.retriever_type = new_retriever_type

        if new_retriever_type == "spacy":
            self.retriever = SpacyToolRetriever(**kwargs)
        elif new_retriever_type == "embeddings":
            # Placeholder for future embedding-based retriever
            raise NotImplementedError("Embedding retriever not implemented yet")
        else:
            raise ValueError(f"Unknown retriever type: {new_retriever_type}")

        print(f"Switched to {new_retriever_type} retriever")

    def get_retriever_info(self) -> Dict[str, Any]:
        """Get information about current retriever"""
        if self.retriever:
            return self.retriever.get_retriever_info()
        return {"type": "none", "status": "not_initialized"}


# Future placeholder for embedding-based retriever
class EmbeddingToolRetriever:
    """
    Placeholder for embedding-based tool retriever
    Will be implemented when embedding models are available
    """

    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding retriever

        Args:
            embedding_model: Embedding model to use
        """
        self.embedding_model = embedding_model
        self.embeddings = None
        self.indexed_tools = {}

        # Placeholder - will implement when needed
        raise NotImplementedError("Embedding retriever will be implemented later")

    def index_tools(self, tools_data: Dict[str, Any]) -> None:
        """Index tools using embeddings"""
        # TODO: Implement embedding-based indexing
        pass

    def retrieve_similar_tools(self, query: str, top_k: int = 10, threshold: float = 0.3) -> List[ToolSimilarityResult]:
        """Retrieve using embedding similarity"""
        # TODO: Implement embedding-based retrieval
        pass


if __name__ == "__main__":
    # Test the retriever
    print("Testing spaCy Tool Retriever...")

    # Create test tools data
    test_tools = {
        "tool_1": {
            "name": "create_job_posting",
            "description": "Create and publish job postings for recruitment",
            "server_id": "hr_server",
            "server_name": "HR Management System",
            "categories": ["hr", "recruitment"],
            "keywords": ["job", "posting", "recruitment", "hiring"]
        },
        "tool_2": {
            "name": "screen_resume",
            "description": "Automatically screen and evaluate candidate resumes",
            "server_id": "hr_server",
            "server_name": "HR Management System",
            "categories": ["hr", "screening"],
            "keywords": ["resume", "cv", "screening", "evaluation"]
        },
        "tool_3": {
            "name": "generate_report",
            "description": "Generate analytics reports and data visualizations",
            "server_id": "analytics_server",
            "server_name": "Analytics Platform",
            "categories": ["analytics", "reporting"],
            "keywords": ["report", "analytics", "data", "visualization"]
        }
    }

    # Test retriever
    manager = ToolRetrieverManager("spacy")
    manager.retriever.index_tools(test_tools)

    # Test queries
    test_queries = [
        "I need to hire new employees and post job openings",
        "Help me analyze recruitment data and create reports",
        "Screen candidates and evaluate their qualifications"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        results = manager.retrieve_for_agent_description(query, top_k=3, threshold=0.2)

        for result in results:
            print(f"  - {result.tool_name}: {result.similarity_score:.3f}")
            print(f"    Matched: {', '.join(result.matched_features)}")

    print(f"\nRetriever info: {manager.get_retriever_info()}")