# PDF Converter Module

A robust Python module for converting web pages to PDFs with metadata storage and organization capabilities. The module uses Playwright for high-quality web page rendering and SQLModel for metadata management.

## Features

- Convert web pages to PDF with desktop-optimized layout
- Automatic file organization by year/month
- Metadata storage in SQLite database
- Configurable output directory and timeouts
- Proper error handling and logging
- Type hints and input validation
- Async/await support for efficient processing
- Comprehensive test coverage

## Installation

This module requires Python 3.8+ and the following dependencies:

```bash
# Using uv (recommended)
uv pip install playwright sqlmodel pydantic slugify

# Install Playwright browsers
playwright install chromium
```

## Usage

### Basic Example

```python
import asyncio
from pdf_converter import UrlToPdfConverter

async def main():
    # Initialize converter with default settings
    converter = UrlToPdfConverter()
    
    try:
        # Convert a URL to PDF
        result = await converter.convert("https://example.com")
        print(f"PDF saved to: {result.pdf_path}")
        print(f"Page title: {result.title}")
    except Exception as e:
        print(f"Conversion failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Configuration

```python
from pdf_converter import UrlToPdfConverter

# Custom output directory and database URL
converter = UrlToPdfConverter(
    output_dir="custom_pdfs",
    database_url="sqlite:///custom.db",
    page_timeout=30000  # 30 seconds timeout
)
```

### Error Handling and Logging

```python
import logging
from pdf_converter import UrlToPdfConverter, ConversionError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def convert_with_error_handling(url: str):
    converter = UrlToPdfConverter()
    
    try:
        result = await converter.convert(url)
        logger.info(f"PDF saved to: {result.pdf_path}")
        return result
    except ConversionError as e:
        logger.error(f"Conversion failed: {str(e)}")
        raise
```

### Metadata Management

```python
# Retrieve all PDF metadata
metadata_list = converter.get_pdf_metadata()

# Filter by URL
filtered_list = converter.get_pdf_metadata(url="example.com")

# Access metadata fields
for metadata in metadata_list:
    print(f"URL: {metadata.url}")
    print(f"PDF Path: {metadata.pdf_path}")
    print(f"Created: {metadata.created_at}")
    print(f"Title: {metadata.title}")
```

## API Reference

### `UrlToPdfConverter`

Main class for handling URL to PDF conversions.

#### Constructor Parameters

- `output_dir` (str, optional): Base directory for PDF storage. Defaults to "pdfs"
- `database_url` (str, optional): SQLite database URL. Defaults to "sqlite:///pdfs.db"
- `page_timeout` (int, optional): Maximum time in milliseconds to wait for page load. Defaults to 30000

#### Methods

- `async convert(url: str) -> PdfOutput`: Convert a URL to PDF
  - Raises `ConversionError` if conversion fails
  - Raises `ValueError` if URL is invalid
- `get_pdf_metadata(url: Optional[str] = None) -> List[PdfMetadata]`: Retrieve PDF metadata

### Data Models

#### `PdfOutput`

Represents the result of a PDF conversion.

- `url` (HttpUrl): Source URL
- `pdf_path` (Path): Path to generated PDF file
- `created_at` (datetime): Creation timestamp
- `title` (str): Page title

#### `PdfMetadata`

Database model for storing PDF metadata.

- `id` (int): Primary key
- `url` (str): Source URL
- `pdf_path` (str): Path to PDF file
- `created_at` (datetime): Creation timestamp
- `title` (str): Page title

## PDF Generation Details

The converter is optimized for desktop layouts with the following settings:

- A3 format in landscape orientation
- Desktop viewport (1920x1080)
- Background rendering enabled
- Custom margins (0.5cm)
- Scale optimization (0.9)
- CSS page size preferences
- Desktop user agent and headers

## File Organization

PDFs are automatically organized in the following structure:
```
output_dir/
└── YYYY/
    └── MM/
        └── {slugified-title}-{timestamp}.pdf
```

## Error Handling

The module provides comprehensive error handling:

- `ConversionError`: Base exception for conversion-related errors
- URL validation with detailed error messages
- Proper cleanup of browser resources
- Detailed logging of all operations
- Database operation error handling

## Logging

The module uses Python's built-in logging system:

- Configurable log levels
- Detailed operation logging
- Error tracing
- Resource management logging

## Testing

The module includes comprehensive tests:

```bash
# Run tests with pytest
pytest tests/test_url_to_pdf.py
```

## Database

The module uses SQLite by default to store metadata about generated PDFs. The database is automatically created and managed using SQLModel, with proper connection handling and error management.

## Contributing

Contributions are welcome! Please ensure:

1. Code includes type hints
2. Tests are added for new features
3. Documentation is updated
4. Error handling follows established patterns
5. Logging is implemented for new operations

## License

MIT License - feel free to use in your own projects.
