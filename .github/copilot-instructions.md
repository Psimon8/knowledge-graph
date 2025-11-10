# Knowledge Graph Explorer - AI Agent Instructions

## Project Overview
This is a **refactored and enhanced** Streamlit application that extracts knowledge graphs from text using LangChain's `LLMGraphTransformer` with OpenAI models. The app converts unstructured text into interactive graph visualizations using PyVis, with support for multiple documents, advanced filtering, and entity exploration.

**Architecture**: Modular 2-file structure with enhanced capabilities
- `app.py` - Streamlit UI with 3 input modes, advanced configuration, and entity explorer
- `generate_knowledge_graph.py` - Refactored core with parameterized functions, logging, and better error handling
- `knowledge_graph.ipynb` - Jupyter notebook for experimentation

## Critical Setup Requirements

### Environment Configuration
**ALWAYS** ensure `.env` file exists in project root with:
```bash
OPENAI_API_KEY=your_actual_api_key_here
```

The refactored code validates API key at import time (line 20-24 in `generate_knowledge_graph.py`) and raises `ValueError` with helpful message if missing. Use `.env.example` as template.

### Running the Application
```bash
streamlit run app.py
```
Application runs on `http://localhost:8501` by default.

## Code Architecture & Patterns

### Modular Function Design
The refactored `generate_knowledge_graph.py` uses **factory pattern** for LLM creation:

```python
create_llm(model_name, temperature)  # Creates ChatOpenAI instance
create_graph_transformer(llm, allowed_nodes, allowed_relationships)  # Creates transformer
```

**Why this matters**: Enables dynamic model switching and constraint configuration from UI without code changes.

### Enhanced Error Handling
All functions use **try/except with logging** instead of silent failures:
- `logger.info()` for successful operations
- `logger.warning()` for skipped items
- `logger.error()` for failures
- Exceptions propagate to Streamlit for user-friendly error display

### Async Pattern (Unchanged)
- `extract_graph_data()` remains async with `aconvert_to_graph_documents()`
- `generate_knowledge_graph()` wraps with `asyncio.run()`
- Required by LangChain's experimental API

### Function Return Values
**IMPORTANT**: `generate_knowledge_graph()` now returns `(net, graph_documents)` tuple instead of just `net`:
```python
net, graph_docs = generate_knowledge_graph(text, model_name=..., ...)
```
This enables entity exploration and data export features in the UI.

## New Features & Implementation

### 1. Multi-Input Modes
Three input methods in `app.py`:
- **"📤 Upload txt"**: Single file upload (original)
- **"✍️ Input text"**: Direct text area (original)
- **"📚 Multiple texts"**: NEW - combines multiple texts with `\n\n---\n\n` separator

All modes use same underlying `generate_knowledge_graph()` with configurable parameters.

### 2. Advanced Configuration
UI exposes previously hardcoded parameters:

**Model Selection** (lines 38-46):
- `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, `gpt-3.5-turbo`
- Temperature slider (0.0-1.0)

**Graph Constraints** (lines 49-73):
- Optional `allowed_nodes` list (e.g., `["Person", "Organization"]`)
- Optional `allowed_relationships` tuples (e.g., `[("Person", "WORKS_AT", "Organization")]`)

**Visualization Settings** (lines 75-79):
- Adjustable graph height (600-2000px)
- Color pickers for background and font

### 3. Entity Explorer
NEW section (lines 289-332) displays after graph generation:
- DataFrames showing all nodes and relationships
- Search functionality to find entities by name
- Shows connections for matched entities (both incoming and outgoing)

**Implementation**: Uses `st.session_state` to persist `graph_documents` across interactions.

### 4. Export Options
Download buttons for both JSON and HTML formats:
- JSON structure: `{"nodes": [...], "relationships": [...]}`
- HTML: Complete interactive visualization

### 5. Enhanced UI/UX
- Custom CSS styling (lines 20-34)
- Metrics display: node count, relationship count, model name
- Collapsible expanders for advanced settings
- Progress spinners with descriptive messages
- Success/error notifications with emoji icons

## Key Configuration Details

### Model Comparison
Models are **not** equivalent - choose based on use case:
- `gpt-4o`: Best accuracy, higher cost ($$$)
- `gpt-4o-mini`: Recommended for production (fast + affordable)
- `gpt-4-turbo`: Balanced option
- `gpt-3.5-turbo`: Testing only (lower accuracy)

### PyVis Visualization
Visualization settings (lines 100-122 in `generate_knowledge_graph.py`):
- Dark theme: `bgcolor="#222222"` (customizable via UI)
- ForceAtlas2Based physics (unchanged from original)
- `filter_menu=True` enables node/edge filtering
- `cdn_resources='remote'` for Streamlit Cloud compatibility

### Logging Strategy
Uses Python `logging` module (lines 11-13):
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```
Logs appear in terminal/Streamlit Cloud logs for debugging.

## Deployment Considerations

### Streamlit Cloud
1. Set secrets in dashboard (not `.env` file):
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
2. Use `requirements.txt` for dependencies
3. Logs available in "Manage app" dashboard

### Environment Variables
Access via `os.getenv()` - works in both local and cloud:
```python
api_key = os.getenv("OPENAI_API_KEY")
```

### File Persistence
Generated `knowledge_graph.html` is temporary and overwritten on each generation. For persistence:
- Use unique filenames with timestamps
- Store in cloud storage (S3, GCS)
- Or rely on export functionality

## Common Workflows

### Adding New Node Types
1. User enters types in UI (comma-separated)
2. Parsed to list: `[n.strip() for n in input.split(",")]`
3. Passed to `create_graph_transformer(allowed_nodes=...)`
4. LLM only extracts specified types

### Multi-Document Analysis
1. User enters number of texts
2. Each text collected in list
3. Combined with `"\n\n---\n\n".join(texts)`
4. Processed as single document
5. Entities/relationships merged automatically

### Debugging Graph Issues
1. Check terminal logs for extraction details
2. Verify node/edge counts in logs vs UI metrics
3. Use Entity Explorer to inspect extracted data
4. Export as JSON to examine raw structure

## Migration Notes (Original → Refactored)

**Breaking Changes:**
1. `generate_knowledge_graph()` returns tuple instead of single value
2. Must pass `graph_transformer` to `extract_graph_data()`
3. `save_graph()` is now separate function (was inline)

**Improvements:**
- Better error messages with context
- Logging throughout pipeline
- Configurable parameters (no hardcoding)
- Separated concerns (creation vs visualization vs saving)

## Performance Optimization

### Caching (Not Yet Implemented)
Consider adding Streamlit caching for expensive operations:
```python
@st.cache_data(ttl=3600)
def cached_generate_knowledge_graph(text, model_name, temperature):
    # Existing logic
```

### Rate Limiting
Not implemented - consider for production:
- Track API calls per user
- Implement exponential backoff
- Set max text length limits

## Common Issues

**"Tuple has no save_graph member"**
- Old code tried `net.save_graph()` on tuple
- Fixed: Use `save_graph(net, filename)` function

**Empty graph despite long text**
- LLM may not extract entities from informal/unstructured text
- Try: More factual text, lower temperature, constrained node types

**API key errors on Streamlit Cloud**
- Must set in Secrets (not `.env`)
- Key name must be exact: `OPENAI_API_KEY`
- Restart app after updating secrets
