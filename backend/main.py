import os
import sys
import subprocess
import requests
from run_spiders import run_spiders, remove_duplicates
from execute_solr_setup import execute_solr_setup

from importlib import metadata
from packaging.requirements import Requirement
from dotenv import load_dotenv

load_dotenv()


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
        # ensures we use the pip associated with the current .venv
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", file_path])
        print("✅ Installation successful.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies. Error: {e}")
        return False


def is_solr_running():
    """Checks if Solr is reachable at the configured URL."""
    # retrieves the base path from your .env file logic
    solr_url = os.getenv('SOLR_BASE_PATH', 'http://localhost:8983')

    try:
        # solr's admin page to check status
        response = requests.get(f"{solr_url}/solr/admin/info/system", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def run_command(description, command):
    print(f"\n➡️  {description}")
    try:
        subprocess.check_call(command, shell=True)
        print("\n✅ Done.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed: {e}")
        sys.exit(1)


def get_solr_conf_dir():
    """Finds the Solr configset directory from the downloaded Solr installation."""
    solr_dir = os.getenv('SOLR_INSTALL_DIR')

    if not solr_dir:
        print("\n⚠️ SOLR_INSTALL_DIR not found in .env.")
        solr_dir = input(
            "Please enter the absolute path to your downloaded Solr folder (e.g., /Users/name/Downloads/solr-9.4.0): ").strip()

    # Construct the path to the _default/conf directory
    conf_dir = os.path.join(solr_dir, "server", "solr", "configsets", "_default", "conf")

    if not os.path.exists(conf_dir):
        print(f"❌ Could not find config directory at {conf_dir}.")
        print("Ensure you provided the root path of your Solr installation.")
        sys.exit(1)

    return conf_dir


def main():
    # user confirmation based on README instructions
    print("--- ⚠️  Pre-flight Check ---")
    print("Please ensure you have followed the setup instructions in README.md.")
    print("Specifically: Solr should be started (it defaults to cloud mode) and a .venv should be active.")

    user_input = input("Have you completed these steps? (y/n): ").lower()
    if user_input not in ['y', 'yes']:
        print("Stopping. Please complete the setup steps before running the pipeline.")
        sys.exit(0)

    # requirement check
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

    # solr status check
    print("\n--- Checking Solr Server ---")
    if not is_solr_running():
        print("❌ Solr server is not running or unreachable.")
        print("Please start Solr by navigating to your Solr directory and running: bin/solr start -p 8983")
        sys.exit(1)
    print("✅ Solr is online.")

    # execute pipeline
    print("\n--- 🕷️  Phase 1: Scraping and Deduplication ---")
    run_spiders(output_dir="raw_data")
    remove_duplicates(output_dir="raw_data", unique_key="id")

    print("\n--- 🔍 Phase 2: Solr Setup and Indexing ---")
    execute_solr_setup()

    print("\n✅ All tasks completed successfully!")

    print("\n--- ⚠️  Post-indexing Check: Solr Clustering ---")
    print(
        "This optional step will:\n"
        "  • Restart Solr globally with the clustering module enabled\n"
        "  • Upload the ZooKeeper configurations dynamically from your Solr installation directory\n"
        "  • Reload the 'memes_collection'\n\n"
        "Make sure you have modified the solrconfig.xml and managed-schema.xml as per the README."
    )

    user_input = input("Do you want to proceed with clustering now? [y/N]: ").strip().lower()
    if user_input not in ("y", "yes"):
        print("ℹ️  Clustering step skipped. You can run it later if needed.")
        sys.exit(0)

    solr_dir = os.getenv('SOLR_INSTALL_DIR')
    solr_bin = os.path.join(solr_dir, 'bin', 'solr') if solr_dir else 'solr'

    run_command(
        "Restarting Solr with clustering enabled",
        f"{solr_bin} restart -p 8983 -Dsolr.modules=clustering -Dsolr.clustering.enabled=true"
    )

    zk_conf_dir = get_solr_conf_dir()
    run_command(
        "Uploading ZooKeeper config for memes_collection",
        f"{solr_bin} zk upconfig -n memes_collection.AUTOCREATED -d {zk_conf_dir}"
    )

    run_command(
        "Reloading memes_collection",
        'curl "http://localhost:8983/solr/admin/collections?action=RELOAD&name=memes_collection"'
    )

    print("\n🎉 Clustering enabled successfully!")


if __name__ == "__main__":
    main()
