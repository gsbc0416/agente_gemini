import os
import subprocess
from google import genai

def run_git_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def main():
    api_key = os.environ.get("GEMINI_API_KEY")
    instruction = os.environ.get("COMMENT_BODY", "").replace("/gemini", "").strip()

    if not instruction:
        print("No se proporcionó ninguna instrucción.")
        return

    # Inicializar el cliente de Gemini
    client = genai.Client(api_key=api_key)

    # Prompt para indicarle a Gemini que actúe como agente programador
    prompt = f"""
    Eres un agente programador experto. Tu tarea es cumplir la siguiente instrucción en este repositorio:
    
    Instrucción: {instruction}
    
    Genera el código o las modificaciones necesarias. Si debes crear o editar un archivo, especifica claramente las modificaciones.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    print("Respuesta del Agente Gemini:\n", response.text)

    # Configurar Git para hacer el commit automáticamente
    run_git_command('git config user.name "Gemini Agent Bot"')
    run_git_command('git config user.email "gemini-bot@users.noreply.github.com"')
    
    # Aquí puedes guardar respuestas o modificaciones directas
    with open("GEMINI_OUTPUT.md", "w", encoding="utf-8") as f:
        f.write(response.text)

    run_git_command("git add GEMINI_OUTPUT.md")
    run_git_command('git commit -m "auto: cambios aplicados por Gemini Agent"')
    run_git_command("git push")

if __name__ == "__main__":
    main()
