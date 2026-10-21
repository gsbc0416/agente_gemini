import json
import os
import re
import subprocess
from google import genai

def run_git_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Git log: {result.stderr}")
    return result.stdout.strip()

def get_repo_files():
    # Obtiene la lista de archivos rastreados en el repositorio
    return run_git_command("git ls-files").splitlines()

def read_file_content(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None
    return None

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    instruction = os.environ.get("COMMENT_BODY", "").replace("/gemini", "").strip()

    if not instruction:
        print("No se proporcionó ninguna instrucción.")
        return

    # 1. Obtener la estructura del proyecto y el contenido de archivos clave
    repo_files = get_repo_files()
    context_files = {}
    
    # Leer el contenido de archivos existentes para dar contexto a Gemini
    for fpath in repo_files:
        if not fpath.startswith(".github/") and not fpath.endswith((".png", ".jpg", ".zip", ".pdf")):
            content = read_file_content(fpath)
            if content is not None and len(content) < 10000: # Límite ligero de lectura
                context_files[fpath] = content

    # 2. Inicializar cliente Gemini
    client = genai.Client(api_key=api_key)

    prompt = f"""
    Eres un agente desarrollador de software autónomo.
    Tu objetivo es modificar, corregir o crear archivos en el repositorio según la siguiente orden:

    Instrucción: {instruction}

    Archivos del repositorio y su contenido actual:
    {json.dumps(context_files, indent=2)}

    Debes responder ÚNICAMENTE con un JSON válido usando el siguiente formato exacto:
    {{
      "changes": [
        {{
          "path": "ruta/al/archivo_a_editar_o_crear.ext",
          "content": "contenido completo actualizado del archivo"
        }}
      ],
      "commit_message": "mensaje descriptivo del commit"
    }}
    No agregues texto explicativo fuera del JSON.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    # Clean Markdown formatting if output comes back wrapped in ```json
    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = re.sub(r"^```[a-z]*\n", "", raw_text)
        raw_text = re.sub(r"\n```$", "", raw_text)

    try:
        data = json.loads(raw_text)
    except Exception as e:
        print(f"Error al interpretar la respuesta JSON de Gemini: {e}")
        print("Respuesta recibida:", raw_text)
        return

    changes = data.get("changes", [])
    commit_msg = data.get("commit_message", "auto: cambios aplicados por Gemini Agent")

    if not changes:
        print("Gemini no determinó cambios a realizar.")
        return

    # 3. Aplicar las modificaciones o crear los nuevos archivos
    for change in changes:
        file_path = change["path"]
        content = change["content"]

        # Crear subdirectorios si la ruta los requiere
        dirname = os.path.dirname(file_path)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Archivo modificado/creado con éxito: {file_path}")

    # 4. Registrar los cambios en Git y subirlos
    run_git_command('git config user.name "Gemini Agent Bot"')
    run_git_command('git config user.email "gemini-bot@users.noreply.github.com"')
    run_git_command("git add .")
    run_git_command(f'git commit -m "{commit_msg}"')
    run_git_command("git push")

if __name__ == "__main__":
    main()
