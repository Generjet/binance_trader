import streamlit as st
import subprocess
import os
import time
import schedule
import threading

st.title("Python Script Scheduler")

uploaded_file = st.file_uploader("Upload your Python script", type="py")

schedule_interval = st.selectbox(
    "Select schedule interval",
    ["1h", "30m", "5m"]
)

if uploaded_file is not None:
    script_path = "uploaded_script.py"
    with open(script_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    st.write("Uploaded script:")
    st.code(uploaded_file.getvalue().decode())

    def run_script():
        command = ["python", script_path]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stderr:
            st.error(f"Error running script: {stderr.decode()}")
        else:
            st.success(f"Script executed successfully at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            st.write("Output:")
            st.code(stdout.decode())

    if st.button("Run Script Now"):
        run_script()

    st.write(f"Selected schedule: {schedule_interval}")

    def schedule_script():
        if schedule_interval == "1h":
            schedule.every().hour.do(run_script)
        elif schedule_interval == "30m":
            schedule.every(30).minutes.do(run_script)
        elif schedule_interval == "5m":
            schedule.every(5).minutes.do(run_script)
        while True:
            schedule.run_pending()
            time.sleep(1)

    if st.button("Schedule Script"):
        threading.Thread(target=schedule_script, daemon=True).start() # Set daemon=True
        st.success(f"Script scheduled to run every {schedule_interval}")
