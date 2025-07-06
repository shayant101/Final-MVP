"""
Image Processing Service
Handles image optimization, compression, and format conversion
"""
import os
import io
import logging
from typing import Tuple, Optional, Dict, Any
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
import pillow_heif

logger = logging.getLogger(__name__)

# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()

class ImageProcessingService:
    """
    Service for processing and optimizing images for web use
    """
    
    # Supported formats
    SUPPORTED_INPUT_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.heic', '.heif'}
    SUPPORTED_OUTPUT_FORMATS = {'JPEG', 'PNG', 'WEBP'}
    
    # Quality settings
    QUALITY_SETTINGS = {
        'high': 95,
        'medium': 85,
        'low': 70,
        'thumbnail': 60
    }
    
    # Image type configurations
    IMAGE_TYPE_CONFIGS = {
        'hero': {
            'max_width': 1920,
            'max_height': 1080,
            'quality': 'high',
            'format': 'JPEG',
            'optimize': True
        },
        'about': {
            'max_width': 800,
            'max_height': 600,
            'quality': 'medium',
            'format': 'JPEG',
            'optimize': True
        },
        'menu_item': {
            'max_width': 600,
            'max_height': 450,
            'quality': 'medium',
            'format': 'JPEG',
            'optimize': True
        },
        'logo': {
            'max_width': 400,
            'max_height': 400,
            'quality': 'high',
            'format': 'PNG',
            'optimize': True,
            'preserve_transparency': True
        },
        'gallery': {
            'max_width': 1200,
            'max_height': 800,
            'quality': 'medium',
            'format': 'JPEG',
            'optimize': True
        },
        'thumbnail': {
            'max_width': 300,
            'max_height': 300,
            'quality': 'thumbnail',
            'format': 'JPEG',
            'optimize': True
        }
    }
    
    @classmethod
    def validate_image(cls, file_content: bytes, max_size: int = 10 * 1024 * 1024) -> Dict[str, Any]:
        """
        Validate image file and return metadata
        """
        try:
            # Check file size
            if len(file_content) > max_size:
                raise ValueError(f"File too large. Maximum size: {max_size // (1024*1024)}MB")
            
            # Try to open image
            image = Image.open(io.BytesIO(file_content))
            
            # Get image info
            width, height = image.size
            format_name = image.format
            mode = image.mode
            
            # Check if image is valid
            if width < 10 or height < 10:
                raise ValueError("Image too small. Minimum dimensions: 10x10px")
            
            if width > 5000 or height > 5000:
                raise ValueError("Image too large. Maximum dimensions: 5000x5000px")
            
            return {
                'valid': True,
                'width': width,
                'height': height,
                'format': format_name,
                'mode': mode,
                'size': len(file_content),
                'aspect_ratio': width / height
            }
            
        except Exception as e:
            logger.error(f"Image validation failed: {str(e)}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    @classmethod
    def optimize_image(
        cls, 
        file_content: bytes, 
        image_type: str = 'general',
        custom_config: Optional[Dict[str, Any]] = None
    ) -> Tuple[bytes, Dict[str, Any]]:
        """
        Optimize image based on type and configuration
        """
        try:
            # Get configuration
            config = cls.IMAGE_TYPE_CONFIGS.get(image_type, cls.IMAGE_TYPE_CONFIGS['gallery'])
            if custom_config:
                config.update(custom_config)
            
            # Open image
            image = Image.open(io.BytesIO(file_content))
            
            # Auto-rotate based on EXIF data
            image = ImageOps.exif_transpose(image)
            
            # Get original dimensions
            original_width, original_height = image.size
            
            # Resize if necessary
            max_width = config.get('max_width', 1200)
            max_height = config.get('max_height', 800)
            
            if original_width > max_width or original_height > max_height:
                # Calculate new dimensions maintaining aspect ratio
                ratio = min(max_width / original_width, max_height / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
                
                # Use high-quality resampling
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Handle transparency and format conversion
            output_format = config.get('format', 'JPEG')
            preserve_transparency = config.get('preserve_transparency', False)
            
            if output_format == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
                if not preserve_transparency:
                    # Create white background for JPEG
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    if image.mode in ('RGBA', 'LA'):
                        background.paste(image, mask=image.split()[-1])
                    image = background
                else:
                    # Convert to PNG to preserve transparency
                    output_format = 'PNG'
            
            # Apply image enhancements if specified
            if config.get('enhance', False):
                image = cls._enhance_image(image, config.get('enhancement_settings', {}))
            
            # Save optimized image
            output_buffer = io.BytesIO()
            quality_setting = config.get('quality', 'medium')
            quality = cls.QUALITY_SETTINGS.get(quality_setting, 85)
            
            save_kwargs = {
                'format': output_format,
                'optimize': config.get('optimize', True)
            }
            
            if output_format == 'JPEG':
                save_kwargs['quality'] = quality
                save_kwargs['progressive'] = True
            elif output_format == 'PNG':
                save_kwargs['optimize'] = True
            elif output_format == 'WEBP':
                save_kwargs['quality'] = quality
                save_kwargs['method'] = 6  # Best compression
            
            image.save(output_buffer, **save_kwargs)
            optimized_content = output_buffer.getvalue()
            
            # Calculate compression ratio
            original_size = len(file_content)
            optimized_size = len(optimized_content)
            compression_ratio = ((original_size - optimized_size) / original_size) * 100
            
            metadata = {
                'original_size': original_size,
                'optimized_size': optimized_size,
                'compression_ratio': round(compression_ratio, 1),
                'original_dimensions': (original_width, original_height),
                'final_dimensions': image.size,
                'format': output_format,
                'quality': quality
            }
            
            logger.info(f"Image optimized: {compression_ratio:.1f}% compression, {original_size} -> {optimized_size} bytes")
            
            return optimized_content, metadata
            
        except Exception as e:
            logger.error(f"Image optimization failed: {str(e)}")
            raise ValueError(f"Image optimization failed: {str(e)}")
    
    @classmethod
    def create_thumbnail(
        cls, 
        file_content: bytes, 
        size: Tuple[int, int] = (300, 300),
        crop: bool = True
    ) -> bytes:
        """
        Create thumbnail from image
        """
        try:
            image = Image.open(io.BytesIO(file_content))
            
            # Auto-rotate based on EXIF data
            image = ImageOps.exif_transpose(image)
            
            if crop:
                # Create square thumbnail with cropping
                image = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
            else:
                # Create thumbnail maintaining aspect ratio
                image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                if image.mode in ('RGBA', 'LA'):
                    background.paste(image, mask=image.split()[-1])
                image = background
            
            # Save thumbnail
            output_buffer = io.BytesIO()
            image.save(output_buffer, 'JPEG', quality=80, optimize=True)
            
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Thumbnail creation failed: {str(e)}")
            raise ValueError(f"Thumbnail creation failed: {str(e)}")
    
    @classmethod
    def _enhance_image(cls, image: Image.Image, settings: Dict[str, Any]) -> Image.Image:
        """
        Apply image enhancements
        """
        try:
            # Brightness adjustment
            if 'brightness' in settings:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(settings['brightness'])
            
            # Contrast adjustment
            if 'contrast' in settings:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(settings['contrast'])
            
            # Color saturation adjustment
            if 'saturation' in settings:
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(settings['saturation'])
            
            # Sharpness adjustment
            if 'sharpness' in settings:
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(settings['sharpness'])
            
            # Apply filters
            if 'blur' in settings and settings['blur'] > 0:
                image = image.filter(ImageFilter.GaussianBlur(radius=settings['blur']))
            
            if 'sharpen' in settings and settings['sharpen']:
                image = image.filter(ImageFilter.SHARPEN)
            
            return image
            
        except Exception as e:
            logger.error(f"Image enhancement failed: {str(e)}")
            return image  # Return original image if enhancement fails
    
    @classmethod
    def convert_format(
        cls, 
        file_content: bytes, 
        target_format: str = 'JPEG',
        quality: int = 85
    ) -> bytes:
        """
        Convert image to different format
        """
        try:
            image = Image.open(io.BytesIO(file_content))
            
            # Auto-rotate based on EXIF data
            image = ImageOps.exif_transpose(image)
            
            # Handle format conversion
            if target_format.upper() == 'JPEG' and image.mode in ('RGBA', 'LA', 'P'):
                # Create white background for JPEG
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                if image.mode in ('RGBA', 'LA'):
                    background.paste(image, mask=image.split()[-1])
                image = background
            
            # Save in target format
            output_buffer = io.BytesIO()
            
            if target_format.upper() == 'JPEG':
                image.save(output_buffer, 'JPEG', quality=quality, optimize=True)
            elif target_format.upper() == 'PNG':
                image.save(output_buffer, 'PNG', optimize=True)
            elif target_format.upper() == 'WEBP':
                image.save(output_buffer, 'WEBP', quality=quality, method=6)
            else:
                raise ValueError(f"Unsupported target format: {target_format}")
            
            return output_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Format conversion failed: {str(e)}")
            raise ValueError(f"Format conversion failed: {str(e)}")
    
    @classmethod
    def get_image_info(cls, file_content: bytes) -> Dict[str, Any]:
        """
        Get detailed image information
        """
        try:
            image = Image.open(io.BytesIO(file_content))
            
            # Basic info
            info = {
                'width': image.width,
                'height': image.height,
                'format': image.format,
                'mode': image.mode,
                'size': len(file_content),
                'aspect_ratio': image.width / image.height
            }
            
            # EXIF data if available
            if hasattr(image, '_getexif') and image._getexif():
                info['has_exif'] = True
                exif = image._getexif()
                if exif:
                    # Extract useful EXIF data
                    info['exif'] = {
                        'orientation': exif.get(274, 1),
                        'camera_make': exif.get(271, ''),
                        'camera_model': exif.get(272, ''),
                        'datetime': exif.get(306, ''),
                        'software': exif.get(305, '')
                    }
            else:
                info['has_exif'] = False
            
            # Color analysis
            if image.mode == 'RGB':
                # Get dominant colors (simplified)
                colors = image.getcolors(maxcolors=256*256*256)
                if colors:
                    # Sort by frequency and get top colors
                    colors.sort(key=lambda x: x[0], reverse=True)
                    dominant_colors = [color[1] for color in colors[:5]]
                    info['dominant_colors'] = dominant_colors
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get image info: {str(e)}")
            return {'error': str(e)}

# Create service instance
image_processing_service = ImageProcessingService()