import tkinter as tk
from tkinter import messagebox
import os
import random
import json
import openai
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Tu API Key de OpenAI 
openai.api_key = "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"

# Carpeta de salida
DOCUMENTOS = os.path.join(os.path.expanduser("~"), "Documents", "ExamenesGenerados")
os.makedirs(DOCUMENTOS, exist_ok=True)

banco_preguntas = {
    "matematicas": [
        {"pregunta": "¿Cuánto es 5 + 7?", "opciones": ["12", "10", "14", "15"], "respuesta": "12"},
        {"pregunta": "¿Cuál es el resultado de 9 × 3?", "opciones": ["27", "21", "30", "24"], "respuesta": "27"},
    ],
    "ciencias": [
        {"pregunta": "¿Qué órgano bombea la sangre?", "opciones": ["Corazón", "Pulmón", "Estómago", "Riñón"], "respuesta": "Corazón"},
        {"pregunta": "¿Qué planeta es el más cercano al Sol?", "opciones": ["Mercurio", "Venus", "Tierra", "Marte"], "respuesta": "Mercurio"},
    ],
    "historia": [
        {"pregunta": "¿Quién descubrió América?", "opciones": ["Cristóbal Colón", "Napoleón", "Simón Bolívar", "Marco Polo"], "respuesta": "Cristóbal Colón"},
        {"pregunta": "¿En qué año fue la Revolución Francesa?", "opciones": ["1789", "1492", "1810", "1914"], "respuesta": "1789"},
    ],
    "geografia": [
        {"pregunta": "¿Cuál es el río más largo del mundo?", "opciones": ["Amazonas", "Nilo", "Yangtsé", "Misisipi"], "respuesta": "Amazonas"},
        {"pregunta": "¿Dónde está la cordillera de los Andes?", "opciones": ["Sudamérica", "África", "Europa", "Asia"], "respuesta": "Sudamérica"},
    ],
    "lenguaje": [
        {"pregunta": "¿Qué es un sustantivo?", "opciones": ["Nombre de persona, lugar o cosa", "Verbo de acción", "Adjetivo que describe", "Pronombre personal"], "respuesta": "Nombre de persona, lugar o cosa"},
        {"pregunta": "¿Cuál es la vocal abierta?", "opciones": ["A", "E", "I", "U"], "respuesta": "A"},
    ]
}

# Funciones auxiliares
def obtener_preguntas_mezcladas(banco, temas_seleccionados, total_preguntas):
    preguntas_seleccionadas = []
    while len(preguntas_seleccionadas) < total_preguntas:
        tema = random.choice(temas_seleccionados)
        pregunta = random.choice(banco[tema])
        if pregunta not in preguntas_seleccionadas:
            preguntas_seleccionadas.append(pregunta)
    return preguntas_seleccionadas

def crear_pdf(nombre_archivo, titulo, preguntas, mostrar_respuestas=False):
    c = canvas.Canvas(nombre_archivo, pagesize=A4)
    width, height = A4
    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, titulo)
    y -= 40
    c.setFont("Helvetica", 12)
    for i, p in enumerate(preguntas, start=1):
        if y < 100:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 12)
        c.drawString(50, y, f"{i}. {p['pregunta']}")
        y -= 20
        opciones = p['opciones'].copy()
        random.shuffle(opciones)
        for j, op in enumerate(opciones):
            c.drawString(70, y, f"{chr(65 + j)}) {op}")
            y -= 20
        if mostrar_respuestas:
            c.drawString(70, y, f"✔ Respuesta: {p['respuesta']}")
            y -= 20
        y -= 10
    c.save()

def generar_examenes():
    try:
        num_estudiantes = int(entry_estudiantes.get())
        num_preguntas = int(entry_preguntas.get())
    except ValueError:
        messagebox.showerror("Error", "Ingrese números válidos.")
        return

    temas_seleccionados = [tema for tema, var in checks.items() if var.get()]
    if not temas_seleccionados:
        messagebox.showerror("Error", "Debe seleccionar al menos un tema.")
        return

    for est in range(1, num_estudiantes + 1):
        preguntas = obtener_preguntas_mezcladas(banco_preguntas, temas_seleccionados, num_preguntas)
        archivo_exam = os.path.join(DOCUMENTOS, f"examen_estudiante_{est}.pdf")
        archivo_resp = os.path.join(DOCUMENTOS, f"respuestas_estudiante_{est}.pdf")

        crear_pdf(archivo_exam, f"Examen Estudiante #{est}", preguntas)
        crear_pdf(archivo_resp, f"Respuestas Estudiante #{est}", preguntas, mostrar_respuestas=True)

    messagebox.showinfo("Éxito", f"Exámenes generados en:\n{DOCUMENTOS}")

def generar_preguntas_gpt(tema, cantidad):
    prompt = f"""
    Genera {cantidad} preguntas tipo test de educación básica sobre el tema "{tema}".
    Cada pregunta debe tener 4 opciones y una respuesta correcta.
    Devuelve un JSON como este:

    [
      {{
        "pregunta": "...",
        "opciones": ["A", "B", "C", "D"],
        "respuesta": "A"
      }},
      ...
    ]
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        content = response.choices[0].message.content.strip()
        preguntas = json.loads(content)
        return preguntas

    except Exception as e:
        messagebox.showerror("Error con GPT", str(e))
        return []

def generar_con_gpt():
    tema = entry_tema_gpt.get().strip()
    try:
        cantidad = int(entry_num_gpt.get())
    except ValueError:
        messagebox.showerror("Error", "Cantidad GPT no válida.")
        return

    preguntas = generar_preguntas_gpt(tema, cantidad)
    if not preguntas:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_exam = os.path.join(DOCUMENTOS, f"examen_GPT_{tema}_{timestamp}.pdf")
    archivo_resp = os.path.join(DOCUMENTOS, f"respuestas_GPT_{tema}_{timestamp}.pdf")

    crear_pdf(archivo_exam, f"Examen GPT - {tema.capitalize()}", preguntas)
    crear_pdf(archivo_resp, f"Respuestas GPT - {tema.capitalize()}", preguntas, mostrar_respuestas=True)

    messagebox.showinfo("GPT", f"Examen con GPT generado:\n{archivo_exam}")

# Interfaz Gráfica
ventana = tk.Tk()
ventana.title("Generador de Exámenes con GPT")
ventana.geometry("400x650")

tk.Label(ventana, text="📘 Generador de Exámenes", font=("Helvetica", 16)).pack(pady=10)

tk.Label(ventana, text="Número de estudiantes:").pack()
entry_estudiantes = tk.Entry(ventana)
entry_estudiantes.insert(0, "10")
entry_estudiantes.pack(pady=5)

tk.Label(ventana, text="Número de preguntas por examen:").pack()
entry_preguntas = tk.Entry(ventana)
entry_preguntas.insert(0, "10")
entry_preguntas.pack(pady=5)

tk.Label(ventana, text="Selecciona los temas:").pack(pady=10)
checks = {}
for tema in banco_preguntas.keys():
    var = tk.BooleanVar(value=True)
    checks[tema] = var
    tk.Checkbutton(ventana, text=tema.capitalize(), variable=var).pack(anchor="w")

tk.Button(ventana, text=" Generar Exámenes", command=generar_examenes, bg="green", fg="white").pack(pady=15)

tk.Label(ventana, text="Tema para preguntas GPT:").pack(pady=(20, 0))
entry_tema_gpt = tk.Entry(ventana)
entry_tema_gpt.insert(0, "historia")
entry_tema_gpt.pack(pady=5)

tk.Label(ventana, text="Cantidad de preguntas GPT:").pack()
entry_num_gpt = tk.Entry(ventana)
entry_num_gpt.insert(0, "5")
entry_num_gpt.pack(pady=5)

tk.Button(ventana, text=" Generar con GPT", command=generar_con_gpt, bg="#007acc", fg="white").pack(pady=20)

ventana.mainloop()
