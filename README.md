# Knowledge Graph Explorer 🕸️

An advanced Streamlit application that extracts knowledge graphs from text using LangChain and OpenAI's GPT models, with interactive graph visualizations powered by PyVis.

![CleanShot 2025-05-28 at 13 11 46](https://github.com/user-attachments/assets/4fef9158-8dd8-432d-bb8a-b53953a82c6c)

👉 This repo is part of my project tutorial on Youtube:
[![](https://img.youtube.com/vi/O-T_6KOXML4/0.jpg)](https://www.youtube.com/watch?v=O-T_6KOXML4)

## ✨ Features

### Core Features
- **Multiple input methods**: Upload .txt files, direct text input, or analyze multiple texts simultaneously
- **Interactive knowledge graph visualization**: Drag, zoom, filter nodes and edges
- **Customizable graph display**: Physics-based layout with adjustable visual settings
- **Advanced entity extraction**: Powered by OpenAI's GPT-4o and other models

### New Advanced Features 🚀
- **Model selection**: Choose between GPT-4o, GPT-4o-mini, GPT-4-turbo, or GPT-3.5-turbo
- **Temperature control**: Adjust randomness in entity extraction (0 = deterministic)
- **Graph constraints**: Limit extraction to specific node types and relationships
- **Multi-document analysis**: Combine multiple texts into a single knowledge graph
- **Entity explorer**: Search and explore entities with their connections
- **Export options**: Download graphs as JSON or interactive HTML
- **Real-time statistics**: View node count, relationship count, and model info
- **Enhanced error handling**: Better logging and error messages
- **Improved UI/UX**: Modern interface with icons, metrics, and collapsible sections

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Dependencies

The application requires the following Python packages:

- **langchain** (>= 0.1.0): Core LLM framework
- **langchain-experimental** (>= 0.0.45): Experimental LangChain features
- **langchain-openai** (>= 0.1.0): OpenAI integration for LangChain
- **python-dotenv** (>= 1.0.0): Environment variable support
- **pyvis** (>= 0.3.2): Graph visualization
- **streamlit** (>= 1.32.0): Web UI framework

Install all required dependencies:

```bash
pip install -r requirements.txt
```

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/thu-vu92/knowledge-graph-llms.git
   cd knowledge-graph-llms
   ```

2. Create a `.env` file in the root directory with your OpenAI API key:
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your key
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## 🚀 Running the Application

To run the Streamlit app:

```bash
streamlit run app.py
```

This will start the application and open it in your default web browser (typically at <http://localhost:8501>).

## 📖 Usage Guide

### Basic Usage

1. **Choose input method** from the sidebar:
   - 📤 Upload txt file
   - ✍️ Input text directly
   - 📚 Multiple texts (for combined analysis)

2. **Configure model settings** (optional):
   - Select OpenAI model (GPT-4o, GPT-4o-mini, etc.)
   - Adjust temperature (0 = deterministic, 1 = creative)

3. **Set graph constraints** (optional):
   - Limit extraction to specific entity types (Person, Organization, Location, etc.)
   - Define allowed relationship types (e.g., Person→WORKS_AT→Organization)

4. **Generate the graph**:
   - Click "🚀 Generate Knowledge Graph"
   - Wait for extraction and visualization

5. **Explore the results**:
   - Interact with the graph (drag, zoom, filter)
   - View statistics (node count, relationship count)
   - Search for specific entities
   - Export as JSON or HTML

### Advanced Features

#### Multi-Document Analysis
Select "📚 Multiple texts" to analyze several documents together:
- Combines entities and relationships across all texts
- Useful for finding connections between different sources
- Creates a unified knowledge graph

#### Entity Explorer
After generating a graph, use the Entity Explorer to:
- View all extracted nodes and relationships in tables
- Search for specific entities by name
- See all connections for a particular entity
- Understand the graph structure

#### Export Options
Download your knowledge graph in multiple formats:
- **JSON**: Structured data for further processing
- **HTML**: Standalone interactive visualization

## 🔧 Configuration Options

### Model Selection
Choose the right model for your use case:

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| gpt-4o | Medium | High | High accuracy, complex texts |
| gpt-4o-mini | Fast | Low | Quick analysis, cost-effective |
| gpt-4-turbo | Fast | Medium | Balanced performance |
| gpt-3.5-turbo | Very Fast | Very Low | Simple texts, testing |

### Graph Constraints

**Node Type Constraints**: Limit extraction to specific entity types
```
Person, Organization, Location, Event, Concept, Technology
```

**Relationship Constraints**: Define allowed connections
```
Person,WORKS_AT,Organization
Person,FOUNDED,Organization
Organization,LOCATED_IN,Location
```

## 🎨 Customization

### Visual Settings
Adjust the graph appearance:
- **Height**: 600-2000px
- **Background color**: Dark theme by default
- **Font color**: Customize text appearance

### Physics Configuration
The graph uses ForceAtlas2Based physics solver for optimal layout. To customize, edit `generate_knowledge_graph.py`:

```python
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
```

## 🧠 How It Works

The application uses LangChain's experimental graph transformers with OpenAI's GPT models to:

1. Extract entities from the input text
2. Identify relationships between these entities
3. Generate a graph structure representing this information
4. Visualize the graph using PyVis, a Python interface for the vis.js visualization library

### Architecture

```
Text Input → LangChain LLMGraphTransformer → Graph Documents → PyVis Network → Interactive HTML
```

**Key Components:**
- **LangChain**: Manages LLM interactions and graph transformation
- **OpenAI GPT**: Performs natural language understanding and entity extraction
- **PyVis**: Creates interactive network visualizations
- **Streamlit**: Provides the web interface

## 📊 Example Use Cases

1. **Research Paper Analysis**: Extract key concepts, methods, and relationships
2. **Business Document Processing**: Identify organizations, people, and their relationships
3. **Historical Text Analysis**: Map events, figures, and their connections
4. **Legal Document Review**: Extract entities and their legal relationships
5. **News Article Summarization**: Visualize who, what, where, and how

## 🚀 Deployment

For production deployment options, see [DEPLOYMENT.md](DEPLOYMENT.md).

Quick deploy options:
- **Streamlit Cloud**: Free, easiest option ([guide](DEPLOYMENT.md#1-streamlit-community-cloud-recommended---free))
- **Hugging Face Spaces**: Free, good for sharing ([guide](DEPLOYMENT.md#2-hugging-face-spaces-free))
- **Docker**: Self-hosted, full control ([guide](DEPLOYMENT.md#3-local-docker-deployment))

## 🐛 Troubleshooting

### Common Issues

**"OpenAI API key not found"**
- Ensure `.env` file exists in project root
- Variable must be named exactly `OPENAI_API_KEY`
- No quotes around the key value in `.env`

**"Module not found" errors**
```bash
pip install -r requirements.txt --upgrade
```

**Empty graph generated**
- Try longer, more structured text
- Check OpenAI API rate limits
- Verify API key has credits

**Graph doesn't render**
- Ensure proper HTML file generation
- Check browser console for errors
- Try different browser

For more troubleshooting, see [DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

Ideas for contributions:
- Add support for local LLMs (Ollama, LlamaCPP)
- Implement graph database export (Neo4j, ArangoDB)
- Add more visualization options (3D graphs, timelines)
- Improve entity type detection
- Add multi-language support

## 📄 License

This project is licensed under the MIT License - a permissive open source license that allows for free use, modification, and distribution of the software.

For more details, see the [MIT License](https://opensource.org/licenses/MIT) documentation.

## 🙏 Acknowledgments

- [LangChain](https://python.langchain.com/) for the graph transformer framework
- [OpenAI](https://openai.com/) for GPT models
- [PyVis](https://pyvis.readthedocs.io/) for graph visualization
- [Streamlit](https://streamlit.io/) for the web framework

## 📚 Resources

- [YouTube Tutorial](https://www.youtube.com/watch?v=O-T_6KOXML4)
- [LangChain Documentation](https://python.langchain.com/docs/use_cases/graph/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Deployment Guide](DEPLOYMENT.md)

---

**Made with ❤️ for the AI community**
