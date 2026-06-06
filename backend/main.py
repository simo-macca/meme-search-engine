import os
import sys
import subprocess
import requests
from run_spiders import run_spiders, remove_duplicates
from execute_solr_setup import execute_solr_setup


from importlib import metadata
from packaging.requirements import Requirement

def check_requirements(file_path="requirements.txt"):
    """Checks if all packages in requirements.txt are installed and compatible."""
    if not os.path.exists(file_path):
        print(f"⚠️ {file_path} not found.")
        return False

    try:
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                req = Requirement(line)
                installed_version = metadata.version(req.name)

                if installed_version not in req.specifier:
                    raise Exception(
                        f"{req.name} {installed_version} does not satisfy {req.specifier}"
                    )
        return True

    except metadata.PackageNotFoundError as e:
        print(f"❌ Missing package: {e}")
        return False
    except Exception as e:
        print(f"❌ Version conflict: {e}")
        return False

def install_requirements(file_path='requirements.txt'):
    """Attempts to install requirements using pip."""
    print(f"📦 Attempting to install missing dependencies from {file_path}...")
    try:
        # sys.executable ensures we use the pip associated with the current .venv
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", file_path])
        print("✅ Installation successful.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies. Error: {e}")
        return False

def is_solr_running():
    """Checks if Solr is reachable at the configured URL."""
    # Retrieves the base path from your .env file logic
    from dotenv import load_dotenv
    load_dotenv()
    solr_url = os.getenv('SOLR_BASE_PATH', 'http://localhost:8983')

    try:
        # Pinging Solr's admin page to check status
        response = requests.get(f"{solr_url}/solr/admin/info/system", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def run_command(description, command):
    print(f"\n➡️  {description}")
    try:
        subprocess.check_call(command.split())
        print("\n✅ Done.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed: {e}")
        sys.exit(1)

def main():
    # 1. User Confirmation based on README instructions
    print("--- ⚠️  Pre-flight Check ---")
    print("Please ensure you have followed the setup instructions in README.md.")
    print("Specifically: Solr should be started in cloud mode and a .venv should be active.")

    user_input = input("Have you completed these steps? (y/n): ").lower()
    if user_input not in ['y', 'yes']:
        print("Stopping. Please complete the setup steps before running the pipeline.")
        sys.exit(0)

    # 2. Requirements Check
    print("\n--- Checking Dependencies ---")
    if not check_requirements():
        print("⚠️  Some dependencies are missing.")
        choice = input("Install missing dependencies now? (y/n): ").lower()
        if choice.startswith("y"):
            install_requirements()
            print("✅ All requirements are now installed.")
        else:
            print("🛑 Execution stopped due to installation failure.")
            sys.exit(1)
    else:
        print("✅ All requirements are already installed.")

    # 3. Solr Status Check
    print("\n--- Checking Solr Server ---")
    if not is_solr_running():
        print("❌ Solr server is not running or unreachable.")
        print("Please start Solr by running: bin/solr start -cloud -p 8983 (adjust the port or cluster mode settings as needed)")
        sys.exit(1)
    print("✅ Solr is online.")

    # 4. Execute Pipeline
    print("\n--- 🕷️  Phase 1: Scraping and Deduplication ---")
    run_spiders(output_dir="raw_data")
    remove_duplicates(output_dir="raw_data", unique_key="id")

    print("\n--- 🔍 Phase 2: Solr Setup and Indexing ---")
    execute_solr_setup()

    print("\n✅ All tasks completed successfully!")

    print("\n--- ⚠️  Post-indexing Check: Solr Clustering ---")
    print(
        "This optional step will:\n"
        "  • Restart Solr in cloud mode\n"
        "  • Enable the clustering module\n"
        "  • Reload the 'memes_collection'\n\n"
        "Make sure you have followed the Solr cluster setup instructions in README.md."
    )

    user_input = input("Do you want to proceed with clustering now? [y/N]: ").strip().lower()
    if user_input not in ("y", "yes"):
        print("ℹ️  Clustering step skipped. You can run it later if needed.")
        sys.exit(0)

    run_command(
        "Restarting Solr in cloud mode with clustering enabled",
        "bin/solr restart -cloud -p 8983 "
        "-Dsolr.modules=clustering "
        "-Dsolr.clustering.enabled=true"
    )

    run_command(
        "Uploading ZooKeeper config for memes_collection",
        "bin/solr zk upconfig "
        "-n memes_collection.AUTOCREATED "
        "-d server/solr/configsets/_default/conf"
    )

    run_command(
        "Reloading memes_collection",
        'curl http://localhost:8983/solr/admin/collections?action=RELOAD&name=memes_collection'
    )

    print("\n🎉 Clustering enabled successfully!")

if __name__ == "__main__":
    main()
