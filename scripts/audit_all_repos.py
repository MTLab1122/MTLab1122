import json
import subprocess
import sys
from pathlib import Path

def get_repos():
    res = subprocess.run(
        ["gh", "repo", "list", "MTLab1122", "--limit", "100", "--json", 
         "name,description,url,isPrivate,isFork,updatedAt,createdAt,primaryLanguage,stargazerCount,repositoryTopics"],
        capture_output=True, text=True, check=True
    )
    return json.loads(res.stdout)

def main():
    repos = get_repos()
    print(f"Total repositories fetched: {len(repos)}\n")
    print(f"{'Repository':<42} | {'Language':<12} | {'Private':<7} | {'Updated':<11} | {'Description'}")
    print("-" * 110)
    for r in repos:
        name = r["name"]
        lang = (r.get("primaryLanguage") or {}).get("name", "None")
        is_priv = "Yes" if r.get("isPrivate") else "No"
        updated = r.get("updatedAt", "")[:10]
        desc = (r.get("description") or "")[:45]
        print(f"{name:<42} | {lang:<12} | {is_priv:<7} | {updated:<11} | {desc}")

if __name__ == "__main__":
    main()
