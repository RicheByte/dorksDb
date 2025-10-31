"""
Optimized Google Dork Generator v2.0
- Fast mode with no dependencies
- Optional AI mode for better results
- Caching for improved performance
"""

import os
import glob
import re
import json
from collections import Counter, defaultdict
import warnings
warnings.filterwarnings('ignore')

class DorkGenerator:
    def __init__(self, data_dir="data", use_ai=True):
        self.data_dir = data_dir
        self.use_ai = use_ai
        self.cache_file = os.path.join(data_dir, 'dorks_cache.json')
        
        # These will be loaded lazily
        self.model = None
        self.nlp = None
        self.index = None
        
        # Core data
        self.ghdb_dorks = []
        self.keyword_index = defaultdict(set)
        self.operator_index = defaultdict(list)
        
        # Load dorks
        print("📂 Loading dork database...")
        self.load_all_dorks()
        
        # Build indices
        print("🔨 Building search indices...")
        self.build_fast_indices()
        
        # Load AI models if requested
        if use_ai:
            self._init_ai_models()
    
    def _init_ai_models(self):
        """Load AI models with error handling"""
        try:
            print("🤖 Loading AI models...")
            from sentence_transformers import SentenceTransformer
            import faiss
            
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✓ Sentence transformer loaded")
            
            if self.ghdb_dorks:
                print("⚙️ Creating embeddings...")
                embeddings = self.model.encode(self.ghdb_dorks, show_progress_bar=True, batch_size=32)
                self.index = faiss.IndexFlatIP(embeddings.shape[1])
                self.index.add(embeddings.astype('float32'))
                print("✓ Semantic search ready")
        except Exception as e:
            print(f"⚠️ AI mode not available: {e}")
            print("⚡ Using fast keyword-only mode")
            self.model = None
        
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            print("✓ NLP loaded")
        except:
            print("⚠️ spaCy not available, using regex")
            self.nlp = None
    
    def load_all_dorks(self):
        """Load dorks with caching"""
        # Try cache first
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.ghdb_dorks = data.get('dorks', [])
                    if self.ghdb_dorks:
                        print(f"✓ Loaded {len(self.ghdb_dorks):,} dorks from cache")
                        return
            except:
                pass
        
        # Load from files
        print("🔍 Scanning dork files...")
        files = glob.glob(os.path.join(self.data_dir, '*.txt'))
        files.extend(glob.glob(os.path.join(self.data_dir, '*.md')))
        
        if not files:
            print("⚠️ No files found, using samples")
            self._create_samples()
            return
        
        print(f"📄 Found {len(files)} files")
        all_dorks = set()
        
        for i, path in enumerate(files):
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    dorks = self.extract_dorks(content)
                    all_dorks.update(dorks)
                    
                    if (i + 1) % 10 == 0:
                        print(f"  Processed {i+1}/{len(files)}, found {len(all_dorks):,} dorks")
            except Exception as e:
                print(f"⚠️ Error in {os.path.basename(path)}: {e}")
        
        self.ghdb_dorks = list(all_dorks)
        print(f"✓ Loaded {len(self.ghdb_dorks):,} unique dorks")
        
        # Save cache
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({'dorks': self.ghdb_dorks}, f)
            print(f"💾 Cache saved")
        except:
            pass
    
    def extract_dorks(self, content):
        """Extract dorks from content"""
        dorks = set()
        operators = ['inurl:', 'intitle:', 'filetype:', 'site:', 'intext:', 'ext:', '"index of"']
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or len(line) > 500 or line.startswith('#'):
                continue
            
            if any(op in line.lower() for op in operators):
                dorks.add(line)
            elif any(kw in line.lower() for kw in ['sql', 'config', 'admin', 'password', 'backup']):
                if not line.startswith('http'):
                    dorks.add(line)
        
        return dorks
    
    def _create_samples(self):
        """Create sample dorks"""
        self.ghdb_dorks = [
            'inurl:wp-config.php',
            'filetype:sql "wordpress"',
            'intitle:"index of" wp-content',
            'inurl:admin login',
            'filetype:env DB_PASSWORD',
            'filetype:log "password"',
            'inurl:backup filetype:sql',
            'site:github.com "api_key"'
        ]
    
    def build_fast_indices(self):
        """Build keyword index"""
        if not self.ghdb_dorks:
            return
        
        for idx, dork in enumerate(self.ghdb_dorks):
            words = re.findall(r'\b\w+\b', dork.lower())
            for word in words:
                if len(word) > 2:
                    self.keyword_index[word].add(idx)
        
        operators = ['inurl:', 'intitle:', 'filetype:', 'site:']
        for idx, dork in enumerate(self.ghdb_dorks):
            for op in operators:
                if op in dork.lower():
                    self.operator_index[op].append(idx)
        
        print(f"✓ Indexed {len(self.keyword_index)} keywords")
    
    def understand_query(self, query):
        """Parse query"""
        query_lower = query.lower()
        
        tech_map = {
            'wordpress': r'\b(wordpress|wp)\b',
            'joomla': r'\bjoomla\b',
            'sql': r'\b(sql|mysql|database|db)\b',
            'php': r'\bphp\b'
        }
        
        target_map = {
            'config': r'\b(config|configuration)\b',
            'login': r'\b(login|admin)\b',
            'backup': r'\b(backup|dump)\b',
            'password': r'\b(password|passwd)\b',
            'database': r'\b(database|db)\b'
        }
        
        filetype_map = {
            'sql': r'\bsql\b',
            'php': r'\bphp\b',
            'env': r'\benv\b',
            'log': r'\blog\b'
        }
        
        components = {
            'technology': [],
            'target': [],
            'filetype': []
        }
        
        for tech, pattern in tech_map.items():
            if re.search(pattern, query_lower):
                components['technology'].append(tech)
        
        for target, pattern in target_map.items():
            if re.search(pattern, query_lower):
                components['target'].append(target)
        
        for ft, pattern in filetype_map.items():
            if re.search(pattern, query_lower):
                components['filetype'].append(ft)
        
        return components
    
    def find_relevant_dorks(self, query, top_k=20):
        """Find dorks using best available method"""
        if not self.ghdb_dorks:
            return []
        
        if self.model and self.index:
            return self._semantic_search(query, top_k)
        
        return self._keyword_search(query, top_k)
    
    def _semantic_search(self, query, top_k):
        """Semantic search"""
        emb = self.model.encode([query]).astype('float32')
        scores, indices = self.index.search(emb, min(top_k * 2, len(self.ghdb_dorks)))
        return [self.ghdb_dorks[idx] for idx in indices[0][:top_k] if idx < len(self.ghdb_dorks)]
    
    def _keyword_search(self, query, top_k):
        """Keyword-based search"""
        words = set(re.findall(r'\b\w+\b', query.lower()))
        words = {w for w in words if len(w) > 2}
        
        scores = {}
        for idx, dork in enumerate(self.ghdb_dorks):
            score = 0
            dork_lower = dork.lower()
            
            for word in words:
                if word in dork_lower:
                    score += 10
            
            if query.lower() in dork_lower:
                score += 50
            
            if score > 0:
                scores[idx] = score
        
        sorted_idx = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        results = [self.ghdb_dorks[idx] for idx in sorted_idx[:top_k]]
        
        if len(results) < top_k:
            for dork in self.ghdb_dorks:
                if dork not in results:
                    results.append(dork)
                    if len(results) >= top_k:
                        break
        
        return results
    
    def generate_new_dorks(self, components, max_count=10):
        """Generate new dorks"""
        templates = {
            'config': [
                'inurl:config {tech}',
                'filetype:{ft} "{tech}" "password"',
                'intitle:"index of" "{tech}" config',
                'site:*.com inurl:config {tech}',
                '{tech} "config" filetype:{ft}',
                'intext:"{tech}" "config" inurl:admin'
            ],
            'login': [
                'inurl:login {tech}',
                'intitle:"admin" "{tech}"',
                '{tech} "admin panel"',
                'inurl:admin {tech}',
                'intitle:"{tech}" "login"',
                '{tech} inurl:wp-admin'
            ],
            'database': [
                'filetype:sql "{tech}"',
                'inurl:backup {tech} filetype:sql',
                '{tech} "database"',
                'inurl:db {tech}',
                'filetype:sql "{tech}" "INSERT INTO"',
                '{tech} "database" filetype:sql'
            ],
            'backup': [
                'filetype:zip "{tech}" backup',
                'inurl:backup {tech}',
                'intitle:"index of" "backup" "{tech}"',
                '{tech} filetype:bak',
                'inurl:backup filetype:sql {tech}',
                '{tech} filetype:tar.gz backup'
            ],
            'password': [
                'filetype:env "{tech}" PASSWORD',
                '{tech} filetype:txt "password"',
                'site:github.com "{tech}" "password"',
                '{tech} "api_key" filetype:env',
                'inurl:{tech} "password" filetype:log',
                '{tech} "secret" OR "api_key"'
            ]
        }
        
        generated = []
        tech = components['technology'][0] if components['technology'] else 'wordpress'
        targets = components['target'] if components['target'] else ['config']
        ft = components['filetype'][0] if components['filetype'] else 'php'
        
        # Generate from templates - use all available for each target
        for target in targets:
            if target in templates:
                for template in templates[target]:
                    dork = template.format(tech=tech, ft=ft)
                    if dork not in generated:
                        generated.append(dork)
                        if len(generated) >= max_count:
                            return generated[:max_count]
        
        # Add more generic combinations if we haven't reached max_count
        if len(generated) < max_count and tech:
            generic = [
                f'inurl:{tech}',
                f'intitle:"{tech}"',
                f'filetype:{ft} "{tech}"',
                f'{tech} filetype:log',
                f'site:*.com {tech} "index of"',
                f'{tech} "password" OR "secret"',
                f'inurl:{tech} filetype:sql',
                f'{tech} intitle:"index of"',
                f'"{tech}" filetype:env',
                f'site:github.com {tech} "key"',
                f'intext:"{tech}" "password"',
                f'{tech} inurl:config',
                f'filetype:txt {tech} "admin"',
                f'{tech} "database" inurl:backup',
                f'site:pastebin.com {tech}'
            ]
            for dork in generic:
                if dork not in generated:
                    generated.append(dork)
                    if len(generated) >= max_count:
                        break
        
        return generated[:max_count]
    
    def get_dork_statistics(self):
        """Get statistics"""
        if not self.ghdb_dorks:
            return {'total_dorks': 0}
        
        stats = {
            'total_dorks': len(self.ghdb_dorks),
            'operators': Counter(),
            'filetypes': Counter(),
            'targets': Counter()
        }
        
        for dork in self.ghdb_dorks:
            dl = dork.lower()
            
            for op in ['inurl', 'intitle', 'filetype', 'site', 'intext']:
                if f'{op}:' in dl:
                    stats['operators'][op] += 1
            
            ft_match = re.search(r'filetype:(\w+)', dl)
            if ft_match:
                stats['filetypes'][ft_match.group(1)] += 1
            
            for target in ['admin', 'login', 'config', 'backup', 'password', 'database']:
                if target in dl:
                    stats['targets'][target] += 1
        
        return stats
    
    def generate_dorks(self, query, count=20):
        """Main generation method"""
        print(f"\n🔎 Analyzing: '{query}'")
        
        components = self.understand_query(query)
        print(f"📊 Tech={components['technology']}, Target={components['target']}")
        
        # Use the count parameter for how many dorks to find
        relevant = self.find_relevant_dorks(query, top_k=count)
        print(f"✓ Found {len(relevant)} relevant dorks")
        
        # Generate proportional number of new dorks (up to count/2)
        generated = self.generate_new_dorks(components, max_count=max(10, count // 2))
        print(f"✓ Generated {len(generated)} new dorks")
        
        return {
            'query': query,
            'components': components,
            'relevant_dorks': relevant,
            'generated_dorks': generated,
            'statistics': self.get_dork_statistics()
        }
