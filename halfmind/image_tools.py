import os
import hashlib
from pathlib import Path


class ImageTools:
    """Tools for image manipulation and processing"""
    
    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    def __init__(self, max_dimension=4096):
        self.max_dimension = max_dimension
    
    def _validate_path(self, path):
        """Validates file path for security"""
        resolved = Path(path).resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if resolved.suffix.lower() not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Invalid file extension: {resolved.suffix}")
        if resolved.stat().st_size > self.MAX_FILE_SIZE:
            raise ValueError("File size exceeds maximum allowed")
        return str(resolved)
    
    def get_image_info(self, image_path):
        """Returns detailed information about an image file"""
        from PIL import Image
        validated_path = self._validate_path(image_path)
        with Image.open(validated_path) as img:
            return {
                'format': img.format,
                'mode': img.mode,
                'width': img.width,
                'height': img.height,
                'size_bytes': os.path.getsize(validated_path),
                'file_hash': self._compute_hash(validated_path)
            }
    
    def _compute_hash(self, file_path):
        """Computes SHA256 hash of a file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def resize_image(self, input_path, output_path, width=None, height=None, maintain_aspect=True):
        """Resizes an image to specified dimensions"""
        from PIL import Image
        validated_input = self._validate_path(input_path)
        with Image.open(validated_input) as img:
            if width is None and height is None:
                raise ValueError("Must specify width or height")
            if maintain_aspect:
                if width and height:
                    img.thumbnail((width, height), Image.Resampling.LANCZOS)
                elif width:
                    ratio = width / img.width
                    height = int(img.height * ratio)
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                else:
                    ratio = height / img.height
                    width = int(img.width * ratio)
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
            else:
                w = width or img.width
                h = height or img.height
                img = img.resize((w, h), Image.Resampling.LANCZOS)
            img.save(output_path)
        return True
    
    def convert_format(self, input_path, output_path):
        """Converts image between formats based on output extension"""
        from PIL import Image
        validated_input = self._validate_path(input_path)
        output_ext = Path(output_path).suffix.lower()
        if output_ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported output format: {output_ext}")
        with Image.open(validated_input) as img:
            if output_ext in {'.jpg', '.jpeg'} and img.mode in {'RGBA', 'P'}:
                img = img.convert('RGB')
            img.save(output_path)
        return True
    
    def create_thumbnail(self, input_path, output_path, size=(128, 128)):
        """Creates a thumbnail of specified size"""
        from PIL import Image
        validated_input = self._validate_path(input_path)
        with Image.open(validated_input) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(output_path)
        return True
    
    def rotate_image(self, input_path, output_path, degrees):
        """Rotates an image by specified degrees"""
        from PIL import Image
        validated_input = self._validate_path(input_path)
        with Image.open(validated_input) as img:
            rotated = img.rotate(-degrees, expand=True, resample=Image.Resampling.BICUBIC)
            rotated.save(output_path)
        return True
    
    def flip_image(self, input_path, output_path, direction='horizontal'):
        """Flips an image horizontally or vertically"""
        from PIL import Image
        validated_input = self._validate_path(input_path)
        with Image.open(validated_input) as img:
            if direction == 'horizontal':
                flipped = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif direction == 'vertical':
                flipped = img.transpose(Image.FLIP_TOP_BOTTOM)
            else:
                raise ValueError("Direction must be 'horizontal' or 'vertical'")
            flipped.save(output_path)
        return True
    
    def apply_grayscale(self, input_path, output_path):
        """Converts an image to grayscale"""
        from PIL import Image
        validated_input = self._validate_path(input_path)
        with Image.open(validated_input) as img:
            gray = img.convert('L')
            gray.save(output_path)
        return True
    
    def adjust_brightness(self, input_path, output_path, factor):
        """Adjusts image brightness (factor > 1 brightens, < 1 darkens)"""
        from PIL import Image, ImageEnhance
        validated_input = self._validate_path(input_path)
        with Image.open(validated_input) as img:
            enhancer = ImageEnhance.Brightness(img)
            enhanced = enhancer.enhance(factor)
            enhanced.save(output_path)
        return True
    
    def adjust_contrast(self, input_path, output_path, factor):
        """Adjusts image contrast"""
        from PIL import Image, ImageEnhance
        validated_input = self._validate_path(input_path)
        with Image.open(validated_input) as img:
            enhancer = ImageEnhance.Contrast(img)
            enhanced = enhancer.enhance(factor)
            enhanced.save(output_path)
        return True
    
    def blur_image(self, input_path, output_path, radius=2):
        """Applies Gaussian blur to an image"""
        from PIL import Image, ImageFilter
        validated_input = self._validate_path(input_path)
        with Image.open(validated_input) as img:
            blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
            blurred.save(output_path)
        return True
    
    def sharpen_image(self, input_path, output_path):
        """Sharpens an image"""
        from PIL import Image, ImageFilter
        validated_input = self._validate_path(input_path)
        with Image.open(validated_input) as img:
            sharpened = img.filter(ImageFilter.SHARPEN)
            sharpened.save(output_path)
        return True
    
    def add_watermark(self, input_path, output_path, watermark_text, position='bottom-right', opacity=0.5):
        """Adds text watermark to an image"""
        from PIL import Image, ImageDraw, ImageFont
        validated_input = self._validate_path(input_path)
        with Image.open(validated_input) as img:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except IOError:
                font = ImageFont.load_default()
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            if position == 'bottom-right':
                x = img.width - text_width - 20
                y = img.height - text_height - 20
            elif position == 'top-left':
                x, y = 20, 20
            elif position == 'center':
                x = (img.width - text_width) // 2
                y = (img.height - text_height) // 2
            else:
                x, y = 20, 20
            alpha = int(255 * opacity)
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, alpha))
            watermarked = Image.alpha_composite(img, txt_layer)
            watermarked.save(output_path)
        return True
    
    def crop_image(self, input_path, output_path, left, top, right, bottom):
        """Crops an image to specified coordinates"""
        from PIL import Image
        validated_input = self._validate_path(input_path)
        with Image.open(validated_input) as img:
            cropped = img.crop((left, top, right, bottom))
            cropped.save(output_path)
        return True
    
    def merge_images(self, image_paths, output_path, direction='horizontal'):
        """Merges multiple images horizontally or vertically"""
        from PIL import Image
        images = []
        total_width = 0
        total_height = 0
        for path in image_paths:
            validated = self._validate_path(path)
            img = Image.open(validated)
            images.append(img)
            if direction == 'horizontal':
                total_width += img.width
                total_height = max(total_height, img.height)
            else:
                total_width = max(total_width, img.width)
                total_height += img.height
        merged = Image.new('RGB', (total_width, total_height), color='white')
        offset = 0
        for img in images:
            if direction == 'horizontal':
                merged.paste(img, (offset, 0))
                offset += img.width
            else:
                merged.paste(img, (0, offset))
                offset += img.height
            img.close()
        merged.save(output_path)
        return True