from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from pyvis.network import Network

from dotenv import load_dotenv
import os
import asyncio
from typing import List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the .env file
load_dotenv()

# Get API key from environment variable
# Note: API key validation is deferred to when LLM is actually created
# This allows Streamlit Cloud to inject secrets after module import
api_key = os.getenv("OPENAI_API_KEY")

# Try to get from streamlit secrets if available
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        api_key = st.secrets['OPENAI_API_KEY']
        logger.info("Using API key from Streamlit secrets")
except (ImportError, FileNotFoundError, KeyError):
    pass  # Streamlit not available or secrets not configured


def create_llm(model_name: str = "gpt-4o", temperature: float = 0, api_key_override: Optional[str] = None):
    """
    Create ChatOpenAI instance with specified parameters.
    
    Validates API key and raises helpful error if not found.
    """
    # Get API key - check multiple sources
    # Priority: explicit override > environment / .env loaded value > streamlit secrets
    current_api_key = api_key_override if api_key_override else api_key
    
    # Try streamlit secrets if api_key is None
    if not current_api_key:
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                current_api_key = st.secrets['OPENAI_API_KEY']
        except (ImportError, FileNotFoundError, KeyError, AttributeError):
            pass
    
    # Validate API key
    if not current_api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. "
            "For local development: Create a .env file with OPENAI_API_KEY=your_key_here. "
            "For Streamlit Cloud: Add OPENAI_API_KEY to your app secrets in the dashboard, or paste it into the API key field in the sidebar."
        )

    return ChatOpenAI(temperature=temperature, model_name=model_name, api_key=current_api_key)


def create_graph_transformer(
    llm,
    allowed_nodes: Optional[List[str]] = None,
    allowed_relationships: Optional[List[Tuple[str, str, str]]] = None
):
    """Create LLMGraphTransformer with optional constraints."""
    kwargs = {"llm": llm}
    if allowed_nodes:
        kwargs["allowed_nodes"] = allowed_nodes
    if allowed_relationships:
        kwargs["allowed_relationships"] = allowed_relationships
    return LLMGraphTransformer(**kwargs)


# Extract graph data from input text
async def extract_graph_data(
    text: str,
    graph_transformer
) -> List:
    """
    Asynchronously extracts graph data from input text using a graph transformer.

    Args:
        text (str): Input text to be processed into graph format.
        graph_transformer: LLMGraphTransformer instance to use.

    Returns:
        list: A list of GraphDocument objects containing nodes and relationships.
    """
    try:
        documents = [Document(page_content=text)]
        graph_documents = await graph_transformer.aconvert_to_graph_documents(documents)
        logger.info(f"Successfully extracted {len(graph_documents)} graph documents")
        return graph_documents
    except Exception as e:
        logger.error(f"Error extracting graph data: {e}")
        raise


def visualize_graph(
    graph_documents,
    height: str = "1200px",
    width: str = "100%",
    bgcolor: str = "#222222",
    font_color: str = "white",
    notebook: bool = False,
    filter_menu: bool = True
):
    """
    Visualizes a knowledge graph using PyVis based on the extracted graph documents.

    Args:
        graph_documents (list): A list of GraphDocument objects with nodes and relationships.
        height (str): Height of the visualization.
        width (str): Width of the visualization.
        bgcolor (str): Background color.
        font_color (str): Font color.
        notebook (bool): Whether running in notebook environment.
        filter_menu (bool): Whether to show filter menu.

    Returns:
        pyvis.network.Network: The visualized network graph object, or None if error.
    """
    try:
        if not graph_documents or len(graph_documents) == 0:
            logger.warning("No graph documents to visualize")
            return None
            
        # Create network
        net = Network(
            height=height,
            width=width,
            directed=True,
            notebook=notebook,
            bgcolor=bgcolor,
            font_color=font_color,
            filter_menu=filter_menu,
            cdn_resources='remote'
        )

        nodes = graph_documents[0].nodes
        relationships = graph_documents[0].relationships
        
        logger.info(f"Processing {len(nodes)} nodes and {len(relationships)} relationships")

        # Build lookup for valid nodes
        node_dict = {node.id: node for node in nodes}
        
        # Filter out invalid edges and collect valid node IDs
        valid_edges = []
        valid_node_ids = set()
        for rel in relationships:
            if rel.source.id in node_dict and rel.target.id in node_dict:
                valid_edges.append(rel)
                valid_node_ids.update([rel.source.id, rel.target.id])

        logger.info(f"Found {len(valid_node_ids)} valid nodes and {len(valid_edges)} valid edges")

        # Track which nodes are part of any relationship
        connected_node_ids = set()
        for rel in relationships:
            connected_node_ids.add(rel.source.id)
            connected_node_ids.add(rel.target.id)

        # Add valid nodes to the graph
        nodes_added = 0
        for node_id in valid_node_ids:
            node = node_dict[node_id]
            try:
                net.add_node(node.id, label=node.id, title=node.type, group=node.type)
                nodes_added += 1
            except Exception as e:
                logger.warning(f"Could not add node {node.id}: {e}")
                continue

        # Add valid edges to the graph
        edges_added = 0
        for rel in valid_edges:
            try:
                net.add_edge(rel.source.id, rel.target.id, label=rel.type.lower())
                edges_added += 1
            except Exception as e:
                logger.warning(f"Could not add edge from {rel.source.id} to {rel.target.id}: {e}")
                continue

        logger.info(f"Added {nodes_added} nodes and {edges_added} edges to visualization")

        # Configure graph layout and physics
        net.set_options("""
            {
                "physics": {
                    "forceAtlas2Based": {
                        "gravitationalConstant": -100,
                        "centralGravity": 0.01,
                        "springLength": 200,
                        "springConstant": 0.08
                    },
                    "minVelocity": 0.75,
                    "solver": "forceAtlas2Based"
                }
            }
        """)

        return net
        
    except Exception as e:
        logger.error(f"Error visualizing graph: {e}")
        return None


def save_graph(net, output_file: str = "knowledge_graph.html") -> bool:
    """
    Save the graph to an HTML file.
    
    Args:
        net: PyVis Network object
        output_file: Output filename
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        net.save_graph(output_file)
        logger.info(f"Graph saved to {os.path.abspath(output_file)}")
        return True
    except Exception as e:
        logger.error(f"Error saving graph: {e}")
        return False


def generate_knowledge_graph(
    text: str,
    model_name: str = "gpt-4o",
    temperature: float = 0,
    allowed_nodes: Optional[List[str]] = None,
    allowed_relationships: Optional[List[Tuple[str, str, str]]] = None,
    output_file: str = "knowledge_graph.html",
    api_key: Optional[str] = None
):
    """
    Generates and visualizes a knowledge graph from input text.

    This function runs the graph extraction asynchronously and then visualizes
    the resulting graph using PyVis.

    Args:
        text (str): Input text to convert into a knowledge graph.
        model_name (str): OpenAI model to use (default: gpt-4o).
        temperature (float): LLM temperature for extraction (default: 0).
        allowed_nodes (list): Optional list of allowed node types.
        allowed_relationships (list): Optional list of allowed relationship tuples.
        output_file (str): Output HTML filename.

    Returns:
        tuple: (pyvis.network.Network, graph_documents) or (None, None) if error.
    """
    try:
        # Create LLM and transformer (pass optional api_key from caller)
        llm = create_llm(model_name=model_name, temperature=temperature, api_key_override=api_key)
        graph_transformer = create_graph_transformer(
            llm=llm,
            allowed_nodes=allowed_nodes,
            allowed_relationships=allowed_relationships
        )

        # Extract graph data
        graph_documents = asyncio.run(extract_graph_data(text, graph_transformer))

        if not graph_documents:
            logger.warning("No graph documents extracted")
            return None, None

        # Visualize
        net = visualize_graph(graph_documents)

        if net:
            # Save graph
            save_graph(net, output_file)
            return net, graph_documents
        else:
            return None, graph_documents

    except Exception as e:
        logger.error(f"Error generating knowledge graph: {e}")
        raise