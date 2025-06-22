# After installing requirements, also run:
python -m spacy download en_core_web_sm

## Command-Line/Script Usage
Run this to test your pipeline from the terminal:

For an interactive web interface:
```bash
streamlit run app.py
```

Inspecting Your Chroma Vectorstore Chunks and Metadata
You can explore your vectorstore chunks and metadata using the included script:
```bash
python inspect_chroma_db.py
```