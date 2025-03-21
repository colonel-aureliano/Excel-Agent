# Excel-Agent
 The Excel Agent takes user instruction (e.g. "Change all rows to the left-aligned, filter out rows that contain keyword 'abc', summarize some property, output to a txt"), parses it into subtasks and executes subtasks one by one till completion.

## Installation
1. Clone the repository:
   ```sh
   git clone <your-repo-url>
   cd <your-project-directory>
   ```
2. Create a virtual environment (optional but recommended):
   ```sh
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate     # On Windows
   ```
3. Install dependencies:
   pip install -r requirements.txt

## Usage
uvicorn main:app --host 127.0.0.1 --port 5000 --reload

## References
https://github.com/X-PLUG/MobileAgent/tree/main/PC-Agent

https://arxiv.org/abs/2502.14282

https://arxiv.org/abs/2308.00352