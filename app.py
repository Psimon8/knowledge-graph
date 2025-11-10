# Import necessary modules
import streamlit as st
import streamlit.components.v1 as components
from generate_knowledge_graph import generate_knowledge_graph
import json
import os

# Set up Streamlit page configuration
st.set_page_config(
    page_title="Knowledge Graph Explorer",
    page_icon="🕸️", 
    layout="wide",
    initial_sidebar_state="expanded", 
    menu_items={
        'About': "Knowledge Graph Generator using LangChain and OpenAI GPT-4o"
    }
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stats-box {
        padding: 1rem;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Set the title of the app
st.markdown('<h1 class="main-header">🕸️ Knowledge Graph Explorer</h1>', unsafe_allow_html=True)
st.markdown("**Extract entities and relationships from text using AI-powered graph analysis**")

# Initialize session state for storing graph data
if 'graph_data' not in st.session_state:
    st.session_state.graph_data = None
if 'graph_documents' not in st.session_state:
    st.session_state.graph_documents = None

# Sidebar section for configuration
st.sidebar.title("⚙️ Configuration")

# Model configuration
with st.sidebar.expander("🤖 Model Settings", expanded=False):
    model_name = st.selectbox(
        "Select Model",
        ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        help="Choose the OpenAI model for entity extraction"
    )
    
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.1,
        help="Higher values make output more random, lower values more deterministic"
    )

    # API key input (optional) - allows pasting key for the session
    st.markdown("---")
    api_from_env = None
    try:
        # Show hint if key is already in streamlit secrets
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            api_from_env = st.secrets['OPENAI_API_KEY']
    except Exception:
        api_from_env = None

    api_key_input = st.text_input(
        "OpenAI API Key (optional)",
        value="" if not api_from_env else api_from_env,
        type="password",
        help="Paste your OpenAI API key for this session. For Streamlit Cloud prefer using Secrets."
    )

    # Store API key in session state so it can be passed to backend functions
    if api_key_input:
        st.session_state['OPENAI_API_KEY'] = api_key_input
    elif 'OPENAI_API_KEY' not in st.session_state and api_from_env:
        st.session_state['OPENAI_API_KEY'] = api_from_env

# Advanced graph constraints
with st.sidebar.expander("🎯 Graph Constraints (Optional)", expanded=False):
    use_node_constraints = st.checkbox("Limit node types", value=False)
    allowed_nodes = None
    if use_node_constraints:
        node_types_input = st.text_area(
            "Allowed node types (comma-separated)",
            "Person, Organization, Location, Event, Concept",
            help="Only extract these types of entities"
        )
        allowed_nodes = [n.strip() for n in node_types_input.split(",") if n.strip()]
        st.info(f"Will extract: {', '.join(allowed_nodes)}")
    
    use_rel_constraints = st.checkbox("Limit relationship types", value=False)
    allowed_relationships = None
    if use_rel_constraints:
        st.markdown("**Define relationships (format: Source,Relation,Target)**")
        rel_input = st.text_area(
            "Relationships (one per line)",
            "Person,WORKS_AT,Organization\nPerson,LOCATED_IN,Location",
            help="Example: Person,FOUNDED,Organization"
        )
        allowed_relationships = []
        for line in rel_input.split("\n"):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) == 3:
                allowed_relationships.append(tuple(parts))
        if allowed_relationships:
            st.info(f"{len(allowed_relationships)} relationship types defined")

# Visualization settings
with st.sidebar.expander("🎨 Visualization Settings", expanded=False):
    graph_height = st.slider("Graph height (px)", 600, 2000, 1200, 100)
    bgcolor = st.color_picker("Background color", "#222222")
    font_color = st.color_picker("Font color", "#FFFFFF")

st.sidebar.markdown("---")
st.sidebar.title("📄 Input Document")

# Input method selection
input_method = st.sidebar.radio(
    "Choose input method:",
    ["📤 Upload txt", "✍️ Input text", "📚 Multiple texts"],
    help="Select how you want to provide the text for analysis"
)

# Case 1: User chooses to upload a .txt file
if input_method == "📤 Upload txt":
    uploaded_file = st.sidebar.file_uploader(
        label="Upload file",
        type=["txt"],
        help="Upload a text file (.txt) to generate knowledge graph"
    )
    
    if uploaded_file is not None:
        try:
            text = uploaded_file.read().decode("utf-8")
            
            st.info(f"**File:** {uploaded_file.name} | **Size:** {len(text)} characters")
            
            with st.expander("📖 Preview text", expanded=False):
                st.text(text[:1000] + ("..." if len(text) > 1000 else ""))
 
            if st.sidebar.button("🚀 Generate Knowledge Graph", type="primary"):
                with st.spinner("🔄 Extracting entities and relationships..."):
                    try:
                        net, graph_docs = generate_knowledge_graph(
                            text,
                            model_name=model_name,
                            temperature=temperature,
                            allowed_nodes=allowed_nodes,
                            allowed_relationships=allowed_relationships,
                            api_key=st.session_state.get('OPENAI_API_KEY')
                        )
                        
                        if net and graph_docs:
                            st.session_state.graph_data = net
                            st.session_state.graph_documents = graph_docs
                            
                            st.success("✅ Knowledge graph generated successfully!")
                            
                            # Display statistics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📊 Nodes", len(graph_docs[0].nodes))
                            with col2:
                                st.metric("🔗 Relationships", len(graph_docs[0].relationships))
                            with col3:
                                st.metric("📝 Model", model_name)
                            
                            # Display the graph
                            output_file = "knowledge_graph.html"
                            HtmlFile = open(output_file, 'r', encoding='utf-8')
                            components.html(HtmlFile.read(), height=graph_height)
                            
                            # Export options
                            st.markdown("---")
                            st.subheader("💾 Export Options")
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Export graph data as JSON
                                graph_json = {
                                    "nodes": [
                                        {"id": n.id, "type": n.type}
                                        for n in graph_docs[0].nodes
                                    ],
                                    "relationships": [
                                        {
                                            "source": r.source.id,
                                            "target": r.target.id,
                                            "type": r.type
                                        }
                                        for r in graph_docs[0].relationships
                                    ]
                                }
                                st.download_button(
                                    label="📥 Download as JSON",
                                    data=json.dumps(graph_json, indent=2),
                                    file_name="knowledge_graph.json",
                                    mime="application/json"
                                )
                            
                            with col2:
                                # Export HTML
                                with open(output_file, 'r', encoding='utf-8') as f:
                                    html_content = f.read()
                                st.download_button(
                                    label="📥 Download as HTML",
                                    data=html_content,
                                    file_name="knowledge_graph.html",
                                    mime="text/html"
                                )
                        else:
                            st.error("❌ Failed to generate graph. Please check your input text.")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.info("💡 Make sure your OPENAI_API_KEY is set in the .env file")
        
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

# Case 2: User chooses to directly input text
elif input_method == "✍️ Input text":
    text = st.sidebar.text_area(
        "Input text",
        height=300,
        placeholder="Paste your text here...",
        help="Enter the text you want to analyze"
    )

    if text:
        st.info(f"**Text length:** {len(text)} characters")
        
        if st.sidebar.button("🚀 Generate Knowledge Graph", type="primary"):
            with st.spinner("🔄 Extracting entities and relationships..."):
                try:
                    net, graph_docs = generate_knowledge_graph(
                        text,
                        model_name=model_name,
                        temperature=temperature,
                        allowed_nodes=allowed_nodes,
                        allowed_relationships=allowed_relationships,
                        api_key=st.session_state.get('OPENAI_API_KEY')
                    )
                    
                    if net and graph_docs:
                        st.session_state.graph_data = net
                        st.session_state.graph_documents = graph_docs
                        
                        st.success("✅ Knowledge graph generated successfully!")
                        
                        # Display statistics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📊 Nodes", len(graph_docs[0].nodes))
                        with col2:
                            st.metric("🔗 Relationships", len(graph_docs[0].relationships))
                        with col3:
                            st.metric("📝 Model", model_name)
                        
                        # Display the graph
                        output_file = "knowledge_graph.html"
                        HtmlFile = open(output_file, 'r', encoding='utf-8')
                        components.html(HtmlFile.read(), height=graph_height)
                        
                        # Export options
                        st.markdown("---")
                        st.subheader("💾 Export Options")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            graph_json = {
                                "nodes": [
                                    {"id": n.id, "type": n.type}
                                    for n in graph_docs[0].nodes
                                ],
                                "relationships": [
                                    {
                                        "source": r.source.id,
                                        "target": r.target.id,
                                        "type": r.type
                                    }
                                    for r in graph_docs[0].relationships
                                ]
                            }
                            st.download_button(
                                label="📥 Download as JSON",
                                data=json.dumps(graph_json, indent=2),
                                file_name="knowledge_graph.json",
                                mime="application/json"
                            )
                        
                        with col2:
                            with open(output_file, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            st.download_button(
                                label="📥 Download as HTML",
                                data=html_content,
                                file_name="knowledge_graph.html",
                                mime="text/html"
                            )
                    else:
                        st.error("❌ Failed to generate graph. Please check your input text.")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Make sure your OPENAI_API_KEY is set in the .env file")

# Case 3: Multiple texts analysis
elif input_method == "📚 Multiple texts":
    st.markdown("### Analyze Multiple Documents")
    st.info("Upload or enter multiple texts to create a combined knowledge graph")
    
    num_texts = st.sidebar.number_input("Number of texts", min_value=2, max_value=10, value=2)
    
    texts = []
    for i in range(num_texts):
        with st.expander(f"📄 Text {i+1}", expanded=(i==0)):
            text_input = st.text_area(
                f"Enter text {i+1}",
                height=150,
                key=f"text_{i}",
                placeholder=f"Paste text {i+1} here..."
            )
            if text_input:
                texts.append(text_input)
    
    if len(texts) >= 2:
        st.info(f"**Ready to analyze {len(texts)} texts**")
        
        if st.sidebar.button("🚀 Generate Combined Graph", type="primary"):
            combined_text = "\n\n---\n\n".join(texts)
            
            with st.spinner("🔄 Extracting entities and relationships from multiple texts..."):
                try:
                    net, graph_docs = generate_knowledge_graph(
                        combined_text,
                        model_name=model_name,
                        temperature=temperature,
                        allowed_nodes=allowed_nodes,
                        allowed_relationships=allowed_relationships,
                        api_key=st.session_state.get('OPENAI_API_KEY')
                    )
                    
                    if net and graph_docs:
                        st.session_state.graph_data = net
                        st.session_state.graph_documents = graph_docs
                        
                        st.success(f"✅ Combined knowledge graph from {len(texts)} texts generated!")
                        
                        # Display statistics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📄 Texts", len(texts))
                        with col2:
                            st.metric("📊 Nodes", len(graph_docs[0].nodes))
                        with col3:
                            st.metric("🔗 Relationships", len(graph_docs[0].relationships))
                        with col4:
                            st.metric("📝 Model", model_name)
                        
                        # Display the graph
                        output_file = "knowledge_graph.html"
                        HtmlFile = open(output_file, 'r', encoding='utf-8')
                        components.html(HtmlFile.read(), height=graph_height)
                        
                        # Export options
                        st.markdown("---")
                        st.subheader("💾 Export Options")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            graph_json = {
                                "nodes": [
                                    {"id": n.id, "type": n.type}
                                    for n in graph_docs[0].nodes
                                ],
                                "relationships": [
                                    {
                                        "source": r.source.id,
                                        "target": r.target.id,
                                        "type": r.type
                                    }
                                    for r in graph_docs[0].relationships
                                ]
                            }
                            st.download_button(
                                label="📥 Download as JSON",
                                data=json.dumps(graph_json, indent=2),
                                file_name="knowledge_graph_combined.json",
                                mime="application/json"
                            )
                        
                        with col2:
                            with open(output_file, 'r', encoding='utf-8') as f:
                                html_content = f.read()
                            st.download_button(
                                label="📥 Download as HTML",
                                data=html_content,
                                file_name="knowledge_graph_combined.html",
                                mime="text/html"
                            )
                    else:
                        st.error("❌ Failed to generate graph. Please check your input texts.")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Make sure your OPENAI_API_KEY is set in the .env file")
    else:
        st.warning(f"⚠️ Please enter at least 2 texts to continue (currently: {len(texts)})")

# Display entity explorer if graph exists
if st.session_state.graph_documents:
    st.markdown("---")
    st.subheader("🔍 Entity Explorer")
    
    graph_docs = st.session_state.graph_documents
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Nodes (Entities)**")
        nodes_data = [
            {"ID": n.id, "Type": n.type}
            for n in graph_docs[0].nodes
        ]
        st.dataframe(nodes_data, use_container_width=True)
    
    with col2:
        st.markdown("**🔗 Relationships**")
        rels_data = [
            {
                "Source": r.source.id,
                "Relation": r.type,
                "Target": r.target.id
            }
            for r in graph_docs[0].relationships
        ]
        st.dataframe(rels_data, use_container_width=True)
    
    # Entity search
    st.markdown("**🔎 Search for an entity**")
    search_term = st.text_input("Enter entity name", placeholder="e.g., Albert Einstein")
    
    if search_term:
        # Find matching nodes
        matching_nodes = [
            n for n in graph_docs[0].nodes
            if search_term.lower() in n.id.lower()
        ]
        
        if matching_nodes:
            st.success(f"Found {len(matching_nodes)} matching entities")
            for node in matching_nodes:
                st.write(f"**{node.id}** ({node.type})")
                
                # Find related relationships
                related_rels = [
                    r for r in graph_docs[0].relationships
                    if r.source.id == node.id or r.target.id == node.id
                ]
                
                if related_rels:
                    st.markdown("Connections:")
                    for rel in related_rels:
                        if rel.source.id == node.id:
                            st.write(f"  → {rel.type} → **{rel.target.id}**")
                        else:
                            st.write(f"  ← {rel.type} ← **{rel.source.id}**")
        else:
            st.warning("No matching entities found")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ using LangChain, OpenAI GPT-4o, and PyVis</p>
        <p>⚡ Powered by Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)