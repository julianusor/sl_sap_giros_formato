import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io

st.title("PDF Last Page to Image Converter")

def convert_last_page_to_image(pdf_bytes):
    # Open PDF from bytes
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    # Get the last page
    last_page = pdf_document[-1]
    
    # Convert to image with high resolution
    pix = last_page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
    
    # Convert to PIL Image
    img_data = pix.tobytes("png")
    image = Image.open(io.BytesIO(img_data))
    
    pdf_document.close()
    return image

def process_pdf(uploaded_file):
    # Read the uploaded PDF
    pdf_bytes = uploaded_file.getvalue()
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(pdf_document)
    
    if total_pages < 1:
        st.error("The uploaded PDF is empty!")
        return None
    
    # Create a new PDF
    output_pdf = fitz.open()
    
    # Copy all pages except the last one directly
    for page_num in range(total_pages - 1):
        output_pdf.insert_pdf(pdf_document, from_page=page_num, to_page=page_num)
    
    # Convert last page to image and back to PDF
    last_page_image = convert_last_page_to_image(pdf_bytes)
    
    # Convert PIL Image to bytes
    img_byte_arr = io.BytesIO()
    last_page_image.save(img_byte_arr, format='PNG', resolution=300)
    img_byte_arr.seek(0)
    
    # Create new page with same dimensions as the last page
    last_page = pdf_document[-1]
    rect = last_page.rect
    new_page = output_pdf.new_page(width=rect.width, height=rect.height)
    
    # Insert image into the new page
    new_page.insert_image(rect, stream=img_byte_arr.getvalue())
    
    # Save the final PDF to bytes
    output_bytes = io.BytesIO()
    output_pdf.save(output_bytes)
    output_bytes.seek(0)
    
    pdf_document.close()
    output_pdf.close()
    
    return output_bytes

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    try:
        # Process the PDF
        output_pdf = process_pdf(uploaded_file)
        
        if output_pdf:
            # Create download button
            st.download_button(
                label="Download Processed PDF",
                data=output_pdf,
                file_name="processed.pdf",
                mime="application/pdf"
            )
            
            # Preview the last page image
            last_page_image = convert_last_page_to_image(uploaded_file.getvalue())
            st.image(last_page_image, caption="Preview of Last Page", use_column_width=True)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")