from dork_generator import DorkGenerator
import os

def scan_data_directory():
    """Scan and analyze the data directory"""
    print("=== DORK DATABASE SCANNER ===\n")
    
    generator = DorkGenerator()
    
    stats = generator.get_dork_statistics()
    
    print(f"Database Summary:")
    print(f"Total dorks: {stats['total_dorks']:,}")
    print(f"Data directory: {os.path.abspath(generator.data_dir)}")
    
    if 'dork_types' in stats:
        print(f"\nDork Types:")
        for dork_type, count in stats['dork_types'].items():
            print(f"  {dork_type}: {count:,}")
    
    # Test some common queries
    test_queries = [
        "wordpress config files",
        "sql database backup", 
        "admin login pages",
        "exposed credentials",
        "joomla configuration"
    ]
    
    print(f"\nSample Queries (showing top 3 dorks each):")
    for query in test_queries:
        print(f"\n--- '{query}' ---")
        results = generator.generate_dorks(query)
        for i, dork in enumerate(results['relevant_dorks'][:3], 1):
            print(f"  {i}. {dork}")

if __name__ == "__main__":
    scan_data_directory()