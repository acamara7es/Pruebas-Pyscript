import csv
import pandas as pd
from js import document, window, Uint8Array, Blob
from io import BytesIO
from pyscript import when
from reportlab.pdfgen import canvas
#from reportlab_tools import generate_pdf

#@TODO proceso del archivo con pandas, quedarse con las columnas que necesitamos
# y generar un array con los datos de las etiquetas
def process_file(data):
    products_df = pd.read_csv(data,delimiter=';')


async def import_file(file):
    array_buf = await file.arrayBuffer() # Get arrayBuffer from file
    file_bytes = array_buf.to_bytes() # convert to raw bytes array
    csv_file = BytesIO(file_bytes) # Wrap in Python BytesIO file-like object
    return csv_file

def download_pdf(pdf_bytes):
    # Convertir los bytes a un formato que JavaScript entienda (Uint8Array)
    js_array = Uint8Array.new(len(pdf_bytes))
    js_array.assign(pdf_bytes)

    # 5. Crear un Blob y disparar la descarga mediante JS
    blob = Blob.new([js_array], {type: "application/pdf"})
    url = window.URL.createObjectURL(blob)

    # Crear un enlace temporal de descarga de forma dinámica
    link = document.createElement("a")
    link.href = url
    link.download = "labels.pdf"

    # Simular el clic en el enlace para descargar
    link.click()

    # Limpiar memoria liberando el objeto URL creado
    window.URL.revokeObjectURL(url)

def temp():
    data = []
    with open('Office_Address_List.txt', 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        for fila in reader:
            if len(fila) >= 4:
                label = [fila[0], fila[1], fila[2], fila[3]]
                data.append(label)
    return data


@when("change","#file-upload")
def generate_labels(e):
    buffer = BytesIO()
    #file = import_file(e.target.files.item(0))
    #labels_data = process_file(file)
    labels_data = temp()
    generate_pdf(labels_data, buffer)
    download_pdf(buffer.getvalue())
    prueba()

    print("CSV procesado")

def prueba():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(595.27, 841.89))  # A4 pagesize
    c.drawString(50, 780, "Hello Again")
    # finish page
    c.showPage()
    # construct and save file to .pdf
    c.save()
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    print("Hello, World!")

#######################################################################
#######################################################################
#######################################################################

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

#ruta_courier = "C:\\Windows\\Fonts\\cour.ttf"
#ruta_courier_bold = "C:\\Windows\\Fonts\\courbd.ttf"
from pyodide.http import pyfetch
async def get_font():
    # 1. Descargar la fuente desde tu servidor o CDN
    response = await pyfetch("https://raw.githubusercontent.com/acamara7es/Pruebas-Pyscript/refs/heads/main/cour.ttf")
    font_bytes = await response.bytes()

    # 2. Guardar el archivo en el sistema de archivos virtual
    with open("cour.ttf", "wb") as f:
        f.write(font_bytes)

    pdfmetrics.registerFont(TTFont('Courier New', "cour.ttf"))
    pdfmetrics.registerFont(TTFont('Courier New-Bold', "courb.ttf"))

# Configuración del documento A4 (21.0 cm x 29.7 cm)
# 2 columnas de 10.5 cm ocupan todo el ancho. 11 filas de 2.6 cm = 28.6 cm.
# Margen superior e inferior restante: (29.7 - 28.6) / 2 = 0.55 cm.

async def main():
    print("HOAL")
    await get_font()
    print("HOLA")

row_heights = [25 * mm, 26 * mm, 25 * mm, 25 * mm, 26 * mm, 25 * mm, 26 * mm, 25 * mm, 25 * mm, 26 * mm, 25 * mm]

# Definición de estilos usando Courier y tamaño 12
estilo_base = ParagraphStyle(
    'EstiloBase',
    fontName='Courier New',
    fontSize=16,
    leading=19,
)
estilo_cod_nacional = ParagraphStyle(
    'EstiloCN',
    parent=estilo_base,
    alignment=2  # 2 = Alineado a la derecha
)
estilo_ubicacion = ParagraphStyle(
    'EstiloUbicacion',
    leading=28,
    fontSize=24,
    fontName='Courier New-Bold'
)
estilo_reserva = ParagraphStyle(
    'EstiloReserva',
    parent=estilo_base,
    fontName='Courier New-Bold'
)
estilo_descripcion = ParagraphStyle(
    'EstiloDescripcion',
    parent=estilo_base,
    fontSize=15,
    leading=18,
)

label_style = TableStyle([
	('SPAN',(0,0),(1,0)),
	('SPAN',(0,1),(-1,1)),
	('SPAN',(1,2),(-1,2)),
	('VALIGN',(0,0),(-1,-1),'MIDDLE'),
	('TOPPADDING',(0,0),(-1,0),10),
	('TOPPADDING',(0,1),(-1,1),5),
	('VALIGN',(0,2),(-1,2),'BOTTOM'),
	('LEFTPADDING',(1,2),(1,2),-5),
])

page_style = TableStyle([
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('TOPPADDING', (0,0), (-1,-1), 2),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ('LEFTPADDING', (0,0), (-1,-1), 6),
    ('RIGHTPADDING', (0,0), (-1,-1), 6),
])


def build_labels(data):
    labels_list = []
    for i in data:
        location, description, code, dynamic = i[0], i[1], i[2], i[3]
        label = Table(
            [[Paragraph(location,estilo_ubicacion), '', Paragraph(f"CN:{code}", estilo_cod_nacional)],
            [Paragraph(description, estilo_descripcion)],
            [Paragraph(f"D:", estilo_cod_nacional),Paragraph(dynamic, estilo_reserva),'']],
        rowHeights=[9 * mm, 10 * mm, 6 * mm],
        colWidths=[16 * mm, 46 * mm, 39 * mm]
        )
        label.setStyle(label_style)
        label.append(labels_list)
    return labels_list

def bla(labels):
    columnas = 2
    matriz_final = []
    fila_temporal = []

    for etiqueta in labels:
        fila_temporal.append(etiqueta)
        if len(fila_temporal) == columnas:
            matriz_final.append(fila_temporal)
            fila_temporal = []
    if fila_temporal:
        while len(fila_temporal) < columnas:
            fila_temporal.append("")
        matriz_final.append(fila_temporal)
    return matriz_final


def generate_pdf(labels_data,buffer):
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        leftMargin=0, rightMargin=0,
        topMargin=6 * mm, bottomMargin=6 * mm
    )
    labels = build_labels(labels_data)
    matrix = bla(labels)
    document = Table(matrix, colWidths=[105 * mm, 105 * mm], rowHeights=row_heights)
    document.setStyle(TableStyle)
    doc.build([document])
    print("¡PDF generado con éxito!")

print("BLA")
main()
