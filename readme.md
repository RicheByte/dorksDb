#  Google Dork Generator v2.0

A blazing-fast, intelligent tool that transforms natural language queries into targeted Google dorks. Works instantly with **zero dependencies** in fast mode, or use optional AI features for semantic search.

![ZoEDR Dashboard](assets/dorkDb.gif)

##  Features

-  **Zero Dependencies Fast Mode** : Works immediately without installing anything
-  **Optional AI Mode** : Enable semantic search with sentence transformers (better results)
-  **Massive Database** : 55,000+ curated dorks from security research sources
-  **Smart Caching** : Lightning-fast startup after first run
-  **Natural Language** : Convert plain English to technical Google dorks
-  **Rich Output**: Beautiful markdown reports with statistics and examples
-  **Offline** : No API calls, everything runs locally

##  Quick Start

### Option 1: Fast Mode (Recommended - No Installation!)

Just run it! No dependencies needed:

```bash
# Works immediately - no setup required
python main.py "find wordpress config files" --fast
python main.py "sql database backups" --fast
python main.py "admin login pages" --fast
```

### Option 2: Full Setup with AI (Better Results)

1. **Clone the repository**
```bash
git clone https://github.com/RicheByte/dorksDb.git
cd dorksDb
```

2. **Run setup wizard**
```bash
python setup_wizard.py
```

The wizard will guide you through installing optional AI dependencies.

### Basic Usage

```bash
# Fast mode (no dependencies)
python main.py "wordpress config files" --fast

# AI mode (semantic search - requires dependencies)
python main.py "sql database backups"

# Specify output file
python main.py "admin pages" -o admin_dorks.md --fast

# Get more results
python main.py "exposed api keys" --count 30 --fast
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
dorksDb/
├── main.py                  # CLI interface
├── dork_generator.py        # Core engine (optimized v2.0)
├── setup_wizard.py          # Interactive setup for AI mode
├── requirements.txt         # Optional AI dependencies
├── readme.md                # This file
└── data/                    # 55K+ dork files (auto-cached)
    ├── *.txt                # Dork collections
    ├── *.md                 # Documentation
    └── dorks_cache.json     # Fast startup cache
```

##  How It Works

### Fast Mode (No Dependencies)
1. **Loads 55K+ dorks** from text files (cached after first run)
2. **Keyword matching** using optimized indices
3. **Pattern generation** based on query analysis
4. **Instant results** - typically < 2 seconds

### AI Mode (Optional)
1. **Everything from fast mode** +
2. **Semantic embeddings** using sentence transformers
3. **FAISS similarity search** for better relevance
4. **NLP entity extraction** with spaCy

Both modes produce excellent results - AI mode just ranks them slightly better!

##  Example Output

**Query:** `python main.py "sql database backups" --fast`

**Console Output:**
```
🚀 Initializing Dork Generator...
⚡ Fast mode enabled (keyword-only, no AI)
📂 Loading dork database...
✓ Loaded 54,949 unique dorks from cache
🔨 Building search indices...
✓ Indexed 8,415 keywords

🔎 Analyzing: 'sql database backups'
📊 Tech=['sql'], Target=['database', 'backup']
✓ Found 20 relevant dorks
✓ Generated 6 new dorks

============================================================
✨ GENERATION COMPLETE
============================================================
📊 Database:     54,949 total dorks
🎲 Found:        20 relevant dorks
✨ Generated:    6 new dorks
📋 Total Output: 26 dorks
💾 Saved to:     sql_database_backups_dorks.md
```

**Generated Markdown File** includes:
-  Database statistics and operator distribution
-  Query analysis breakdown
-  Relevant dorks from database
-  AI-generated custom dorks
-  Usage guide and examples
-  Legal and ethical guidelines

##  Advanced Usage

![ZoEDR Dashboard](assets/dorkDb%20files.gif)

### Command-Line Options

```bash
python main.py <query> [options]

Options:
  --fast, -f           Use fast mode (no AI, instant results)
  --output, -o FILE    Specify output filename
  --count, -c N        Number of dorks to generate (default: 20)
  --quiet, -q          Minimal console output
  --help, -h           Show help message

Examples:
  python main.py "wordpress vulnerabilities" --fast
  python main.py "exposed databases" -o databases.md --count 50
  python main.py "api keys github" --quiet --fast
```

### Performance Tips

1. **First run** may take 10-30 seconds to scan and cache dorks
2. **Subsequent runs** start instantly (< 1 second)
3. **Fast mode** is recommended for most use cases
4. **AI mode** adds 5-10 seconds but provides better ranking
5. **Clear cache** by deleting `data/dorks_cache.json` if needed

##  Legal & Ethical Usage

**Important Disclaimer:** This tool is intended for:

-  Security research on systems you own
-  Penetration testing with proper authorization  
-  Educational purposes and CTF challenges
-  Vulnerability assessment with permission

**Never use for:**
-  Unauthorized security testing
-  Accessing systems without permission
-  Malicious or illegal activities

The developers are not responsible for misuse. Always follow responsible disclosure practices and applicable laws.

##  Troubleshooting

### Common Issues & Solutions

** Problem:** `ModuleNotFoundError: No module named 'sentence_transformers'`
** Solution:** Use fast mode: `python main.py "query" --fast` (no dependencies needed!)

** Problem:** `OSError: Can't find model 'en_core_web_sm'`
** Solution:** Either run `python -m spacy download en_core_web_sm` OR use fast mode

** Problem:** Slow download when first running
** Solution:** The AI libraries are trying to download models. Either:
- Wait for download to complete (one-time only)
- Press Ctrl+C and use `--fast` mode instead
- Run `python setup_wizard.py` and choose option 1 (Fast Setup)

** Problem:** "No dork files found"
** Solution:** Make sure you're in the correct directory with the `data/` folder

** Problem:** Out of memory error
** Solution:** Use fast mode - it's much more memory efficient

** Problem:** Results not relevant
** Solution:** Try:
- More specific queries: "wordpress wp-config.php files"
- Increase count: `--count 50`
- Try AI mode (if dependencies installed)

### Performance Benchmarks

| Mode | First Run | Cached Run | Memory | Dependencies |
|------|-----------|------------|--------|--------------|
| Fast | ~15s | ~1s | ~50MB | None ✅ |
| AI   | ~45s | ~8s | ~500MB | Required |

**Recommendation:** Start with fast mode. Only use AI mode if you need the absolute best result ranking.

##  Contributing

Contributions welcome! Areas for improvement:
- Additional dork collections (add to `data/` folder)
- Enhanced pattern templates
- Performance optimizations
- Additional output formats (JSON, CSV, etc.)
- New search operators and techniques

##  License

This project is for **educational and authorized security research only**. 

Users are responsible for complying with all applicable laws and regulations.

---

**Built with ❤️ for the security community**  
*v2.0 - Optimized, Fast, and Dependency-Free*

