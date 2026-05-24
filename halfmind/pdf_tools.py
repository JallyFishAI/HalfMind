import os
import hashlib
from pathlib import Path


class PDFTools:
    """Tools for PDF file manipulation and processing"""
    
    ALLOWED_EXTENSIONS = {'.pdf'}
    MAX_FILE_SIZE = 100 * 1024 * 1024
    
    def __init__(self):
        self.extracted_text_cache = {}
    
    def _validate_path(self, path, must_exist=True):
        """Validates PDF file path for security"""
        resolved = Path(path).resolve()
        if must_exist:
            if not resolved.exists():
                raise FileNotFoundError(f"File not found: {path}")
            if resolved.suffix.lower() not in self.ALLOWED_EXTENSIONS:
                raise ValueError(f"Invalid file extension: {resolved.suffix}")
            if resolved.stat().st_size > self.MAX_FILE_SIZE:
                raise ValueError("File size exceeds maximum allowed")
        return str(resolved)
    
    def _compute_hash(self, file_path):
        """Computes SHA256 hash of a file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def extract_text(self, pdf_path, page_numbers=None):
        """Extracts text from PDF, optionally from specific pages"""
        import PyPDF4
        validated_path = self._validate_path(pdf_path)
        text_content = []
        with open(validated_path, 'rb') as file:
            reader = PyPDF4.PdfFileReader(file)
            total_pages = reader.numPages
            if page_numbers is None:
                page_numbers = range(total_pages)
            for page_num in page_numbers:
                if page_num < 0 or page_num >= total_pages:
                    raise ValueError(f"Invalid page number: {page_num}")
                page = reader.getPage(page_num)
                text_content.append(page.extractText())
        return '\n'.join(text_content)
    
    def get_pdf_info(self, pdf_path):
        """Returns metadata and information about a PDF file"""
        import PyPDF4
        validated_path = self._validate_path(pdf_path)
        with open(validated_path, 'rb') as file:
            reader = PyPDF4.PdfFileReader(file)
            info = reader.getDocumentInfo()
            return {
                'title': info.get('/Title', ''),
                'author': info.get('/Author', ''),
                'subject': info.get('/Subject', ''),
                'creator': info.get('/Creator', ''),
                'producer': info.get('/Producer', ''),
                'pages': reader.numPages,
                'encrypted': reader.isEncrypted,
                'file_size': os.path.getsize(validated_path),
                'file_hash': self._compute_hash(validated_path)
            }
    
    def merge_pdfs(self, pdf_paths, output_path):
        """Merges multiple PDF files into one"""
        import PyPDF4
        validated_output = self._validate_path(output_path, must_exist=False)
        merger = PyPDF4.PdfFileMerger()
        for pdf_path in pdf_paths:
            validated_input = self._validate_path(pdf_path)
            merger.append(validated_input)
        with open(validated_output, 'wb') as output_file:
            merger.write(output_file)
        merger.close()
        return True
    
    def split_pdf(self, pdf_path, output_dir, page_ranges=None):
        """Splits a PDF into separate files based on page ranges"""
        import PyPDF4
        validated_path = self._validate_path(pdf_path)
        os.makedirs(output_dir, exist_ok=True)
        with open(validated_path, 'rb') as file:
            reader = PyPDF4.PdfFileReader(file)
            total_pages = reader.numPages
            if page_ranges is None:
                page_ranges = [(i, i) for i in range(total_pages)]
            output_files = []
            for idx, (start, end) in enumerate(page_ranges):
                writer = PyPDF4.PdfFileWriter()
                for page_num in range(start, min(end + 1, total_pages)):
                    writer.addPage(reader.getPage(page_num))
                output_file = os.path.join(output_dir, f"split_{idx + 1}.pdf")
                with open(output_file, 'wb') as out:
                    writer.write(out)
                output_files.append(output_file)
        return output_files
    
    def extract_pages(self, pdf_path, output_path, page_numbers):
        """Extracts specific pages from a PDF"""
        import PyPDF4
        validated_path = self._validate_path(pdf_path)
        validated_output = self._validate_path(output_path, must_exist=False)
        with open(validated_path, 'rb') as file:
            reader = PyPDF4.PdfFileReader(file)
            writer = PyPDF4.PdfFileWriter()
            for page_num in page_numbers:
                if page_num < 0 or page_num >= reader.numPages:
                    raise ValueError(f"Invalid page number: {page_num}")
                writer.addPage(reader.getPage(page_num))
            with open(validated_output, 'wb') as out:
                writer.write(out)
        return True
    
    def rotate_pages(self, pdf_path, output_path, rotation=90, page_numbers=None):
        """Rotates specified pages in a PDF"""
        import PyPDF4
        validated_path = self._validate_path(pdf_path)
        validated_output = self._validate_path(output_path, must_exist=False)
        with open(validated_path, 'rb') as file:
            reader = PyPDF4.PdfFileReader(file)
            writer = PyPDF4.PdfFileWriter()
            for page_num in range(reader.numPages):
                page = reader.getPage(page_num)
                if page_numbers is None or page_num in page_numbers:
                    page.rotateClockwise(rotation)
                writer.addPage(page)
            with open(validated_output, 'wb') as out:
                writer.write(out)
        return True
    
    def add_page_numbers(self, pdf_path, output_path):
        """Adds page numbers to a PDF"""
        import PyPDF4
        from io import BytesIO
        from reportlab.pdfgen import canvas
        validated_path = self._validate_path(pdf_path)
        validated_output = self._validate_path(output_path, must_exist=False)
        with open(validated_path, 'rb') as file:
            reader = PyPDF4.PdfFileReader(file)
            writer = PyPDF4.PdfFileWriter()
            for page_num in range(reader.numPages):
                page = reader.getPage(page_num)
                packet = BytesIO()
                can = canvas.Canvas(packet)
                can.setFont("Helvetica", 10)
                can.drawCentredString(page.mediaBox.getWidth() / 2, 30, f"Page {page_num + 1}")
                can.save()
                packet.seek(0)
                overlay = PyPDF4.PdfFileReader(packet)
                page.mergePage(overlay.getPage(0))
                writer.addPage(page)
            with open(validated_output, 'wb') as out:
                writer.write(out)
        return True
    
    def encrypt_pdf(self, pdf_path, output_path, user_password, owner_password=None):
        """Encrypts a PDF with password protection"""
        import PyPDF4
        validated_path = self._validate_path(pdf_path)
        validated_output = self._validate_path(output_path, must_exist=False)
        if owner_password is None:
            owner_password = user_password
        with open(validated_path, 'rb') as file:
            reader = PyPDF4.PdfFileReader(file)
            writer = PyPDF4.PdfFileWriter()
            writer.appendPagesFromReader(reader)
            writer.encrypt(user_password, owner_password)
            with open(validated_output, 'wb') as out:
                writer.write(out)
        return True
    
    def decrypt_pdf(self, pdf_path, output_path, password):
        """Decrypts a password-protected PDF"""
        import PyPDF4
        validated_path = self._validate_path(pdf_path)
        validated_output = self._validate_path(output_path, must_exist=False)
        with open(validated_path, 'rb') as file:
            reader = PyPDF4.PdfFileReader(file)
            if reader.isEncrypted:
                reader.decrypt(password)
            writer = PyPDF4.PdfFileWriter()
            writer.appendPagesFromReader(reader)
            with open(validated_output, 'wb') as out:
                writer.write(out)
        return True
    
    def compress_pdf(self, pdf_path, output_path):
        """Compresses a PDF file by removing unnecessary elements"""
        import PyPDF4
        validated_path = self._validate_path(pdf_path)
        validated_output = self._validate_path(output_path, must_exist=False)
        with open(validated_path, 'rb') as file:
            reader = PyPDF4.PdfFileReader(file)
            writer = PyPDF4.PdfFileWriter()
            for page_num in range(reader.numPages):
                page = reader.getPage(page_num)
                page.compressContentStreams()
                writer.addPage(page)
            with open(validated_output, 'wb') as out:
                writer.write(out)
        original_size = os.path.getsize(validated_path)
        compressed_size = os.path.getsize(validated_output)
        return {
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': round((1 - compressed_size / original_size) * 100, 2)
        }
    
    def extract_images(self, pdf_path, output_dir):
        """Extracts all images from a PDF"""
        import PyPDF4
        validated_path = self._validate_path(pdf_path)
        os.makedirs(output_dir, exist_ok=True)
        extracted_images = []
        with open(validated_path, 'rb') as file:
            reader = PyPDF4.PdfFileReader(file)
            image_count = 0
            for page_num in range(reader.numPages):
                page = reader.getPage(page_num)
                if '/XObject' in page['/Resources']:
                    x_objects = page['/Resources']['/XObject'].getObject()
                    for obj in x_objects:
                        if x_objects[obj]['/Subtype'] == '/Image':
                            image = x_objects[obj]
                            image_data = image.getData()
                            image_ext = 'png' if image.get('/Filter') == '/FlateDecode' else 'jpg'
                            image_path = os.path.join(output_dir, f"image_{image_count}.{image_ext}")
                            with open(image_path, 'wb') as img_file:
                                img_file.write(image_data)
                            extracted_images.append(image_path)
                            image_count += 1
        return extracted_images
    
    def create_blank_pdf(self, output_path, pages=1):
        """Creates a blank PDF with specified number of pages"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        validated_output = self._validate_path(output_path, must_exist=False)
        c = canvas.Canvas(validated_output, pagesize=letter)
        for _ in range(pages):
            c.showPage()
        c.save()
        return True
    
    def text_to_pdf(self, text, output_path, font_size=12):
        """Converts plain text to PDF"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        validated_output = self._validate_path(output_path, must_exist=False)
        c = canvas.Canvas(validated_output, pagesize=letter)
        width, height = letter
        c.setFont("Helvetica", font_size)
        lines = text.split('\n')
        y_position = height - 50
        for line in lines:
            if y_position < 50:
                c.showPage()
                c.setFont("Helvetica", font_size)
                y_position = height - 50
            c.drawString(50, y_position, line[:100])
            y_position -= font_size * 1.2
        c.save()
        return True