import subprocess
import os
import sys
import configparser

# --- Read config.ini ---
CONFIG_FILE = "config.ini"  # name of your rtc2git config file
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# --- Extract values from [General] ---
RTC2GIT_PATH = os.path.abspath(os.path.dirname(__file__))  # folder where migration.py lives
repo_url = config.get("General", "Repo", fallback="").strip()
user = config.get("General", "User", fallback="").strip()
password = config.get("General", "Password", fallback="").strip()
git_repo_name = config.get("General", "GIT-Reponame", fallback="").strip()
workspace_name = config.get("General", "WorkspaceName", fallback="").strip()
directory = config.get("General", "Directory", fallback="").strip()

# --- Extract values from [Migration] ---
stream_to_migrate = config.get("Migration", "StreamToMigrate", fallback="").strip()
# Look up the Git branch mapped to that stream
branch_to_push = config.get("Migration", stream_to_migrate, fallback="").strip()

# --- Derived paths ---
WORKING_TREE = os.path.join(directory, os.path.splitext(git_repo_name)[0])
GITHUB_REMOTE = f"https://github.com/RTC2G/{git_repo_name}"

def run_cmd(cmd, cwd=None):
    print(f"\n>>> Running: {cmd}")
    result = subprocess.run(cmd, cwd=cwd, shell=True)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)

def main():
    # Step 1: Run rtc2git migration
    run_cmd(f"python migration.py -c {CONFIG_FILE}", cwd=RTC2GIT_PATH)

    # Step 2: Verify working tree exists
    if not os.path.isdir(WORKING_TREE):
        print(f"ERROR: Working tree folder not found: {WORKING_TREE}")
        sys.exit(1)

    # Step 3: Add GitHub remote
    run_cmd("git remote remove origin", cwd=WORKING_TREE)  # remove if exists
    run_cmd(f"git remote add origin {GITHUB_REMOTE}", cwd=WORKING_TREE)

    # Step 4: Push only the migrated branch and tags
    if branch_to_push:
        run_cmd(f"git push -u origin {branch_to_push} --force", cwd=WORKING_TREE)
    else:
        print(f"WARNING: No branch mapping found for stream '{stream_to_migrate}', skipping branch push.")

    run_cmd("git push origin --tags --force", cwd=WORKING_TREE)

    print(f"\n✅ Migration of stream '{stream_to_migrate}' and push of branch '{branch_to_push}' completed successfully.")

if __name__ == "__main__":
    main()
