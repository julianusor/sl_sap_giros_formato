import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io

st.title("Convertidor de Primera y Última Página de PDF a Imágenes")

def convertir_pagina_a_imagen(pdf_bytes, numero_pagina):
    # Abrir PDF desde bytes
    pdf_documento = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    # Obtener la página especificada
    pagina = pdf_documento[numero_pagina]
    
    # Convertir a imagen con alta resolución
    pix = pagina.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
    
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
    
    # Convertir la primera página a imagen y añadir al PDF
    imagen_primera_pagina = convertir_pagina_a_imagen(pdf_bytes, 0)
    
    # Convertir la última página a imagen y añadir al PDF
    imagen_ultima_pagina = convertir_pagina_a_imagen(pdf_bytes, total_paginas - 1)
    
    # Convertir imágenes PIL a bytes
    img_byte_arr_primera = io.BytesIO()
    imagen_primera_pagina.save(img_byte_arr_primera, format='PNG', resolution=300)
    img_byte_arr_primera.seek(0)
    
    img_byte_arr_ultima = io.BytesIO()
    imagen_ultima_pagina.save(img_byte_arr_ultima, format='PNG', resolution=300)
    img_byte_arr_ultima.seek(0)
    
    # Crear páginas nuevas con las mismas dimensiones
    primera_pagina = pdf_documento[0]
    ultima_pagina = pdf_documento[-1]
    rect_primera = primera_pagina.rect
    rect_ultima = ultima_pagina.rect
    
    nueva_pagina_primera = pdf_salida.new_page(width=rect_primera.width, height=rect_primera.height)
    nueva_pagina_primera.insert_image(rect_primera, stream=img_byte_arr_primera.getvalue())
    
    nueva_pagina_ultima = pdf_salida.new_page(width=rect_ultima.width, height=rect_ultima.height)
    nueva_pagina_ultima.insert_image(rect_ultima, stream=img_byte_arr_ultima.getvalue())
    
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
            
            # Vista previa de la primera y última página como imágenes
            imagen_primera_pagina = convertir_pagina_a_imagen(archivo_subido.getvalue(), 0)
            st.image(imagen_primera_pagina, caption="Vista previa de la primera página", use_column_width=True)
            
            imagen_ultima_pagina = convertir_pagina_a_imagen(archivo_subido.getvalue(), len(fitz.open(stream=archivo_subido.getvalue(), filetype="pdf")) - 1)
            st.image(imagen_ultima_pagina, caption="Vista previa de la última página", use_column_width=True)
            
    except Exception as e:
        st.error(f"Ocurrió un error: {str(e)}")
