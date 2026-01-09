import os
import shutil
import whisper
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

class Scribe:
    def __init__(self, upload_dir="uploads", data_dir="codex/data"):
        self.upload_dir = upload_dir
        self.data_dir = data_dir
        
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(data_dir, exist_ok=True)
        
        # Lazy load heavy models
        self.whisper_model = None

    def ingest_media(self, file_path):
        """
        Main entry point for converting Audio/Image/PDF to Text.
        """
        if not os.path.exists(file_path):
            return f"[Scribe] File not found: {file_path}"
            
        ext = os.path.splitext(file_path)[1].lower()
        filename = os.path.basename(file_path)
        
        result_text = ""
        
        try:
            if ext in ['.mp3', '.wav', '.m4a']:
                result_text = self._transcribe_audio(file_path)
            elif ext in ['.png', '.jpg', '.jpeg']:
                result_text = self._ocr_image(file_path)
            elif ext == '.pdf':
                result_text = self._ocr_pdf(file_path)
            else:
                return "[Scribe] Unsupported file format."
                
            # Save the "recreated" document
            output_name = f"{os.path.splitext(filename)[0]}_transcript.txt"
            output_path = os.path.join(self.data_dir, output_name)
            
            with open(output_path, "w") as f:
                f.write(f"--- Source: {filename} ---\n\n")
                f.write(result_text)
                
            return f"[Scribe] Successfully converted {filename}. Saved to {output_path}"
            
        except Exception as e:
            return f"[Scribe] Transformation failed: {e}"

    def _transcribe_audio(self, path):
        if not self.whisper_model:
            print("[Scribe] Loading Whisper Model (this may take a moment)...")
            self.whisper_model = whisper.load_model("base")
            
        print(f"[Scribe] Listening to {os.path.basename(path)}...")
        result = self.whisper_model.transcribe(path)
        return result["text"]

    def _ocr_image(self, path):
        print(f"[Scribe] Reading {os.path.basename(path)}...")
        text = pytesseract.image_to_string(Image.open(path))
        return text

    def _ocr_pdf(self, path):
        print(f"[Scribe] Scanning PDF {os.path.basename(path)}...")
        # 1. Try text extraction first (faster)
        import fitz
        text = ""
        try:
            with fitz.open(path) as doc:
                for page in doc:
                    text += page.get_text()
        except:
            pass
            
        if len(text.strip()) > 50:
            return text
            
        # 2. Fallback to OCR (if scanned pdf)
        print("[Scribe] PDF seems like an image. Applying OCR...")
        images = convert_from_path(path)
        ocr_text = ""
        for i, image in enumerate(images):
            ocr_text += f"\n--- Page {i+1} ---\n"
            ocr_text += pytesseract.image_to_string(image)
            
        return ocr_text
