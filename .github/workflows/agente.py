import os, requests

key = os.environ["GEMINI_API_KEY"].strip()
print(f"Probando llave: {key[:8]}... largo {len(key)}")

# 1. Probar con API nueva (para llaves AQ.)
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
r = requests.get(url)
print(f"GET models status: {r.status_code}")
print(r.text[:1000])

if r.status_code != 200:
    print("\n>>> LA LLAVE NO SIRVE. Es por restricciones de la cuenta o no esta habilitada.")
    print("Ve a console.cloud.google.com/apis/credentials con tu cuenta PERSONAL")
    print("click en la llave AQ. > Application restrictions = None > Save")
    exit(1)

print("\n>>> LLAVE OK, ahora genera contenido")
url2 = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
resp = requests.post(url2, json={"contents":[{"parts":[{"text":"di hola"}]}]})
print(resp.status_code, resp.text[:500])
