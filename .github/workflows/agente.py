import os, pathlib, subprocess
from google import genai

key = os.environ["GEMINI_API_KEY"].strip()
target = "https://github.com/gsbc0416/gsbc-v11-fix-total"

subprocess.run(["git", "clone", "--depth", "1", target, "target_repo"], check=False)
# Junta todo el código
all_code = ""
for p in pathlib.Path("target_repo").rglob("*.py"):
    if ".git" in str(p): continue
    try: all_code += f"\n--- ARCHIVO: {p} ---\n" + p.read_text(errors="ignore")[:4000]
    except: pass
all_code = all_code[:30000]

client = genai.Client(api_key=key)
prompt = f"""
Audita a fondo el proyecto GSBC v11 fix total.
Analiza este codigo:
{all_code}

Entrega informe en markdown con:
# Informe de Auditoría GSBC v11 - Fix Total
## 1. Resumen Ejecutivo
## 2. Arquitectura detectada
## 3. Hallazgos Críticos (bugs, seguridad)
## 4. Deuda técnica
## 5. Recomendaciones priorizadas
## 6. Conclusión y nivel de riesgo
Se profesional, directo y tecnico.
"""

resp = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
report = resp.text
open("AUDIT_REPORT.md","w",encoding="utf-8").write(report)
print(report)
# Guardar para que Actions lo muestre
with open(os.environ.get("GITHUB_STEP_SUMMARY","summary.md"),"w") as f:
    f.write(report)
