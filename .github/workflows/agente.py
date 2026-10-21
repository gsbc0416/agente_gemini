import os
import google.generativeai as genai

api_key = os.environ["GEMINI_API_KEY"]
comment = os.environ["COMMENT_BODY"]

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

prompt = f"Eres un auditor de código senior. Audita este repo y genera un reporte en markdown: {comment}"

response = model.generate_content(prompt)

with open("AUDIT_REPORT.md", "w", encoding="utf-8") as f:
    f.write(response.text)

print("AUDITADO OK")
print(response.text)
