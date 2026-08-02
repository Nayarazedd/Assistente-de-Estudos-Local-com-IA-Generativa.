import webview
import subprocess
import time

processo = subprocess.Popen(["streamlit", "run", "app.py", "--server.headless", "true"])
time.sleep(3)  # espera o streamlit subir

webview.create_window("Minha IA de Estudos", "http://localhost:8501", width=1000, height=700)
webview.start()

processo.terminate()