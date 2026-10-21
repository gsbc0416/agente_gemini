import os
from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
comment_body = os.environ.get("COMMENT_BODY", "")
client = genai.Client(api_key=api_key)

# Lee todo el repo para darle contexto
def get_repo_context():
    contexto = ""
    for root, _, files in os.walk("."):
        if '.git' in root or '__pycache__' in root:
            continue
        for f in files:
            if f.endswith(('.py','.js','.html','.css','.json','.md','.yml','.php','.java')):
                try:
                    path = os.path.join(root, f)
                    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                        contexto += f"\n--- {path} ---\n{file.read()[:3000]}"
                except: pass
    return contexto[:100000]

contexto = get_repo_context()

prompt = f"""
Eres un agente de desarrollo autónomo. Estás dentro de un repo de GitHub.

Petición del usuario: "{comment_body}"

Contexto actual del repo:
{contexto}

INSTRUCCIONES:
1. Si el usuario pide CREAR un archivo, genera el código completo y ponlo entre marcas: 
   FILE: ruta/del/archivo.py
   ```codigo```

2. Si el usuario pide AUDITAR, genera un informe de vulnerabilidades y buenas prácticas.

3. Si el usuario pide ARREGLAR o MEJORAR, propón el código corregido con FILE:

4. Siempre explica brevemente lo que hiciste.

Responde en español, para estudiantes de la CUN.
"""

print("Ejecutando agente maestro...")
response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
texto = response.text

# Guarda la respuesta y crea los archivos que Gemini pida
print(texto)

# Lógica simple para crear archivos automáticamente si Gemini usa FILE:
for bloque in texto.split("FILE:"):
    if "```" in bloque:
        try:
            ruta = bloque.split("\n")[0].strip()
            codigo = bloque.split("```")[1]
            # Limpia el nombre del lenguaje (python, javascript)
            if "\n" in codigo:
                codigo = "\n".join(codigo.split("\n")[1:])
            
            os.makedirs(os.path.dirname(ruta), exist_ok=True) if "/" in ruta else None
            with open(ruta, "w", encoding="utf-8") as f:
                f.write(codigo)
            print(f"Archivo creado: {ruta}")
        except Exception as e:
            print(f"No se pudo crear archivo: {e}")

# Guarda siempre la respuesta como reporte
with open("RESPUESTA_GEMINI.md", "w", encoding="utf-8") as f:
    f.write(texto)
