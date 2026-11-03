import subprocess
import json
import os
import glob
from datetime import datetime

def run_username_recon(target_name):
    print(f"[*] [System Log] Beginning automated hunt for: {target_name}")
    
    # We pass the filename to Sherlock, but we will find it dynamically afterwards
    output_filename = f"{target_name}_raw.txt"
    
    command = [
        "python", "-m", "sherlock_project", 
        target_name, 
        "--output", output_filename,
        "--print-found"
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"[+] [System Log] Raw network footprint data captured.")
        return output_filename
    except subprocess.CalledProcessError as e:
        print(f"[!] System Error calling recon engine: {e}")
        return None

def generate_system_report(target_name):
    print(f"[*] [System Log] Scanning system workspace for generated files...")
    
    # Search everywhere recursively for any file containing the target's username
    search_pattern = os.path.join(os.getcwd(), "**", f"*{target_name}*")
    found_files = glob.glob(search_pattern, recursive=True)
    
    final_source_path = None
    for file_path in found_files:
        # Ignore our main script file and our finalized report files
        if "osint_system.py" not in file_path and "SYSTEM_REPORT" not in file_path:
            if file_path.endswith(".txt") or file_path.endswith(".json"):
                final_source_path = file_path
                break
                
    if not final_source_path:
        print(f"[!] System Error: Could not locate the raw output file for '{target_name}'.")
        return
        
    print(f"[*] [System Log] Successfully intercepted source data path: {final_source_path}")
    print(f"[*] [System Log] Processing intelligence feed and normalizing records...")
    
    discovered_links = []
    
    # Handle both text logs or json objects cleanly
    try:
        if final_source_path.endswith(".json"):
            with open(final_source_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Map standard structures
                for platform, details in data.items():
                    url = details.get("url_user") if isinstance(details, dict) else str(details)
                    if "http" in url:
                        discovered_links.append({"platform": platform.capitalize(), "url": url})
        else:
            with open(final_source_path, "r", encoding="utf-8") as f:
                for line in f:
                    line_str = line.strip()
                    if line_str and "http" in line_str:
                        # Extract the platform name cleanly from the domain string topology
                        domain_parts = line_str.split("/")
                        platform_name = "Target Profile"
                        if len(domain_parts) >= 3:
                            clean_domain = domain_parts[2].replace("www.", "")
                            platform_name = clean_domain.split(".")[0].capitalize()
                        
                        discovered_links.append({
                            "platform": platform_name,
                            "url": line_str
                        })
    except Exception as e:
        print(f"[!] Failed to parse source logs: {e}")
        return
        
    # Build uniform enterprise schema output asset
    system_report = {
        "system_metadata": {
            "classification": "RESTRICTED // OSINT INTERNAL",
            "generation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "target_identifier": target_name,
            "total_records_discovered": len(discovered_links),
            "execution_environment": "Windows-Native x64 / Python 3.14"
        },
        "intelligence_footprint": discovered_links
    }

    output_filename = f"SYSTEM_REPORT_{target_name}.json"
    with open(output_filename, "w", encoding="utf-8") as out_f:
        json.dump(system_report, out_f, indent=4)
        
    print(f"\n[V] SUCCESS: System Target Profile compiled cleanly!")
    print(f"[V] Final Data Package Location: {os.getcwd()}\\{output_filename}")
    
    # Securely shred raw intermediary file trails
    try:
        os.remove(final_source_path)
    except OSError:
        pass

if __name__ == "__main__":
    target = input("Enter target username for system intake: ").strip()
    if target:
        if run_username_recon(target):
            generate_system_report(target)


