import os, re, pathlib, subprocess
from google import genai

# 1. LEER EL LINK DEL ISSUE
issue_body = os.environ.get("ISSUE_BODY", "")
match = re.search(r'https://github\.com/[^\s]+', issue_body)
if match:
    TARGET_URL = match.group(0).strip()
else:
    TARGET_URL = "https://github.com/gsbc0416/gsbc-v11-fix-total"

print(f"Repo a auditar: {TARGET_URL}")

# 2. CLONAR
subprocess.run(["rm", "-rf", "target_repo"], check=False)
subprocess.run(["git", "clone", "--depth", "1", TARGET_URL, "target_repo"], check=True)

# 3. LEER CODIGO
codigo = ""
for p in pathlib.Path("target_repo").rglob("*"):
    if ".git" in str(p):
        continue
    if p.is_file() and p.suffix in [".py",".js",".ts",".jsx",".tsx",".json",".md",".yaml",".yml",".html"]:
        try:
            codigo += f"\n--- {p} ---\n" + p.read_text(errors="ignore")[:4000]
        except:
            pass
codigo = codigo[:50000]
print(f"Codigo leido: {len(codigo)} chars")

# 4. LLAMAR A GEMINI
API_KEY = os.environ["GEMINI_API_KEY"].strip()
client = genai.Client(api_key=API_KEY)

prompt = f"""
Eres auditor senior. Audita el repo GSBC v11 Fix Total.
Entrega INFORME FINAL en markdown en español con:
1. Resumen Ejecutivo
2. Arquitectura
3. Hallazgos Críticos (tabla con Severidad, Archivo, Problema, Fix)
4. Seguridad OWASP
5. Deuda Técnica
6. Roadmap Priorizado
7. Score 0-100

Codigo a auditar:
{codigo}
"""

resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
report = resp.text

# 5. GUARDAR Y ENTREGAR
pathlib.Path("AUDIT_REPORT.md").write_text(report, encoding="utf-8")
print(report)

# Entrega en Summary (donde sale chulito verde)
if "GITHUB_STEP_SUMMARY" in os.environ:
    with open(os.environ["GITHUB_STEP_SUMMARY"], "w", encoding="utf-8") as f:
        f.write(report)

# Entrega como comentario en el Issue
try:
    from github import Github
    token = os.environ.get("GITHUB_TOKEN")
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    issue_num = os.environ.get("ISSUE_NUMBER")
    if token and repo
