import streamlit as st
import subprocess

st.set_page_config(page_title="Enterprise OSINT System", page_icon="🔍", layout="centered")

st.title("🔍 Enterprise OSINT System")
st.write("Enter a target identifier below to scan public platforms natively on Windows.")

# 1. User Input Box
target = st.text_input("Target Username:", placeholder="e.g., Felecarious").strip()

if st.button("Launch System Scan", type="primary"):
    if not target:
        st.warning("Please input a target name first.")
    else:
        with st.spinner(f"System actively hunting profiles for '{target}'..."):
            
            # We remove all file output flags completely to read the raw terminal screen instead
            command = [
                "python", "-m", "sherlock_project", 
                target, 
                "--timeout", "1"
            ]
            
            try:
                # Capture everything printed to the terminal screen directly into Python memory
                result = subprocess.run(
                    command, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    shell=True
                )
                
                discovered_links = []
                
                # Split the screen output line-by-line and isolate the links
                if result.stdout:
                    for line in result.stdout.splitlines():
                        if "http" in line:
                            # Strip out Sherlock's terminal text formatting to isolate the URL
                            parts = line.split()
                            for part in parts:
                                if part.startswith("http"):
                                    discovered_links.append(part.strip())
                
                # 2. Display Visual Results Directly to the Web Page
                if discovered_links:
                    st.success(f"Scan complete! Discovered {len(discovered_links)} footprints.")
                    st.subheader("📋 Discovered Intelligence Footprint")
                    for link in discovered_links:
                        st.markdown(f"• [{link}]({link})")
                else:
                    st.info(f"Scan completed, but no public profile endpoints were returned for '{target}'.")
                    
            except Exception as e:
                st.error(f"System pipeline failure: {e}")




