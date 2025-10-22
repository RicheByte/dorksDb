import sqlite3
import pickle
import os
import glob
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy
import re
from collections import Counter

class DorkGenerator:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize databases
        self.init_databases()
        self.load_all_dorks()
        
    def init_databases(self):
        os.makedirs(self.data_dir, exist_ok=True)
        self.conn = sqlite3.connect(f'{self.data_dir}/dorks.db')
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS query_dork_pairs (
                id INTEGER PRIMARY KEY,
                query TEXT,
                dork TEXT,
                success_score REAL DEFAULT 0.5
            )
        ''')
        self.conn.commit()
    
    def load_all_dorks(self):
        """Load ALL dork files from the data directory"""
        print("Scanning for dork files...")
        dork_files = []
        
        # Find all text files in data directory
        for file_pattern in ['*.txt', '*.md']:
            dork_files.extend(glob.glob(os.path.join(self.data_dir, file_pattern)))
        
        print(f"Found {len(dork_files)} dork files")
        
        all_dorks = set()
        file_stats = {}
        
        for file_path in dork_files:
            try:
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                print(f"Loading {file_name} ({file_size} bytes)...")
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Extract dorks - look for patterns like inurl:, filetype:, etc.
                    dorks_from_file = self.extract_dorks_from_content(content)
                    all_dorks.update(dorks_from_file)
                    
                    file_stats[file_name] = {
                        'size': file_size,
                        'dorks_found': len(dorks_from_file)
                    }
                    
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
        
        self.ghdb_dorks = list(all_dorks)
        print(f"Total unique dorks loaded: {len(self.ghdb_dorks)}")
        
        # Print file statistics
        print("\nFile Statistics:")
        for file_name, stats in list(file_stats.items())[:10]:  # Show top 10
            print(f"  {file_name}: {stats['dorks_found']} dorks")
        
        if len(file_stats) > 10:
            print(f"  ... and {len(file_stats) - 10} more files")
        
        # Create embeddings and indices
        self.create_search_indices()
    
    def extract_dorks_from_content(self, content):
        """Extract proper dorks from file content"""
        dorks = set()
        lines = content.split('\n')
        
        # Common Google dork operators
        operators = [
            'inurl:', 'intitle:', 'filetype:', 'ext:', 'site:', 
            'intext:', 'allintext:', 'allintitle:', 'allinurl:',
            'index of', '"index of"', 'parent directory'
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) > 500:  # Skip empty or very long lines
                continue
                
            # Check if line contains dork operators
            if any(op in line.lower() for op in operators):
                dorks.add(line)
            # Also include lines that look like search queries
            elif any(keyword in line.lower() for keyword in ['sql', 'config', 'admin', 'login', 'password', 'backup']):
                dorks.add(line)
        
        return dorks
    
    def create_search_indices(self):
        """Create FAISS index and TF-IDF features for all dorks"""
        print("Creating search indices...")
        
        if not self.ghdb_dorks:
            print("No dorks found! Creating sample dorks...")
            self.ghdb_dorks = [
                'inurl:wp-config.php',
                'filetype:sql "wordpress"', 
                'intitle:"index of" wp-content',
                'inurl:admin login',
                'filetype:env DB_PASSWORD'
            ]
        
        # Create embeddings
        print("Generating embeddings...")
        self.dork_embeddings = self.model.encode(self.ghdb_dorks)
        
        # Create FAISS index
        print("Building FAISS index...")
        self.index = faiss.IndexFlatIP(self.dork_embeddings.shape[1])
        self.index.add(self.dork_embeddings.astype('float32'))
        
        # TF-IDF features
        print("Building TF-IDF features...")
        self.tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=5000)
        self.tfidf_features = self.tfidf.fit_transform(self.ghdb_dorks)
        
        print("Search indices ready!")
    
    def understand_query(self, natural_query):
        """Parse natural language query into components"""
        doc = self.nlp(natural_query.lower())
        
        components = {
            'technology': [],
            'target': [],
            'filetype': [],
            'intent': 'search',
            'operators': []
        }
        
        # Technology mapping
        tech_keywords = {
            'wordpress': ['wordpress', 'wp'],
            'joomla': ['joomla'], 
            'drupal': ['drupal'],
            'magento': ['magento'],
            'sql': ['sql', 'database', 'mysql'],
            'php': ['php']
        }
        
        # Target mapping
        target_keywords = {
            'config': ['config', 'configuration', 'setup'],
            'login': ['login', 'admin', 'administrator', 'panel'],
            'backup': ['backup', 'back up', 'dump'],
            'password': ['password', 'pass', 'credential', 'auth'],
            'database': ['database', 'db', 'sql']
        }
        
        # Filetype mapping
        filetype_keywords = {
            'sql': ['sql', 'database', 'mysql'],
            'php': ['php', 'script'],
            'env': ['.env', 'environment'],
            'log': ['log', 'logs'],
            'txt': ['txt', 'text']
        }
        
        for token in doc:
            word = token.text.lower()
            
            # Check technology
            for tech, keywords in tech_keywords.items():
                if any(keyword in word for keyword in keywords):
                    if tech not in components['technology']:
                        components['technology'].append(tech)
            
            # Check target
            for target, keywords in target_keywords.items():
                if any(keyword in word for keyword in keywords):
                    if target not in components['target']:
                        components['target'].append(target)
            
            # Check filetype
            for ft, keywords in filetype_keywords.items():
                if any(keyword in word for keyword in keywords):
                    if ft not in components['filetype']:
                        components['filetype'].append(ft)
        
        return components
    
    def find_relevant_dorks(self, query, top_k=10):
        """Find relevant dorks using hybrid matching"""
        if not self.ghdb_dorks:
            return ["No dorks available in database"]
        
        # Semantic similarity
        query_embedding = self.model.encode([query])
        query_embedding = query_embedding.astype('float32')
        
        # Search more initially then filter
        search_k = min(top_k * 3, len(self.ghdb_dorks))
        semantic_scores, semantic_indices = self.index.search(query_embedding, search_k)
        semantic_scores = semantic_scores[0]
        semantic_indices = semantic_indices[0]
        
        # Keyword matching
        try:
            keyword_features = self.tfidf.transform([query])
            keyword_scores = np.array(keyword_features.mean(axis=1))[0]
            
            # Combine scores
            combined_scores = []
            for i, idx in enumerate(semantic_indices):
                if idx < len(self.ghdb_dorks):  # Ensure valid index
                    keyword_score = keyword_scores if hasattr(keyword_scores, '__len__') else keyword_scores
                    combined_score = 0.7 * semantic_scores[i] + 0.3 * keyword_score
                    combined_scores.append((idx, combined_score))
            
            combined_scores.sort(key=lambda x: x[1], reverse=True)
            top_indices = [idx for idx, _ in combined_scores[:top_k]]
            
        except Exception as e:
            print(f"Keyword matching failed: {e}")
            top_indices = semantic_indices[:top_k]
        
        return [self.ghdb_dorks[idx] for idx in top_indices if idx < len(self.ghdb_dorks)]
    
    def generate_new_dorks(self, components):
        """Generate new dorks based on query components"""
        templates = {
            'config': [
                'inurl:config {technology}',
                'filetype:php "{technology}" "password"',
                '"{technology} config" {filetype}',
                'intitle:"index of" "{technology} config"',
                'site:example.com "{technology}" "config"'
            ],
            'login': [
                'inurl:login {technology}',
                'intitle:"admin" "{technology}"',
                '{technology} "admin panel"',
                'inurl:admin {technology}',
                '{technology} "login" "password"'
            ],
            'database': [
                'filetype:sql "{technology}"',
                'inurl:backup {technology}',
                '"{technology} database" {filetype}',
                'intitle:"index of" "sql" "{technology}"'
            ],
            'backup': [
                'filetype:zip "{technology}"',
                'inurl:backup {technology}',
                '"{technology} backup"',
                'intitle:"index of" "backup" "{technology}"'
            ]
        }
        
        generated = []
        tech = components['technology'][0] if components['technology'] else ''
        target = components['target'][0] if components['target'] else 'config'
        filetype = components['filetype'][0] if components['filetype'] else 'php'
        
        # Generate based on target
        if target in templates:
            for template in templates[target]:
                generated_dork = template.format(
                    technology=tech,
                    filetype=filetype
                )
                generated.append(generated_dork)
        
        # Also generate some generic dorks
        generic_templates = [
            'inurl:{tech} "{target}"',
            'filetype:{ft} "{tech}"',
            'intitle:"index of" "{tech}"'
        ]
        
        for template in generic_templates:
            if tech or target != 'config':  # Only use if we have specific info
                generated_dork = template.format(
                    tech=tech,
                    target=target,
                    ft=filetype
                )
                if generated_dork not in generated:
                    generated.append(generated_dork)
        
        return generated
    
    def get_dork_statistics(self):
        """Get statistics about loaded dorks"""
        if not self.ghdb_dorks:
            return {"total_dorks": 0}
        
        # Count dorks by type
        dork_types = Counter()
        for dork in self.ghdb_dorks:
            dork_lower = dork.lower()
            if 'inurl:' in dork_lower:
                dork_types['inurl'] += 1
            if 'intitle:' in dork_lower:
                dork_types['intitle'] += 1
            if 'filetype:' in dork_lower:
                dork_types['filetype'] += 1
            if 'site:' in dork_lower:
                dork_types['site'] += 1
            if 'index of' in dork_lower:
                dork_types['index_of'] += 1
        
        return {
            'total_dorks': len(self.ghdb_dorks),
            'dork_types': dict(dork_types)
        }
    
    def generate_dorks(self, query):
        """Main method to generate dorks for a query"""
        components = self.understand_query(query)
        relevant_dorks = self.find_relevant_dorks(query, top_k=15)  # Get more dorks
        new_dorks = self.generate_new_dorks(components)
        stats = self.get_dork_statistics()
        
        return {
            'query': query,
            'components': components,
            'relevant_dorks': relevant_dorks,
            'generated_dorks': new_dorks,
            'statistics': stats
        }