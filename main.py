import argparse
from dork_generator import DorkGenerator
import re
import time
import sys
import os

def sanitize_filename(query):
    """Convert query to safe filename"""
    return re.sub(r'[^\w\s-]', '', query).strip().replace(' ', '_')[:50]

def format_number(num):
    """Format number with commas"""
    return f"{num:,}"

def save_to_markdown(results, filename):
    """Save comprehensive results to markdown file with better formatting"""
    
    stats = results['statistics']
    components = results['components']
    
    # Header with timestamp
    content = [
        f"# 🔍 Google Dorks: \"{results['query']}\"",
        f"",
        f"*Generated on {time.strftime('%Y-%m-%d at %H:%M:%S')}*",
        f"",
        f"---",
        f""
    ]
    
    # Statistics Section
    content.extend([
        f"## 📊 Database Statistics",
        f"",
        f"- **Total Dorks Available**: {format_number(stats['total_dorks'])}",
    ])
    
    if 'operators' in stats and stats['operators']:
        content.append(f"")
        content.append(f"### Operator Distribution")
        for op, count in sorted(stats['operators'].items(), key=lambda x: x[1], reverse=True)[:10]:
            content.append(f"- `{op}:` — {format_number(count)} dorks")
    
    if 'filetypes' in stats and stats['filetypes']:
        content.append(f"")
        content.append(f"### Top Filetypes")
        for ft, count in sorted(stats['filetypes'].items(), key=lambda x: x[1], reverse=True)[:10]:
            content.append(f"- `.{ft}` — {format_number(count)} dorks")
    
    if 'targets' in stats and stats['targets']:
        content.append(f"")
        content.append(f"### Common Targets")
        for target, count in sorted(stats['targets'].items(), key=lambda x: x[1], reverse=True)[:8]:
            content.append(f"- {target.capitalize()} — {format_number(count)} dorks")
    
    content.append(f"")
    content.append(f"---")
    content.append(f"")
    
    # Query Analysis
    content.extend([
        f"## 🎯 Query Analysis",
        f""
    ])
    
    for key, values in components.items():
        if key == 'intent':
            continue
        emoji = {'technology': '💻', 'target': '🎯', 'filetype': '📄', 'operators': '🔧'}.get(key, '▪️')
        if values:
            content.append(f"{emoji} **{key.capitalize()}**: {', '.join(f'`{v}`' for v in values)}")
        else:
            content.append(f"{emoji} **{key.capitalize()}**: *None detected*")
    
    content.append(f"")
    content.append(f"---")
    content.append(f"")
    
    # Relevant Dorks from Database
    relevant_count = len(results['relevant_dorks'])
    content.extend([
        f"## 🎲 Relevant Dorks from Database",
        f"",
        f"*{relevant_count} dorks found matching your query*",
        f""
    ])
    
    for i, dork in enumerate(results['relevant_dorks'], 1):
        content.append(f"{i}. `{dork}`")
    
    content.append(f"")
    content.append(f"---")
    content.append(f"")
    
    # Generated Dorks
    generated_count = len(results['generated_dorks'])
    content.extend([
        f"## ✨ AI-Generated Dorks",
        f"",
        f"*{generated_count} custom dorks generated for your query*",
        f""
    ])
    
    for i, dork in enumerate(results['generated_dorks'], 1):
        content.append(f"{i}. `{dork}`")
    
    content.append(f"")
    content.append(f"---")
    content.append(f"")
    
    # All Dorks Combined
    all_dorks = results['relevant_dorks'] + results['generated_dorks']
    content.extend([
        f"## 📋 All Dorks Combined",
        f"",
        f"*Total: {len(all_dorks)} dorks ready to use*",
        f"",
        f"```"
    ])
    
    for dork in all_dorks:
        content.append(dork)
    
    content.extend([
        f"```",
        f"",
        f"---",
        f""
    ])
    
    # Usage Guide
    content.extend([
        f"## 📖 Usage Guide",
        f"",
        f"### How to Use These Dorks",
        f"",
        f"1. **Copy a dork** from the list above",
        f"2. **Paste into Google** search bar",
        f"3. **Review results** carefully",
        f"4. **Combine dorks** for more specific searches",
        f"",
        f"### Pro Tips",
        f"",
        f"- 🎯 **Target specific sites**: Add `site:example.com` to any dork",
        f"- 🔗 **Combine operators**: Mix `inurl:`, `filetype:`, and `intitle:` for precision",
        f"- 🚫 **Exclude results**: Use `-keyword` to filter out unwanted results",
        f"- 📅 **Time-based search**: Add `&tbs=qdr:y` to URL for results from the last year",
        f"- 🔄 **Rotate IPs**: Use VPN when doing extensive searches",
        f"",
        f"### Example Combinations",
        f"",
        f"```",
        f"site:github.com filetype:env DB_PASSWORD",
        f"inurl:admin intitle:login -demo",
        f"filetype:sql \"wordpress\" \"wp_users\"",
        f"```",
        f"",
        f"---",
        f""
    ])
    
    # Safety Warning
    content.extend([
        f"## ⚠️ Legal & Ethical Notice",
        f"",
        f"**IMPORTANT**: Only use these dorks on:",
        f"",
        f"- ✅ Systems you own or have explicit permission to test",
        f"- ✅ Bug bounty programs with proper authorization",
        f"- ✅ Educational environments and CTF challenges",
        f"",
        f"**DO NOT use for:**",
        f"",
        f"- ❌ Unauthorized access to systems",
        f"- ❌ Malicious activities or illegal purposes",
        f"- ❌ Violating terms of service or privacy laws",
        f"",
        f"**The developers are not responsible for misuse of this tool.**",
        f"",
        f"---",
        f"",
        f"*Generated by DorkGenerator v2.0 using {format_number(stats['total_dorks'])} dorks*"
    ])
    
    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    return len(all_dorks)

def print_banner():
    """Print fancy banner"""
    banner = """
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║          🔍 GOOGLE DORK GENERATOR v2.0 🔍            ║
║                                                       ║
║     Transform natural language into powerful         ║
║           Google dorks for security research         ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    parser = argparse.ArgumentParser(
        description='🔍 Generate Google dorks from natural language queries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "find wordpress config files"
  python main.py "sql database backups" -o sql_dorks.md
  python main.py "admin login pages" --fast
  python main.py "exposed api keys" --count 30
        """
    )
    
    parser.add_argument('query', help='Your search query (e.g., "find wordpress config files")')
    parser.add_argument('--output', '-o', help='Output file name (default: auto-generated)')
    parser.add_argument('--count', '-c', type=int, default=20, help='Number of dorks to find (default: 20)')
    parser.add_argument('--fast', '-f', action='store_true', help='Use fast mode (no AI, keyword-only)')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print_banner()
    
    try:
        # Initialize generator
        if not args.quiet:
            print("🚀 Initializing Dork Generator...")
            if args.fast:
                print("⚡ Fast mode enabled (keyword-only, no AI)")
        
        use_ai = not args.fast
        generator = DorkGenerator(use_ai=use_ai)
        
        if not args.quiet:
            print("")
        
        # Generate dorks with the specified count
        results = generator.generate_dorks(args.query, count=args.count)
        
        # Determine output filename
        if args.output:
            output_file = args.output
        else:
            safe_query = sanitize_filename(args.query)
            output_file = f"{safe_query}_dorks.md"
        
        # Ensure .md extension
        if not output_file.endswith('.md'):
            output_file += '.md'
        
        # Save results
        if not args.quiet:
            print(f"\n💾 Saving results to {output_file}...")
        
        total_dorks = save_to_markdown(results, output_file)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"✨ GENERATION COMPLETE")
        print(f"{'='*60}")
        print(f"")
        print(f"📊 Database:     {format_number(results['statistics']['total_dorks'])} total dorks")
        print(f"🎲 Found:        {len(results['relevant_dorks'])} relevant dorks")
        print(f"✨ Generated:    {len(results['generated_dorks'])} new dorks")
        print(f"📋 Total Output: {total_dorks} dorks")
        print(f"💾 Saved to:     {output_file}")
        print(f"")
        
        # Show sample dorks
        print(f"🔥 Top 10 Dorks:")
        print(f"")
        all_dorks = results['relevant_dorks'] + results['generated_dorks']
        for i, dork in enumerate(all_dorks[:10], 1):
            # Truncate long dorks
            display_dork = dork if len(dork) <= 60 else dork[:57] + "..."
            print(f"   {i:2}. {display_dork}")
        
        if len(all_dorks) > 10:
            print(f"\n   ... and {len(all_dorks) - 10} more in the output file")
        
        print(f"")
        print(f"{'='*60}")
        print(f"✅ Ready to use! Copy dorks from {output_file}")
        print(f"{'='*60}")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️ Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
