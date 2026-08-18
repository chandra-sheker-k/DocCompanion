# DocCompanion

## Setup Instructions

### 1. Install Dependencies
```bash
# Create virtual environment (if not exists)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file in the project root with the following variables:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
TIME_ZONE=UTC
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:7b
```

### 3. Run Migrations
```bash
python manage.py migrate
```

### 4. Download Ollama Model
For your Intel Mac, I recommend starting with a smaller model to verify everything works.

#### Option 1 (Recommended)
```bash
ollama pull qwen2.5:7b
```
#### Option 2
```bash
ollama pull mistral:7b
```
