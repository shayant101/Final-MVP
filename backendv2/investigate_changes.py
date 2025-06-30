#!/usr/bin/env python3
"""
Investigation Script: What Changed That Broke MongoDB SSL Connection
Analyzes system state to identify what changed from a previously working setup
"""

import os
import sys
import ssl
import platform
import subprocess
import pkg_resources
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_command(cmd):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1

def check_git_history():
    """Check recent git commits to see what changed"""
    print("🔍 CHECKING GIT HISTORY FOR RECENT CHANGES")
    print("=" * 60)
    
    # Get recent commits
    stdout, stderr, code = run_command("git log --oneline -10")
    if code == 0:
        print("📝 Recent commits:")
        for line in stdout.split('\n')[:5]:
            print(f"   {line}")
    else:
        print(f"❌ Could not get git history: {stderr}")
    
    # Check if requirements.txt was recently modified
    stdout, stderr, code = run_command("git log -1 --name-only requirements.txt")
    if code == 0 and stdout:
        print(f"\n📦 requirements.txt last modified:")
        print(f"   {stdout.split()[0] if stdout.split() else 'Unknown'}")
    
    # Check if .env was recently modified
    stdout, stderr, code = run_command("git log -1 --name-only .env")
    if code == 0 and stdout:
        print(f"\n🔧 .env last modified:")
        print(f"   {stdout.split()[0] if stdout.split() else 'Unknown'}")
    
    print()

def check_system_info():
    """Check system information that could affect SSL"""
    print("🖥️  SYSTEM INFORMATION ANALYSIS")
    print("=" * 60)
    
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"SSL Version: {ssl.OPENSSL_VERSION}")
    print(f"SSL Version Number: {ssl.OPENSSL_VERSION_NUMBER}")
    
    # Check if this is a Homebrew Python
    if "homebrew" in sys.executable.lower():
        print("🍺 Homebrew Python detected")
        
        # Check Homebrew updates
        stdout, stderr, code = run_command("brew list --versions python@3.9")
        if code == 0:
            print(f"   Homebrew Python version: {stdout}")
        
        # Check OpenSSL version from Homebrew
        stdout, stderr, code = run_command("brew list --versions openssl")
        if code == 0:
            print(f"   Homebrew OpenSSL: {stdout}")
    
    # Check system OpenSSL
    stdout, stderr, code = run_command("openssl version")
    if code == 0:
        print(f"System OpenSSL: {stdout}")
    
    print()

def check_python_packages():
    """Check Python package versions that could affect MongoDB connection"""
    print("📦 PYTHON PACKAGE VERSION ANALYSIS")
    print("=" * 60)
    
    critical_packages = [
        'pymongo', 'motor', 'fastapi', 'uvicorn', 
        'cryptography', 'certifi', 'urllib3', 'requests'
    ]
    
    for package in critical_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"✅ {package}: {version}")
        except pkg_resources.DistributionNotFound:
            print(f"❌ {package}: NOT INSTALLED")
    
    # Check for known problematic versions
    try:
        pymongo_version = pkg_resources.get_distribution('pymongo').version
        if pymongo_version.startswith('4.6'):
            print(f"\n⚠️  WARNING: PyMongo {pymongo_version} has known SSL issues with some MongoDB Atlas clusters")
        elif pymongo_version.startswith('4.5'):
            print(f"\n✅ PyMongo {pymongo_version} is generally stable")
        elif pymongo_version.startswith('4.7'):
            print(f"\n⚠️  WARNING: PyMongo {pymongo_version} is very recent and may have compatibility issues")
    except:
        pass
    
    print()

def check_certificate_store():
    """Check SSL certificate store"""
    print("🔐 SSL CERTIFICATE STORE ANALYSIS")
    print("=" * 60)
    
    try:
        import certifi
        ca_bundle = certifi.where()
        print(f"Certifi CA Bundle: {ca_bundle}")
        
        # Check if CA bundle exists and is readable
        if os.path.exists(ca_bundle):
            stat = os.stat(ca_bundle)
            print(f"CA Bundle size: {stat.st_size} bytes")
            print(f"CA Bundle modified: {datetime.fromtimestamp(stat.st_mtime)}")
        else:
            print("❌ CA Bundle file not found!")
    except ImportError:
        print("❌ Certifi package not available")
    
    # Check system certificate stores
    common_ca_paths = [
        '/etc/ssl/certs/ca-certificates.crt',
        '/etc/ssl/certs/ca-bundle.crt',
        '/usr/local/etc/openssl/cert.pem',
        '/opt/homebrew/etc/openssl/cert.pem'
    ]
    
    print("\nSystem CA certificate locations:")
    for path in common_ca_paths:
        if os.path.exists(path):
            stat = os.stat(path)
            print(f"✅ {path} ({stat.st_size} bytes)")
        else:
            print(f"❌ {path} (not found)")
    
    print()

def check_network_connectivity():
    """Check network connectivity to MongoDB Atlas"""
    print("🌐 NETWORK CONNECTIVITY ANALYSIS")
    print("=" * 60)
    
    # Extract hostname from MongoDB URL
    mongodb_url = os.getenv("MONGODB_URL", "")
    if "mongodb+srv://" in mongodb_url:
        # Extract hostname
        try:
            hostname = mongodb_url.split("@")[1].split("/")[0].split("?")[0]
            print(f"MongoDB Atlas hostname: {hostname}")
            
            # Test DNS resolution
            stdout, stderr, code = run_command(f"nslookup {hostname}")
            if code == 0:
                print("✅ DNS resolution successful")
            else:
                print(f"❌ DNS resolution failed: {stderr}")
            
            # Test basic connectivity
            stdout, stderr, code = run_command(f"ping -c 3 {hostname}")
            if code == 0:
                print("✅ Basic connectivity successful")
            else:
                print(f"⚠️  Ping failed (may be normal for MongoDB Atlas): {stderr}")
            
            # Test SSL connection
            stdout, stderr, code = run_command(f"openssl s_client -connect {hostname}:27017 -servername {hostname} < /dev/null")
            if "CONNECTED" in stdout:
                print("✅ SSL connection established")
            else:
                print(f"❌ SSL connection failed")
                if "certificate verify failed" in stderr:
                    print("   Issue: Certificate verification failed")
                elif "handshake failure" in stderr:
                    print("   Issue: SSL handshake failure")
        except Exception as e:
            print(f"❌ Could not parse MongoDB URL: {e}")
    
    print()

def check_recent_system_changes():
    """Check for recent system changes that could affect SSL"""
    print("🔄 RECENT SYSTEM CHANGES ANALYSIS")
    print("=" * 60)
    
    # Check Homebrew update history
    stdout, stderr, code = run_command("brew list --versions | grep -E '(python|openssl|ca-certificates)'")
    if code == 0:
        print("🍺 Homebrew SSL-related packages:")
        for line in stdout.split('\n'):
            if line.strip():
                print(f"   {line}")
    
    # Check when Python packages were last installed
    try:
        import pymongo
        pymongo_path = pymongo.__file__
        stat = os.stat(pymongo_path)
        print(f"\n📦 PyMongo installed/modified: {datetime.fromtimestamp(stat.st_mtime)}")
    except:
        pass
    
    try:
        import motor
        motor_path = motor.__file__
        stat = os.stat(motor_path)
        print(f"📦 Motor installed/modified: {datetime.fromtimestamp(stat.st_mtime)}")
    except:
        pass
    
    # Check system update history (macOS)
    stdout, stderr, code = run_command("system_profiler SPInstallHistoryDataType | head -20")
    if code == 0:
        print(f"\n🍎 Recent macOS updates:")
        lines = stdout.split('\n')
        for i, line in enumerate(lines[:10]):
            if line.strip():
                print(f"   {line}")
    
    print()

def analyze_mongodb_atlas_changes():
    """Analyze potential MongoDB Atlas changes"""
    print("☁️  MONGODB ATLAS ANALYSIS")
    print("=" * 60)
    
    mongodb_url = os.getenv("MONGODB_URL", "")
    if mongodb_url:
        print(f"Connection String: {mongodb_url}")
        
        # Check if using mongodb+srv (which requires DNS resolution)
        if "mongodb+srv://" in mongodb_url:
            print("✅ Using SRV connection (recommended)")
        else:
            print("⚠️  Using direct connection")
        
        # Check connection parameters
        if "ssl=true" in mongodb_url or "tls=true" in mongodb_url:
            print("✅ SSL/TLS explicitly enabled")
        else:
            print("⚠️  SSL/TLS not explicitly configured")
        
        if "retryWrites=true" in mongodb_url:
            print("✅ Retry writes enabled")
        
        if "w=majority" in mongodb_url:
            print("✅ Write concern set to majority")
    
    print("\n💡 Potential MongoDB Atlas changes that could cause issues:")
    print("   • Cluster maintenance/restart")
    print("   • SSL certificate renewal")
    print("   • IP whitelist changes")
    print("   • MongoDB version upgrade")
    print("   • Security policy changes")
    
    print()

def main():
    """Run comprehensive investigation"""
    print("🔍 MONGODB SSL CONNECTION ISSUE INVESTIGATION")
    print("=" * 80)
    print(f"Investigation started: {datetime.now()}")
    print("=" * 80)
    print()
    
    check_git_history()
    check_system_info()
    check_python_packages()
    check_certificate_store()
    check_network_connectivity()
    check_recent_system_changes()
    analyze_mongodb_atlas_changes()
    
    print("🎯 INVESTIGATION SUMMARY")
    print("=" * 60)
    print("Key areas to investigate based on findings above:")
    print("1. Check if PyMongo version changed recently")
    print("2. Check if Homebrew updated Python/OpenSSL recently")
    print("3. Check if MongoDB Atlas cluster had maintenance")
    print("4. Check if system SSL certificates were updated")
    print("5. Check if IP address changed (affecting Atlas whitelist)")
    print()
    print("💡 Next steps:")
    print("1. Try downgrading PyMongo to a known working version")
    print("2. Check MongoDB Atlas cluster status and logs")
    print("3. Verify IP whitelist in MongoDB Atlas")
    print("4. Test with a fresh virtual environment")

if __name__ == "__main__":
    main()