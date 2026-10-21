import os, re, subprocess
from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
comment = os.environ.get("COMMENT_BODY", "")
client = genai.Client(api_key=api_key)

# 1. Detecta si el usuario pasó un link de otro repo
# Ej: /gemini audita https://github.com/usuario/mi-proyecto
match = re.search(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", comment)
repo_a_auditar = "."
if match:
    repo_url = f"https://github.com/{match.group(1)}.git"
    print(f"Clonando repo externo: {repo_url}")
    subprocess.run(f"rm -rf /tmp/auditar && git clone {repo_url} /tmp/auditar", shell=True)
    repo_a_auditar = "/tmp/auditar"
else:
    print("Auditando el repo actual")

# 2. Lee los archivos del repo objetivo
def leer_repo(path_base):
    contexto = ""
    for root, _, files in os.walk(path_base):
        if '.git' in root or '__pycache__' in root or 'node_modules' in root:
            continue
        for f in files:
            if f.endswith(('.py','.js','.html','.css','.json','.md','.yml','.php','.java','.env')):
                try:
                    full_path = os.path.join(root, f)
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as file:
                        contexto += f"\n--- {full_path} ---\n{file.read()[:4000]}"
                except: pass
    return contexto[:120000]

contexto_repo = leer_repo(repo_a_auditar)

prompt = f"""
Eres un auditor Senior de ciberseguridad de la CUN.
Petición: "{comment}"
Audita este código:

{contexto_repo}

Entrega un informe en Markdown con:
1. Vulnerabilidades CRÍTICAS (claves expuestas, SQLi, XSS)
2. Errores de lógica
3. Buenas prácticas que faltan
4. Calificación 0-10
5. Código corregido si aplica
"""

response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)

with open("AUDIT_REPORT.md", "w", encoding="utf-8") as f:
    f.write(f"# Auditoría para: {repo_a_auditar}\nPetición: {comment}\n\n" + response.text)

print(response.text)
