# set virtual environment
cd path\to\your\educational_rag

```bash
python -m venv venv
```
venv\Scripts\activate

for installing requirements: 
```bash
pip install -r requirements.txt
```

# After installing requirements, also run:
Download Specy related package
```bash
python -m spacy download en_core_web_sm
```

## Command-Line/Script Usage
Run this to test your pipeline from the terminal:

for running app locally:

```bash
python run main.py
```

For an interactive web interface:
```bash
streamlit run app.py
```

Inspecting Your Chroma Vectorstore Chunks and Metadata
You can explore your vectorstore chunks and metadata using the included script:
```bash
python inspect_chroma_db.py
```