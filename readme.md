# 🔍 Google Dork Generator

A powerful, lightweight tool that transforms natural language queries into targeted Google dorks using semantic search and pattern recognition. Leverages a massive database of security research dorks to generate precise search queries for penetration testers and security researchers.

##  Features

- **Natural Language Processing**: Convert plain English queries into technical Google dorks
- **Massive Dork Database**: Built with 55,237+ curated dorks from multiple security sources
- **Semantic Search**: Uses Sentence Transformers and FAISS for intelligent dork matching
- **Pattern Recognition**: Generates new dorks based on query context and intent
- **Lightweight & Offline**: No API calls required - everything runs locally
- **Comprehensive Output**: Generates detailed markdown reports with statistics

##  Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/RicheByte/dorksDb.git
cd dorksDb
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download spaCy model**
```bash
python -m spacy download en_core_web_sm
```

### Basic Usage

```bash
# Generate dorks for WordPress config files
python main.py "find wordpress config files"

# Generate dorks for SQL database backups  
python main.py "locate sql database backups"

# Generate dorks for admin login pages
python main.py "search for admin login pages"

# Specify output file
python main.py "wordpress exposed files" -o wordpress_dorks.md
```

##  Database Statistics

The system comes pre-loaded with **55,237+** carefully curated Google dorks:

| Dork Type | Count |
|-----------|-------|
| `site:` dorks | 44,202 |
| `filetype:` dorks | 1,175 |
| `inurl:` dorks | 3,068 |
| `intitle:` dorks | 1,803 |
| `index of` dorks | 105 |

##  Project Structure

```
dork-generator/
├── main.py                 # Main CLI interface
├── dork_generator.py       # Core dork generation engine
├── scan_data.py           # Data analysis utility
├── requirements.txt       # Python dependencies
└── data/                 # Dork database (55,237+ dorks)
    ├── *.txt             # Various dork collections
    ├── *.md              # Documentation files
    └── dorks.db          # SQLite database (auto-generated)
```

##  How It Works

### 1. Query Processing
- Parses natural language using spaCy NER
- Identifies technologies, targets, and filetypes
- Maps intent to dork patterns

### 2. Semantic Matching
- Converts dorks to vector embeddings using Sentence Transformers
- Uses FAISS for fast similarity search
- Combines semantic and keyword-based matching

### 3. Dork Generation
- Retrieves relevant dorks from 55K+ database
- Generates new dorks using pattern templates
- Ranks results by relevance

### 4. Output Generation
- Creates comprehensive markdown reports
- Includes statistics and usage tips
- Formats for easy copy-paste usage

##  Example Output

**Query:** `"find wordpress config files"`

**Generated Report:**
```markdown
# Google Dorks for: "find wordpress config files"

## Database Statistics
- Total Dorks: 55,237
- site dorks: 44,202
- filetype dorks: 1,175
- inurl dorks: 3,068

## Relevant Dorks (15)
- `inurl:wp-config.php`
- `filetype:sql "wordpress"`
- `intitle:"index of" wp-content`
- `site:example.com "wp-config"`
...

## Generated Dorks (5)
- `inurl:config wordpress`
- `filetype:php "wordpress" "password"`
- `"wordpress config" php`
...
```

##  Advanced Usage

### Scan Your Data Directory
```bash
python scan_data.py
```
Analyzes your dork database and shows statistics and sample queries.

### Custom Dork Files
Add your own dork collections to the `data/` directory. The system automatically scans and indexes:
- `.txt` files with dork patterns
- Files containing Google dork operators (`inurl:`, `filetype:`, etc.)

### Modify Search Parameters
Edit `dork_generator.py` to adjust:
- Number of results (`top_k`)
- Scoring weights (semantic vs keyword)
- Template patterns for dork generation

##  Legal & Ethical Usage

**Important Disclaimer:** This tool is intended for:

- ✅ Security research on systems you own
- ✅ Penetration testing with proper authorization  
- ✅ Educational purposes and CTF challenges
- ✅ Vulnerability assessment with permission

**Never use for:**
- ❌ Unauthorized security testing
- ❌ Accessing systems without permission
- ❌ Malicious or illegal activities

The developers are not responsible for misuse. Always follow responsible disclosure practices and applicable laws.

##  Troubleshooting

**Common Issues:**

1. **"Module not found" errors**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **spaCy model download fails**
   ```bash
   python -m spacy download en_core_web_sm --user
   ```

3. **Memory issues with large datasets**
   - Reduce `top_k` parameter in `main.py`
   - Use `--count 10` for fewer results

##  Contributing

Contributions welcome! Areas for improvement:
- Additional dork patterns and templates
- Enhanced NLP for query understanding
- Performance optimizations for larger datasets
- Additional output formats

##  License

This project is for educational and authorized security research purposes only. Users are responsible for complying with all applicable laws and regulations.

---

**Generated with ❤️ for the security community**  
*Leveraging 55,237+ dorks from comprehensive security research databases*