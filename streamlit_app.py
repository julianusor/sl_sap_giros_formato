import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io

st.title("Convertidor de Última Página de PDF a Imagen")

def convertir_ultima_pagina_a_imagen(pdf_bytes):
    # Abrir PDF desde bytes
    pdf_documento = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    # Obtener la última página
    ultima_pagina = pdf_documento[-1]
    
    # Convertir a imagen con alta resolución
    pix = ultima_pagina.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
    
    # Convertir a imagen PIL
    img_datos = pix.tobytes("png")
    imagen = Image.open(io.BytesIO(img_datos))
    
    pdf_documento.close()
    return imagen

def procesar_pdf(archivo_subido):
    # Leer el PDF subido
    pdf_bytes = archivo_subido.getvalue()
    pdf_documento = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_paginas = len(pdf_documento)
    
    if total_paginas < 1:
        st.error("¡El PDF subido está vacío!")
        return None
    
    # Crear un nuevo PDF
    pdf_salida = fitz.open()
    
    # Copiar todas las páginas excepto la última
    for numero_pagina in range(total_paginas - 1):
        pdf_salida.insert_pdf(pdf_documento, from_page=numero_pagina, to_page=numero_pagina)
    
    # Convertir la última página a imagen y luego de vuelta a PDF
    imagen_ultima_pagina = convertir_ultima_pagina_a_imagen(pdf_bytes)
    
    # Convertir imagen PIL a bytes
    img_byte_arr = io.BytesIO()
    imagen_ultima_pagina.save(img_byte_arr, format='PNG', resolution=300)
    img_byte_arr.seek(0)
    
    # Crear una nueva página con las mismas dimensiones que la última página
    ultima_pagina = pdf_documento[-1]
    rect = ultima_pagina.rect
    nueva_pagina = pdf_salida.new_page(width=rect.width, height=rect.height)
    
    # Insertar imagen en la nueva página
    nueva_pagina.insert_image(rect, stream=img_byte_arr.getvalue())
    
    # Guardar el PDF final en bytes
    salida_bytes = io.BytesIO()
    pdf_salida.save(salida_bytes)
    salida_bytes.seek(0)
    
    pdf_documento.close()
    pdf_salida.close()
    
    return salida_bytes

# Cargador de archivos
archivo_subido = st.file_uploader("Elige un archivo PDF", type="pdf")

if archivo_subido is not None:
    try:
        # Procesar el PDF
        pdf_salida = procesar_pdf(archivo_subido)
        
        if pdf_salida:
            # Crear botón de descarga
            st.download_button(
                label="Descargar PDF Procesado",
                data=pdf_salida,
                file_name="procesado.pdf",
                mime="application/pdf"
            )
            
            # Vista previa de la última página como imagen
            imagen_ultima_pagina = convertir_ultima_pagina_a_imagen(archivo_subido.getvalue())
            st.image(imagen_ultima_pagina, caption="Vista previa de la última página", use_column_width=True)
            
    except Exception as e:
        st.error(f"Ocurrió un error: {str(e)}")
