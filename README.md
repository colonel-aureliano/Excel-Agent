# Excel-Agent

> An AI-powered agent that understands natural language instructions and automatically manipulates Excel files using LLMs.

Excel-Agent is an intelligent automation tool that takes natural language instructions (e.g., "highlight all rows where the student's last name is Peters", "summarize the Excel content", "add a new column called Status") and executes them directly on your local Excel files. Powered by state-of-the-art language models, it combines planning, execution, and reflection to reliably complete complex Excel tasks.

## ✨ Features

- 🤖 **Natural Language Interface** - Describe what you want in plain English
- 📊 **Direct File Manipulation** - Changes are executed immediately on your Excel files
- 🔄 **Multi-Agent Architecture** - Uses action, reflection, and memory agents for reliable execution
- 🎯 **Multiple LLM Support** - Works with Gemini, OpenAI, DeepSeek, and Claude
- 💾 **Automatic Persistence** - Changes are saved after each successful operation
- 🛡️ **Error Recovery** - Automatic retry with reflection-based error correction
- 🌐 **Google Sheets Add-on** - FastAPI backend for Google Sheets integration
- 📝 **Rich Feedback** - Detailed console output showing every step

## 🚀 Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd Excel-Agent
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # venv\Scripts\activate   # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key:**
   ```bash
   # For Gemini (default, recommended)
   export GEMINI_API_KEY="your_api_key_here"
   
   # Or for other providers
   export OPENAI_API_KEY="your_api_key_here"
   export DEEPSEEK_API_KEY="your_api_key_here"
   export CLAUDE_API_KEY="your_api_key_here"
   ```

### Your First Command

```bash
python run.py \
  --instruction "summarize the excel content" \
  --excel_file_path example.xlsx
```

That's it! The agent will:
1. Load and analyze your Excel file
2. Understand your instruction
3. Execute the necessary operations
4. Save changes automatically
5. Provide feedback on what was done

## 📖 Usage

### Basic Usage

```bash
# Summarize Excel content
python run.py \
  --instruction "summarize the excel content" \
  --excel_file_path example.xlsx

# Find and highlight specific data
python run.py \
  --instruction "highlight the row where the student's last name is Peters" \
  --excel_file_path example2.xlsx

# Modify data
python run.py \
  --instruction "add a new column called 'Status' and set it to 'Active' for all rows" \
  --excel_file_path data.xlsx
```

### Advanced Configuration

```bash
# Use a different model provider
python run.py \
  --model_provider openai \
  --model_name "gpt-4o" \
  --instruction "your task" \
  --excel_file_path data.xlsx

# Customize execution parameters
python run.py \
  --instruction "your task" \
  --excel_file_path data.xlsx \
  --model_provider gemini \
  --model_name "gemini-2.0-flash-exp" \
  --temperature 0.0 \
  --max_iters 20 \
  --disable_reflection
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--instruction` | The task instruction in natural language | Required |
| `--excel_file_path` | Path to the Excel file | Required |
| `--model_provider` | LLM provider: `gemini`, `openai`, `deepseek`, `claude` | `gemini` |
| `--model_name` | Specific model name | `gemini-2.0-flash-exp` |
| `--api_key` | API key (or use environment variable) | From env var |
| `--temperature` | Model temperature (0.0-1.0) | `0.0` |
| `--max_iters` | Maximum iterations before stopping | `20` |
| `--stagnation_patience` | Iterations before stopping if no progress | `3` |
| `--disable_reflection` | Disable reflection agent (faster, less reliable) | `False` |
| `--pc_type` | Platform: `mac` or `windows` | `mac` |

## 🎯 Supported Operations

The agent can perform a wide variety of Excel operations:

### Selection & Highlighting
- **Select ranges** - `Select(0, 0, 4, 0)` highlights columns A-E in row 1
- **Select cells** - `Select(2, 3)` selects cell C4
- **Conditional selection** - Select based on cell values

### Data Manipulation
- **Set values** - `Set("New Value")` sets selected cells
- **Copy/Paste** - `Copy()`, `Paste()` for clipboard operations
- **Delete** - `Delete()` removes selected content
- **Auto-fill** - `SelectAndDrag(0, 0, 0, 5)` fills a range

### Formatting
- **Text formatting** - Bold, italic, colors
- **Cell formatting** - Background colors, borders
- **Conditional formatting** - Format based on conditions

### Communication
- **Tell User** - Agent can ask for clarification or provide updates
- **Terminate** - End the task when complete

## 🏗️ Architecture

Excel-Agent uses a multi-agent architecture inspired by [MobileAgent](https://github.com/X-PLUG/MobileAgent/tree/main/PC-Agent) and [SheetMind](https://arxiv.org/abs/2506.12339):

### Components

1. **Action Agent** - Decides what action to take based on current state
2. **Reflection Agent** - Verifies actions succeeded and suggests corrections
3. **Memory Agent** (optional) - Maintains context across operations
4. **Action Executor** - Parses and executes actions on Excel files

### Execution Flow

```
User Instruction
    ↓
Action Agent analyzes Excel file
    ↓
Action Agent decides on action (e.g., Select(0, 0, 4, 0))
    ↓
ActionExecutor parses and executes action
    ↓
File is saved with changes
    ↓
Reflection Agent verifies success
    ↓
Continue or retry with corrections
```

## 🔧 Model Configuration

Excel-Agent supports multiple LLM providers. See [MODEL_USAGE.md](MODEL_USAGE.md) for detailed configuration.

### Supported Providers

- **Gemini** (default) - Fast, free tier available
- **OpenAI** - GPT-4o, GPT-4o-mini, etc.
- **DeepSeek** - Cost-effective alternative
- **Claude** - Anthropic's Claude models

### Recommended Models

| Provider | Model | Use Case |
|----------|-------|----------|
| Gemini | `gemini-2.0-flash-exp` | Fast, default choice |
| Gemini | `gemini-1.5-pro` | More capable for complex tasks |
| OpenAI | `gpt-4o` | Best quality |
| OpenAI | `gpt-4o-mini` | Faster, cheaper |
| DeepSeek | `deepseek-chat` | Cost-effective |

## 🌐 Google Sheets Add-on

Excel-Agent includes a FastAPI backend for Google Sheets integration:

```bash
# Start the API server
uvicorn main:app --host 127.0.0.1 --port 5000 --reload
```

The server provides endpoints for:
- `/echo` - Echo test endpoint
- `/subtask-process` - Process subtask instructions
- `/health` - Health check

See `GoogleAdd-on/` directory for the Google Apps Script frontend.

## 📚 Documentation

- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Detailed usage examples and workflows
- **[MODEL_USAGE.md](MODEL_USAGE.md)** - Comprehensive model configuration guide
- **[IMPLEMENTATION_NOTES.md](IMPLEMENTATION_NOTES.md)** - Technical implementation details
- **[CHANGES.md](CHANGES.md)** - Changelog and migration guide

## 🐛 Troubleshooting

### "No API key provided" Error

Make sure you've set the appropriate environment variable:
```bash
export GEMINI_API_KEY="your_key"
```

Or pass it directly:
```bash
python run.py --api_key "your_key" --instruction "..." --excel_file_path data.xlsx
```

### Action Execution Fails

- Check that your Excel file exists and is readable
- Verify the action format in console output
- The reflection agent will usually retry with corrections
- Try rephrasing your instruction to be more specific

### File Not Being Modified

- Ensure you're using the virtual environment
- Check file permissions
- Verify the file path is correct
- Look for error messages in console output

### Import Errors

If you get import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## 💡 Tips for Best Results

1. **Be Specific** - "Highlight row 1" is better than "highlight something"
2. **One Task at a Time** - Break complex tasks into steps
3. **Check File Path** - Ensure your Excel file exists and is readable
4. **Use Descriptive Columns** - Clear column names help the agent understand your data
5. **Start Simple** - Test with basic operations before trying complex tasks
6. **Enable Reflection** - Keep reflection enabled (default) for better reliability

## 🔬 Example Session

```bash
$ python run.py --instruction "summarize the excel content" --excel_file_path example2.xlsx

✅ Loaded Excel file: example2.xlsx
Excel Sheet Summary:
Shape: 4 rows x 5 columns
Columns: ['Student ID', 'Last Name', 'First Name', 'Class', 'Sex']
...

🤖 Agent: The Excel file contains student data with the following columns: 
         Student ID (numeric), Last Name (text), First Name (text), 
         Class (numeric), and Sex (text).

👤 Your response: is there a student with last name Peters?

🤖 Agent: Yes, there is a student with the last name Peters. 
         The student's first name is Jennifer.

👤 Your response: can you highlight the row where the student's last name is Peters

📋 Executing action: Select(0, 0, 4, 0)
✅ Action executed successfully: Selected Row 1
💾 File saved: File saved to example2.xlsx

🤖 Agent: I have highlighted the row containing Jennifer Peters.
```

## 🛠️ Development

### Project Structure

```
Excel-Agent/
├── ExcelAgent/           # Core agent code
│   ├── agents/          # Agent state and base classes
│   ├── api/             # API schemas and parsing
│   ├── chat/            # LLM interaction and prompts
│   └── utils/           # Action execution utilities
├── GoogleAdd-on/        # Google Sheets add-on frontend
├── main.py              # FastAPI server
├── run.py               # CLI agent runner
└── requirements.txt     # Python dependencies
```

### Key Files

- `run.py` - Main CLI entry point
- `ExcelAgent/utils/action_executor.py` - Action execution engine
- `ExcelAgent/chat/api.py` - LLM inference with multi-provider support
- `ExcelAgent/chat/prompt.py` - Agent prompts and instructions

## 📄 License

[Add your license information here]

## 🙏 Acknowledgments

This project is inspired by:
- [SheetMind: An End-to-End LLM-Powered Multi-Agent Framework for Spreadsheet Automation](https://arxiv.org/abs/2506.12339) - Multi-agent framework for spreadsheet automation via natural language
- [MobileAgent](https://github.com/X-PLUG/MobileAgent/tree/main/PC-Agent) - Multi-agent architecture
- [MobileAgent v2 Paper](https://arxiv.org/abs/2502.14282)
- [PC-Agent Paper](https://arxiv.org/abs/2308.00352)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Made with ❤️ for automating Excel workflows**
