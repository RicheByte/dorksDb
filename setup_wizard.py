#!/usr/bin/env python3
"""
Setup Script for Google Dork Generator
Helps install dependencies and models with better error handling
"""

import sys
import subprocess
import os

def run_command(cmd, description):
    """Run a command and handle errors gracefully"""
    print(f"\n{'='*60}")
    print(f"📦 {description}...")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️ {description} - FAILED")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print(f"🐍 Checking Python version...")
    version = sys.version_info
    print(f"   Found: Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ ERROR: Python 3.7 or higher is required")
        print(f"   Please upgrade Python and try again")
        return False
    
    print(f"✓ Python version is compatible")
    return True

def install_dependencies(mode='full'):
    """Install dependencies based on mode"""
    print(f"\n{'='*60}")
    print(f"🚀 GOOGLE DORK GENERATOR SETUP")
    print(f"{'='*60}")
    
    if not check_python_version():
        return False
    
    print(f"\n📋 Installation mode: {mode.upper()}")
    
    if mode == 'minimal':
        print(f"\n✨ Minimal mode: No dependencies needed!")
        print(f"   The tool will use fast keyword-only mode")
        return True
    
    # Install core Python packages
    packages = [
        "sentence-transformers",
        "faiss-cpu", 
        "scikit-learn",
        "numpy"
    ]
    
    print(f"\n📦 Installing {len(packages)} packages...")
    
    for package in packages:
        success = run_command(
            f'pip install "{package}"',
            f"Installing {package}"
        )
        if not success:
            print(f"\n⚠️ Warning: Could not install {package}")
            print(f"   The tool will still work in fast mode")
    
    # Install spaCy
    print(f"\n🧠 Installing spaCy for natural language processing...")
    success = run_command(
        'pip install spacy',
        "Installing spaCy"
    )
    
    if success:
        # Download spaCy model
        print(f"\n📥 Downloading spaCy language model...")
        success = run_command(
            'python -m spacy download en_core_web_sm',
            "Downloading English model"
        )
        
        if not success:
            print(f"\n⚠️ Could not download spaCy model")
            print(f"   You can try manually later:")
            print(f"   python -m spacy download en_core_web_sm")
    
    return True

def verify_installation():
    """Verify the installation works"""
    print(f"\n{'='*60}")
    print(f"🧪 Verifying installation...")
    print(f"{'='*60}")
    
    try:
        print(f"\n1️⃣ Testing basic import...")
        from dork_generator import DorkGenerator
        print(f"   ✓ Core module loaded")
        
        print(f"\n2️⃣ Testing fast mode (no AI)...")
        gen = DorkGenerator(use_ai=False)
        print(f"   ✓ Fast mode works!")
        print(f"   ✓ Loaded {len(gen.ghdb_dorks):,} dorks")
        
        print(f"\n3️⃣ Testing AI mode...")
        try:
            gen_ai = DorkGenerator(use_ai=True)
            if gen_ai.model:
                print(f"   ✓ AI mode fully functional")
            else:
                print(f"   ⚡ AI libraries not available, using fast mode")
                print(f"      (This is fine! Fast mode still works great)")
        except Exception as e:
            print(f"   ⚡ AI mode not available: {e}")
            print(f"      (This is fine! Fast mode still works great)")
        
        print(f"\n✅ Installation verified successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main setup routine"""
    print("""
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║       🔍 DORK GENERATOR SETUP WIZARD 🔍              ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
    """)
    
    print("Choose installation mode:")
    print("")
    print("1. 🚀 FAST SETUP (Recommended)")
    print("   → No dependencies, works immediately")
    print("   → Uses keyword-based search (still very effective)")
    print("")
    print("2. 🤖 FULL SETUP (With AI)")
    print("   → Installs AI libraries (~500MB)")
    print("   → Enables semantic search for better results")
    print("   → May take 5-10 minutes to download models")
    print("")
    
    choice = input("Enter your choice (1 or 2) [default: 1]: ").strip()
    
    if choice == '2':
        mode = 'full'
    else:
        mode = 'minimal'
    
    # Run installation
    success = install_dependencies(mode)
    
    if not success:
        print(f"\n⚠️ Setup encountered some issues")
        print(f"   But you can still use the tool in fast mode!")
    
    # Verify
    verify_installation()
    
    # Final instructions
    print(f"\n{'='*60}")
    print(f"🎉 SETUP COMPLETE!")
    print(f"{'='*60}")
    print(f"\n📖 Quick Start:")
    print(f"")
    print(f'   python main.py "find wordpress config files"')
    print(f'   python main.py "sql database backups"')
    print(f'   python main.py "admin login pages" --fast')
    print(f"")
    print(f"💡 Tips:")
    print(f"   • Use --fast flag to skip AI and run faster")
    print(f"   • Use --help to see all options")
    print(f"   • Check output .md files for detailed dorks")
    print(f"")
    print(f"{'='*60}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
