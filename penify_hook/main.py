import sys
import os
import argparse
from pathlib import Path

from .api_client import APIClient
from .analyzer import DocGenHook

HOOK_FILENAME = "post-commit"
HOOK_TEMPLATE = """#!/bin/sh
# This is a post-commit hook generated by penify-hook.

penify-hook -t {token} -f {folder_path}
"""

def install_hook(repo_path, token, folder_path):
    hooks_dir = Path(repo_path) / ".git/hooks"
    hook_path = hooks_dir / HOOK_FILENAME
    
    if not hooks_dir.exists():
        print(f"Error: The hooks directory {hooks_dir} does not exist.")
        sys.exit(1)
    
    hook_content = HOOK_TEMPLATE.format(token=token, folder_path=folder_path)
    hook_path.write_text(hook_content)
    hook_path.chmod(0o755)  # Make the hook script executable

    print(f"Post-commit hook installed in {hook_path}")

def uninstall_hook(repo_path):
    hook_path = Path(repo_path) / ".git/hooks" / HOOK_FILENAME
    
    if hook_path.exists():
        hook_path.unlink()
        print(f"Post-commit hook uninstalled from {hook_path}")
    else:
        print(f"No post-commit hook found in {hook_path}")

def main():
    parser = argparse.ArgumentParser(description="A Git post-commit hook that generates docstrings for modified functions and classes in the latest commit.")

    parser.add_argument("-t", "--token", help="API token for authentication. If not provided, the environment variable 'PENIFY_API_TOKEN' will be used.", default=os.getenv('PENIFY_API_TOKEN'))
    parser.add_argument("-f", "--folder_path", help="Path to the folder to scan for modified files. Defaults to the current folder.", default=os.getcwd())

    # Add the install and uninstall options
    parser.add_argument("--install", action="store_true", help="Install the post-commit hook.")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall the post-commit hook.")

    args = parser.parse_args()

    # Handle installation and uninstallation of the hook
    if args.install:
        if not args.token:
            print("Error: API token must be provided either as an argument or via the 'PENIFY_API_TOKEN' environment variable. ")
            sys.exit(1)
        install_hook(args.folder_path, args.token, args.folder_path)
        sys.exit(0)

    if args.uninstall:
        uninstall_hook(args.folder_path)
        sys.exit(0)

    # Normal operation
    if not args.token:
        print("Error: API token must be provided either as an argument or via the 'PENIFY_API_TOKEN' environment variable.")
        sys.exit(1)

    repo_path = args.folder_path
    api_token = args.token
    api_url = 'https://production-gateway.snorkell.ai/api'
    api_client = APIClient(api_url, api_token)
    analyzer = DocGenHook(repo_path, api_client)
    analyzer.run()

if __name__ == "__main__":
    main()
