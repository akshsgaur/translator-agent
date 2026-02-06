# 🌐 Translator Agent - Advanced AI-Powered Language Translation System

A sophisticated **AI-powered translation agent** built with **LangChain orchestration**, **Ollama local models**, and **LangSmith observability**. This desktop application provides intelligent translation capabilities with memory, context awareness, and comprehensive analytics.

## ✨ Key Features

### 🤖 Agent-Based Architecture
- **Smart Translation Agent**: LangChain-powered agent with tool orchestration
- **Multi-Model Support**: Specialized models for translation vs reasoning tasks
- **Context Awareness**: Maintains conversation history and context
- **Tool Integration**: Automatic tool selection and execution

### 🧠 Advanced Memory System
- **Semantic Search**: Mem0 with Ollama embeddings for intelligent retrieval
- **Translation History**: Store and retrieve all translations for review
- **Learning Analytics**: Comprehensive progress tracking and statistics
- **Persistent Storage**: SQLite database for user data and preferences

### 📊 Observability & Monitoring
- **LangSmith Integration**: Full tracing of AI interactions and decisions
- **Real-time Monitoring**: Track all agent runs, tool calls, and responses
- **Performance Analytics**: Monitor response times, success rates, and usage patterns
- **Debug Support**: Detailed logs for troubleshooting and optimization

### 🖥️ Modern Desktop Interface
- **CustomTkinter GUI**: Modern, responsive desktop application
- **Multi-Tab Interface**: Organized workflow with different functional areas
- **Real-time Feedback**: Immediate progress tracking and status updates
- **Export/Import**: Data portability and backup capabilities

## 🛠️ Technology Stack

### Core AI Framework
- **🔗 LangChain**: Agent orchestration and tool management
- **🦙 Ollama**: Local model serving with privacy-first approach
- **📊 LangSmith**: Enterprise-grade observability and monitoring
- **🧠 Mem0**: Advanced memory with semantic search capabilities

### AI Models
- **🔄 translategemma:4b**: Specialized translation model for high-quality translations
- **🧠 mixtral:8x7b**: Advanced reasoning for complex language tasks
- **🔍 mxbai-embed-large**: Text embeddings for semantic memory search

### Development Stack
- **🖥️ CustomTkinter**: Modern GUI framework for desktop applications
- **💾 SQLite**: Local database for user data and analytics
- **🐍 Python 3.8+**: Core programming language
- **📦 PyInstaller**: Application packaging and distribution

## 🚀 Quick Start

### Prerequisites
1. **Python 3.8+** installed
2. **Ollama** installed and running locally
3. **LangSmith Account** (optional but recommended for observability)

### Installation Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/akshsgaur/translator-agent.git
cd translator-agent
```

#### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Set Up Ollama Models
```bash
# Install and start Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve

# Pull required AI models
ollama pull translategemma:4b      # Translation model
ollama pull mixtral:8x7b           # Reasoning model
ollama pull mxbai-embed-large     # Embedding model
```

#### 5. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# Add your LangSmith API key (optional but recommended)
```

#### 6. Run the Application
```bash
python main_enhanced.py
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with the following configuration:

```bash
# LangSmith Configuration (Optional but Recommended)
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_PROJECT=translator-agent

# Model Configuration
TRANSLATION_MODEL=translategemma:4b
REASONING_MODEL=mixtral:8x7b
EMBEDDING_MODEL=mxbai-embed-large

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
```

### LangSmith Setup (Optional)
1. Visit [LangSmith](https://smith.langchain.com/)
2. Create an account and obtain your API key
3. Create a new project for your translator agent
4. Add the API key to your `.env` file

## 📱 Application Interface

### Main Features

#### 🗣️ Smart Translation
- **Multi-language Support**: Translate between 20+ languages
- **Context-Aware**: Maintains conversation context for better translations
- **Quality Detection**: Automatic detection of source language
- **Translation Memory**: Stores and reuses previous translations

#### 🤖 Agent Chat
- **Conversational Interface**: Natural language interaction with the AI agent
- **Tool Orchestration**: Agent automatically selects appropriate tools
- **Memory Integration**: Access to translation history and learning data
- **Real-time Responses**: Fast, contextually relevant answers

#### 📚 Learning & Analytics
- **Progress Tracking**: Monitor translation accuracy and usage patterns
- **Performance Metrics**: Track response times and success rates
- **Export Data**: Export translation history and analytics
- **Visual Analytics**: Charts and graphs for learning progress

#### 🔍 Observability Dashboard
- **Live Monitoring**: Real-time view of AI operations
- **Trace Analysis**: Detailed breakdown of agent decision-making
- **Performance Insights**: Identify bottlenecks and optimization opportunities
- **Error Tracking**: Comprehensive error logging and analysis

## 🎯 Advanced Usage

### Custom Tools
Extend the agent's capabilities by adding custom tools:

```python
from langchain.tools import Tool

def custom_translation_function(text: str, source_lang: str, target_lang: str) -> str:
    # Your custom translation logic
    return translated_text

# Add to agent tools
custom_tool = Tool(
    name="advanced_translator",
    description="Advanced translation with custom logic",
    func=custom_translation_function
)
```

### Memory Customization
Configure memory behavior for different use cases:

```python
# Adjust memory window size
from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(
    k=20,  # Number of conversations to remember
    return_messages=True,
    memory_key="chat_history"
)
```

### Custom Model Configuration
Use different models based on your needs:

```python
# In langchain_service.py
tutor_service = LangChainTutorService(
    translation_model="your_custom_model",
    reasoning_model="your_reasoning_model",
    embedding_model="your_embedding_model",
    langsmith_api_key="your_key"
)
```

## 📊 Performance & Analytics

### Tracked Metrics
- **Translation Volume**: Number of translations performed
- **Language Pairs**: Most frequently translated language combinations
- **Response Times**: AI model performance metrics
- **Success Rates**: Translation accuracy and completion rates
- **User Engagement**: Feature usage and interaction patterns

### LangSmith Observability
- **Agent Runs**: Complete trace of every agent interaction
- **Tool Calls**: Detailed logging of all tool executions
- **Memory Operations**: Track memory additions and searches
- **Error Analysis**: Comprehensive error tracking and debugging

## 🔍 Troubleshooting

### Common Issues

**Ollama Connection Error**:
```bash
# Check if Ollama is running
ollama list

# Restart Ollama if needed
ollama serve
```

**Model Not Found**:
```bash
# Pull missing models
ollama pull translategemma:4b
ollama pull mixtral:8x7b
ollama pull mxbai-embed-large
```

**LangSmith Connection Issues**:
- Verify API key is correct in `.env` file
- Check project name matches your LangSmith project
- Ensure internet connectivity for LangSmith access

**Memory Service Errors**:
- Check embedding model is available
- Verify Mem0 configuration
- Restart the application if memory becomes corrupted

### Debug Mode
Enable verbose logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🏗️ Development

### Project Structure
```
translator-agent/
├── src/
│   ├── langchain_service.py      # Core LangChain integration
│   ├── enhanced_memory_service.py # Memory management
│   ├── tutor_app.py              # Main application logic
│   ├── ollama_check.py           # Ollama availability check
│   └── modern_ui_components.py   # UI components
├── main_enhanced.py              # Application entry point
├── requirements.txt               # Python dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

### Building for Distribution
Create a standalone desktop application:

```bash
# Build Mac app
pyinstaller --onefile --windowed --icon=logo.png main_enhanced.py

# Create installer (macOS)
python build_mac_app.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LangChain**: For the powerful agent orchestration framework
- **Ollama**: For enabling local AI model deployment
- **LangSmith**: For comprehensive observability and monitoring
- **CustomTkinter**: For the modern GUI framework
- **Mem0**: For advanced memory management capabilities

## 📞 Support

- **Issues**: Report bugs and request features via [GitHub Issues](https://github.com/akshsgaur/translator-agent/issues)
- **Discussions**: Join community discussions and share ideas
- **Documentation**: Check the [Wiki](https://github.com/akshsgaur/translator-agent/wiki) for detailed guides

---

**🎉 Ready to transform your translation workflow with AI?**

The Translator Agent combines the power of local AI processing with enterprise-grade observability, providing a privacy-first, intelligent translation solution that learns and adapts to your needs.

---

**Happy Translating! 🌐🤖📊**
