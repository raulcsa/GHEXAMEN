#!/usr/bin/env python3
import os
import sys
import subprocess

# ANSI colors for beautiful output
COLOR_RESET = "\033[0;0m"
COLOR_BOLD = "\033[1m"
COLOR_GREEN = "\033[32m"
COLOR_RED = "\033[31m"
COLOR_YELLOW = "\033[33m"
COLOR_CYAN = "\033[36m"
COLOR_MAGENTA = "\033[35m"

def print_header(title):
    print(f"\n{COLOR_BOLD}{COLOR_CYAN}{'='*60}")
    print(f" {title.center(58)}")
    print(f"{'='*60}{COLOR_RESET}\n")

def run_command(command, cwd=None):
    print(f"{COLOR_BOLD}{COLOR_YELLOW}⚙️ Executing: {command}{COLOR_RESET}")
    result = subprocess.run(command, shell=True, cwd=cwd, text=True, capture_output=True)
    if result.returncode == 0:
        if result.stdout.strip():
            print(f"{COLOR_GREEN}{result.stdout.strip()}{COLOR_RESET}")
        return True, result.stdout
    else:
        print(f"{COLOR_RED}❌ Error running command (Code {result.returncode}):{COLOR_RESET}")
        if result.stderr.strip():
            print(f"{COLOR_RED}{result.stderr.strip()}{COLOR_RESET}")
        elif result.stdout.strip():
            print(f"{COLOR_RED}{result.stdout.strip()}{COLOR_RESET}")
        return False, result.stderr

def get_git_changes():
    files = set()
    # 1. Uncommitted/unstaged files
    success, out = run_command("git status --porcelain")
    if success:
        for line in out.splitlines():
            if len(line) > 3:
                files.add(line[3:].strip())
    
    # 2. Diff with last commit
    success_rev, _ = run_command("git rev-parse HEAD")
    if success_rev:
        success_diff, out_diff = run_command("git diff --name-only HEAD~1 HEAD")
        if success_diff:
            for line in out_diff.splitlines():
                if line.strip():
                    files.add(line.strip())
                    
    return list(files)

# Predefined scenarios mapped to corrected monorepo directory names
SCENARIOS = {
    "1": {
        "name": "Only Frontend changes",
        "files": ["frontend/index.js", "frontend/package.json"]
    },
    "2": {
        "name": "Only Backend changes",
        "files": ["backend/index.test.js"]
    },
    "3": {
        "name": "Only Infrastructure changes",
        "files": ["infrastructure/main.tf"]
    },
    "4": {
        "name": "Only Documentation changes",
        "files": ["docs/README.md"]
    },
    "5": {
        "name": "Multi-component changes (Frontend & Backend)",
        "files": ["frontend/index.test.js", "backend/index.js", "docs/README.md"]
    },
    "6": {
        "name": "Global/Root changes (All affected)",
        "files": ["frontend/index.js", "backend/index.js", "infrastructure/main.tf", "docs/README.md"]
    }
}

def analyze_changes(file_list):
    frontend = False
    backend = False
    infra = False
    docs = False

    for f in file_list:
        f = f.replace('\\', '/')
        if f.startswith("frontend/"):
            frontend = True
        elif f.startswith("backend/"):
            backend = True
        elif f.startswith("infrastructure/"):
            infra = True
        elif f.startswith("docs/"):
            docs = True

    return frontend, backend, infra, docs

def simulate_pipeline():
    print_header("Monorepo CI Selective Pipeline Simulator")
    
    print(f"{COLOR_BOLD}Select input mode:{COLOR_RESET}")
    print(" 1) Run Predefined Scenario")
    print(" 2) Detect actual changes from Local Git Repository")
    print(" 3) Input custom file list manually")
    
    choice = input(f"{COLOR_BOLD}Enter choice (1-3): {COLOR_RESET}").strip()
    
    files = []
    scenario_name = "Custom Simulation"
    
    if choice == "1":
        print(f"\n{COLOR_BOLD}Select a Predefined Scenario:{COLOR_RESET}")
        for k, v in SCENARIOS.items():
            print(f"  {k}) {v['name']} (changes in: {', '.join(v['files'])})")
        scen_choice = input(f"{COLOR_BOLD}Select scenario (1-6): {COLOR_RESET}").strip()
        if scen_choice in SCENARIOS:
            files = SCENARIOS[scen_choice]["files"]
            scenario_name = SCENARIOS[scen_choice]["name"]
        else:
            print(f"{COLOR_RED}Invalid option. Exiting.{COLOR_RESET}")
            return
    elif choice == "2":
        scenario_name = "Git Repository Detected Changes"
        files = get_git_changes()
        if not files:
            print(f"{COLOR_YELLOW}No changes detected in Git. Running default scenario (Frontend & Backend).{COLOR_RESET}")
            files = SCENARIOS["5"]["files"]
            scenario_name = "Fallback: " + SCENARIOS["5"]["name"]
    elif choice == "3":
        print(f"\nEnter file paths relative to monorepo root, separated by commas:")
        print("Example: frontend/index.js, docs/README.md")
        custom_input = input(f"{COLOR_BOLD}Files: {COLOR_RESET}").strip()
        files = [f.strip() for f in custom_input.split(",") if f.strip()]
        scenario_name = "Manually Specified Files"
    else:
        print(f"{COLOR_RED}Invalid choice. Exiting.{COLOR_RESET}")
        return

    print_header(f"Simulation Scenario: {scenario_name}")
    print(f"{COLOR_BOLD}Modified Files Checked:{COLOR_RESET}")
    for f in files:
        print(f"  📄 {f}")
    print()

    # Analyze path changes
    fe_changed, be_changed, infra_changed, docs_changed = analyze_changes(files)
    
    print(f"{COLOR_BOLD}🔍 Path Filters Decision Summary:{COLOR_RESET}")
    print(f"  Frontend:       {'⚠️ CHANGED' if fe_changed else '✅ UNCHANGED'}")
    print(f"  Backend:        {'⚠️ CHANGED' if be_changed else '✅ UNCHANGED'}")
    print(f"  Infrastructure: {'⚠️ CHANGED' if infra_changed else '✅ UNCHANGED'}")
    print(f"  Documentation:  {'📝 CHANGED' if docs_changed else '✅ UNCHANGED'}")
    print()

    # Simulation results
    fe_status = "skipped"
    be_status = "skipped"
    infra_status = "skipped"

    # Execute pipelines conditionally
    print_header("Executing Conditional Pipeline Jobs")
    
    # 1. Frontend Job
    if fe_changed:
        print(f"{COLOR_BOLD}{COLOR_MAGENTA}[Job: Frontend CI]{COLOR_RESET} Triggers due to changes...")
        s1, _ = run_command("npm run lint", cwd="frontend")
        s2, _ = run_command("npm run test", cwd="frontend")
        s3, _ = run_command("npm run build", cwd="frontend")
        fe_status = "success" if (s1 and s2 and s3) else "failure"
    else:
        print(f"{COLOR_BOLD}{COLOR_CYAN}[Job: Frontend CI]{COLOR_RESET} ⏭️ SKIPPED (No frontend changes)")

    print()

    # 2. Backend Job
    if be_changed:
        print(f"{COLOR_BOLD}{COLOR_MAGENTA}[Job: Backend CI]{COLOR_RESET} Triggers due to changes...")
        s1, _ = run_command("npm run lint", cwd="backend")
        s2, _ = run_command("npm run test", cwd="backend")
        s3, _ = run_command("npm run build", cwd="backend")
        be_status = "success" if (s1 and s2 and s3) else "failure"
    else:
        print(f"{COLOR_BOLD}{COLOR_CYAN}[Job: Backend CI]{COLOR_RESET} ⏭️ SKIPPED (No backend changes)")

    print()

    # 3. Infrastructure Job
    if infra_changed:
        print(f"{COLOR_BOLD}{COLOR_MAGENTA}[Job: Infrastructure CI]{COLOR_RESET} Triggers due to changes...")
        run_command("chmod +x ./validate.sh", cwd="infrastructure")
        s1, _ = run_command("./validate.sh", cwd="infrastructure")
        infra_status = "success" if s1 else "failure"
    else:
        print(f"{COLOR_BOLD}{COLOR_CYAN}[Job: Infrastructure CI]{COLOR_RESET} ⏭️ SKIPPED (No infrastructure changes)")

    # 4. Reporting Job
    print_header("Job: Reporting (Generating Summary)")
    
    report_content = f"""### 📊 Monorepo CI/CD Report (Simulation)

**Simulation Scenario:** {scenario_name}

#### 🔍 Change Detection Analysis
- **Frontend:** {"⚠️ Changes detected" if fe_changed else "✅ No changes"}
- **Backend:** {"⚠️ Changes detected" if be_changed else "✅ No changes"}
- **Infrastructure:** {"⚠️ Changes detected" if infra_changed else "✅ No changes"}
- **Documentation:** {"📝 Changes detected" if docs_changed else "✅ No changes"}

#### 🚀 Executed Pipelines Summary
| Component | Job Status | Action Taken |
| --- | --- | --- |
| **Frontend** | {"🟢 `success`" if fe_status == "success" else "🔴 `failure`" if fe_status == "failure" else "⏭️ `skipped`"} | {"Executed Build & Test" if fe_changed else "Omitted (No code changes)"} |
| **Backend** | {"🟢 `success`" if be_status == "success" else "🔴 `failure`" if be_status == "failure" else "⏭️ `skipped`"} | {"Executed Build & Test" if be_changed else "Omitted (No code changes)"} |
| **Infrastructure** | {"🟢 `success`" if infra_status == "success" else "🔴 `failure`" if infra_status == "failure" else "⏭️ `skipped`"} | {"Executed Validation" if infra_changed else "Omitted (No code changes)"} |

---
*Report generated locally by `scripts/simulate-ci.py`.*
"""
    
    # Save the report file
    report_path = "CI_REPORT_MOCK.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"{COLOR_BOLD}{COLOR_GREEN}✅ Report generated successfully at '{report_path}'.{COLOR_RESET}\n")
    print(f"{COLOR_BOLD}Report Output Preview:{COLOR_RESET}")
    print("-" * 60)
    print(report_content)
    print("-" * 60)

if __name__ == "__main__":
    try:
        simulate_pipeline()
    except KeyboardInterrupt:
        print(f"\n{COLOR_RED}Simulation aborted by user.{COLOR_RESET}")
        sys.exit(1)
