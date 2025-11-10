# 🚀 Deployment Guide - Knowledge Graph Explorer

## Deployment Options

### 1. Streamlit Community Cloud (Recommended - FREE)

#### Prerequisites
- GitHub account
- OpenAI API key

#### Steps:
1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository and branch
   - Set main file path: `app.py`
   - Click "Deploy!"

3. **Configure Secrets**
   - In Streamlit Cloud dashboard, go to your app settings
   - Navigate to "Secrets"
   - Add your OpenAI API key:
     ```toml
     OPENAI_API_KEY = "sk-your-actual-key-here"
     ```

### 2. Hugging Face Spaces (FREE)

#### Steps:
1. Create a new Space on [huggingface.co/spaces](https://huggingface.co/spaces)
2. Choose "Streamlit" as the SDK
3. Upload your files or connect to GitHub
4. Add secrets in Settings → Repository secrets:
   - Key: `OPENAI_API_KEY`
   - Value: Your OpenAI API key

5. Create `requirements.txt` if not exists (already included)

### 3. Local Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

#### Build and run:
```bash
docker build -t knowledge-graph-app .
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key knowledge-graph-app
```

### 4. Heroku Deployment

1. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Deploy:
   ```bash
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your_key
   git push heroku main
   ```

### 5. AWS EC2 / DigitalOcean

#### Setup script:
```bash
# Install Python and pip
sudo apt update
sudo apt install python3-pip -y

# Clone repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Install dependencies
pip3 install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your_key_here" > .env

# Run with nohup
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
```

## Performance Optimization Tips

### 1. Caching for Better Performance
Add to `generate_knowledge_graph.py`:
```python
import streamlit as st

@st.cache_data(ttl=3600)
def cached_generate_knowledge_graph(text, model_name, temperature):
    # Your existing code
    pass
```

### 2. Rate Limiting
Consider implementing rate limiting for API calls to avoid excessive costs.

### 3. Cost Management
- Use `gpt-4o-mini` for lower cost (faster, cheaper)
- Set token limits in OpenAI API calls
- Monitor usage via OpenAI dashboard

## Model Suggestions & Improvements

### Recommended Models by Use Case:

| Use Case | Model | Pros | Cost |
|----------|-------|------|------|
| **Production** | gpt-4o-mini | Fast, cost-effective, good accuracy | $ |
| **High Accuracy** | gpt-4o | Best accuracy, detailed extraction | $$$ |
| **Balanced** | gpt-4-turbo | Good balance of speed & accuracy | $$ |
| **Quick Tests** | gpt-3.5-turbo | Fastest, cheapest | $ |

### Improvements to Consider:

1. **Add Local LLM Support**
   - Use Ollama with local models (Llama 3, Mistral)
   - No API costs, better privacy
   - Update `generate_knowledge_graph.py` to support local models

2. **Batch Processing**
   - Process multiple documents in parallel
   - Queue system for large documents

3. **Graph Database Integration**
   - Export to Neo4j for advanced queries
   - Store graphs persistently

4. **Enhanced Visualization**
   - Add 3D graph view
   - Timeline view for temporal relationships
   - Clustering/community detection

5. **API Endpoint**
   - Create FastAPI wrapper
   - RESTful API for programmatic access

## Monitoring & Logging

### Streamlit Cloud
- Built-in logs in app dashboard
- Monitor app health and errors

### Custom Logging
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

## Security Best Practices

1. **Never commit .env files**
   - Always use `.gitignore`
   - Use environment variables

2. **API Key Rotation**
   - Rotate OpenAI keys regularly
   - Use separate keys for dev/prod

3. **Input Validation**
   - Limit text size
   - Sanitize user inputs
   - Rate limiting per user

## Troubleshooting

### Common Issues:

**1. "Module not found" errors**
```bash
pip install -r requirements.txt --upgrade
```

**2. OpenAI API errors**
- Check API key validity
- Verify billing/quota on OpenAI platform
- Check rate limits

**3. Memory issues on free hosting**
- Use smaller models (gpt-4o-mini)
- Limit text input size
- Clear cache regularly

**4. Slow graph generation**
- Reduce text length
- Use faster models
- Implement caching

## Support & Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [LangChain Documentation](https://python.langchain.com)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [PyVis Documentation](https://pyvis.readthedocs.io)

## License
MIT License - See LICENSE file for details
