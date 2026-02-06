# 🌐 Enhanced Language Tutor - LangChain Powered

An advanced AI-powered language learning desktop application with **LangChain orchestration**, **Ollama local models**, and **LangSmith observability**.

## 🚀 New Enhanced Features

### LangChain Integration
- **🤖 Agent-Based Architecture**: Smart language tutor agent with tool orchestration
- **🛠️ Advanced Tools**: Translation, language detection, exercise generation, progress tracking
- **🧠 Memory Management**: ConversationBufferWindowMemory for context awareness
- **🔄 Multi-Model Support**: Different models for translation vs reasoning tasks

### LangSmith Observability
- **📊 Full Tracing**: Complete visibility into AI interactions and decision-making
- **🔍 Run Monitoring**: Track all agent runs, tool calls, and responses
- **📈 Performance Analytics**: Monitor response times, success rates, and usage patterns
- **🐛 Debugging Support**: Detailed logs for troubleshooting and optimization

### Enhanced Memory System
- **💾 Intelligent Storage**: Mem0 with Ollama embeddings for semantic search
- **📚 Learning Analytics**: Comprehensive progress tracking and milestone recording
- **🔄 Translation History**: Store and retrieve all translations for review
- **📊 Exercise Tracking**: Monitor exercise completion and performance

## 🛠️ Enhanced Tech Stack

### Core Framework
- **🔗 LangChain**: Agent orchestration and tool management
- **🦙 Ollama**: Local model serving (translategemma:4b, mixtral:8x7b)
- **📊 LangSmith**: Observability and monitoring platform
- **🧠 Mem0**: Advanced memory with semantic search

### Models Used
- **🔄 translategemma:4b**: Specialized translation model
- **🧠 mixtral:8x7b**: Reasoning and complex task processing
- **🔍 mxbai-embed-large**: Text embeddings for memory search

### GUI & Storage
- **🖥️ CustomTkinter**: Modern, responsive desktop interface
- **💾 SQLite**: Local user data and progress storage
- **📁 File System**: Export/import functionality

## 📦 Enhanced Installation

### Prerequisites
1. **Python 3.8+** installed
2. **Ollama** installed and running locally
3. **LangSmith Account** (optional but recommended)

### Model Setup
```bash
# Install and start Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve

# Pull required models
ollama pull translategemma:4b      # Translation
ollama pull mixtral:8x7b           # Reasoning
ollama pull mxbai-embed-large     # Embeddings
```

### LangSmith Setup (Optional but Recommended)
1. Go to [LangSmith](https://smith.langchain.com/)
2. Create an account and get your API key
3. Set up a project for your language tutor

### Application Setup
```bash
# Clone or download the repository
cd language-tutor-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install enhanced dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your LangSmith API key

# Run the enhanced application
python main_enhanced.py
```

## 🎯 Enhanced Features

### 🤖 Smart Agent Interface
The LangChain-powered tutor agent can:
- **🔄 Translate** text between 20+ languages
- **🔍 Detect** languages automatically
- **📚 Generate** adaptive exercises based on difficulty
- **📊 Track** learning progress and milestones
- **💬 Maintain** conversational context

### 📊 Observability Dashboard
- **🔍 Real-time Monitoring**: Watch AI decisions in real-time
- **📈 Performance Metrics**: Track response times and success rates
- **🐛 Error Tracking**: Identify and debug issues quickly
- **📋 Run History**: Review all past interactions

### 🧠 Enhanced Memory System
- **💾 Semantic Search**: Find relevant past conversations
- **📚 Translation History**: Review all previous translations
- **📊 Progress Analytics**: Comprehensive learning statistics
- **📤 Data Export**: Export learning data for analysis

## 🔧 Advanced Configuration

### Environment Variables
```bash
# LangSmith Configuration
LANGSMITH_API_KEY=your_api_key_here
LANGSMITH_PROJECT=language-tutor

# Model Configuration
TRANSLATION_MODEL=translategemma:4b
REASONING_MODEL=mixtral:8x7b
EMBEDDING_MODEL=mxbai-embed-large

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
```

### Custom Model Configuration
You can customize which models to use:

```python
# In langchain_service.py
tutor_service = LangChainTutorService(
    translation_model="your_translation_model",
    reasoning_model="your_reasoning_model",
    langsmith_api_key="your_key"
)
```

## 📱 Enhanced User Interface

### New Tabs
1. **💬 Smart Chat**: Agent-powered conversation with tool access
2. **🔄 Smart Translation**: Enhanced translation with memory
3. **📚 Adaptive Exercises**: AI-generated exercises with difficulty levels
4. **📊 Progress Analytics**: Comprehensive learning analytics
5. **🔍 Observability**: LangSmith integration and monitoring

### Enhanced Features
- **🧠 Context Awareness**: Agent remembers conversation history
- **🛠️ Tool Orchestration**: Automatic tool selection and execution
- **📊 Real-time Feedback**: Immediate progress tracking
- **🔍 Debug Mode**: View agent decision-making process

## 🔍 LangSmith Integration

### What Gets Tracked?
- **🤖 Agent Runs**: Every interaction with the tutor agent
- **🛠️ Tool Calls**: All translation, detection, and exercise generation
- **📊 Memory Operations**: All memory additions and searches
- **🔄 Conversation Flow**: Complete conversation history

### Viewing Traces
1. Go to your LangSmith project
2. View real-time runs as they happen
3. Filter by user, session, or tool type
4. Analyze performance and identify patterns

### Debugging with LangSmith
- **🐛 Error Analysis**: Identify where failures occur
- **⚡ Performance**: Track response times and bottlenecks
- **🔄 Tool Usage**: See which tools are used most frequently
- **📊 User Behavior**: Understand learning patterns

## 📊 Enhanced Analytics

### Learning Progress
- **📈 Exercise Completion**: Track finished exercises and scores
- **🔄 Translation History**: Monitor translation accuracy and usage
- **🎯 Milestone Achievement**: Record learning milestones
- **⏱️ Time Tracking**: Monitor study sessions and duration

### Performance Metrics
- **⚡ Response Times**: Track AI model performance
- **🎯 Success Rates**: Monitor tool execution success
- **📊 Usage Patterns**: Understand feature utilization
- **🔍 Error Rates**: Track and analyze failures

## 🚀 Advanced Usage

### Custom Tools
Add your own tools to the agent:

```python
def custom_tool(query: str) -> str:
    # Your custom logic here
    return "Result"

# Add to tools list in langchain_service.py
Tool(
    name="custom_tool",
    description="Your custom tool description",
    func=custom_tool
)
```

### Memory Customization
Customize memory behavior:

```python
# Adjust memory window size
self.memory = ConversationBufferWindowMemory(
    k=20,  # Increase for longer context
    return_messages=True
)
```

### Observability Enhancement
Add custom tracing:

```python
# Log custom events to LangSmith
self.langsmith_client.create_run(
    name="custom_event",
    inputs={"data": "your_data"},
    outputs={"result": "your_result"}
)
```

## 🐛 Troubleshooting

### Common Issues

**LangSmith Connection Error**:
- Verify API key is correct
- Check project name matches
- Ensure internet connectivity

**Model Loading Issues**:
- Verify Ollama is running: `ollama serve`
- Check models are installed: `ollama list`
- Restart Ollama if needed

**Memory Service Errors**:
- Check embedding model is available
- Verify Mem0 configuration
- Check Ollama connection

**Agent Tool Failures**:
- Check model permissions
- Verify tool definitions
- Review LangSmith traces for details

### Debug Mode
Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📄 LangSmith vs Original

| Feature | Original | Enhanced |
|---------|----------|----------|
| AI Integration | Direct Ollama | LangChain Agent |
| Memory | Basic Mem0 | Enhanced + LangChain |
| Observability | None | Full LangSmith |
| Tool Orchestration | Manual | Automatic |
| Context Awareness | Limited | Advanced |
| Debugging | Basic Logs | Full Tracing |
| Analytics | Simple | Comprehensive |

## 🎓 Benefits of LangChain Integration

### For Developers
- **🔧 Easier Maintenance**: Modular, reusable components
- **🐛 Better Debugging**: Full observability and tracing
- **⚡ Performance**: Optimized tool orchestration
- **🔄 Flexibility**: Easy to add new tools and models

### For Users
- **🧠 Smarter Tutor**: Context-aware, agent-based interactions
- **📊 Better Progress**: Comprehensive learning analytics
- **🔍 Transparency**: See how AI makes decisions
- **🚀 Enhanced Features**: More capabilities and better UX

---

**🎉 Ready to experience the future of language learning?**

The enhanced version provides enterprise-grade observability and AI orchestration while maintaining the privacy and offline capabilities of the original.

---

**Happy Learning with LangChain! 🌐🤖📊**
