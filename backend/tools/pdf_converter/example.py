"""Example usage of the PDF converter module with error handling and logging."""

import asyncio
import logging
from pathlib import Path

from .converter import UrlToPdfConverter, ConversionError

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_desktop_layout(converter: UrlToPdfConverter) -> None:
    """Test desktop layout conversion with proper error handling.

    Args:
        converter: Configured UrlToPdfConverter instance

    This example demonstrates:
    - Proper error handling
    - Logging of conversion process
    - Metadata retrieval
    """
    url = "https://rwc-finland.fmi.fi/"

    try:
        logger.info(f"Converting {url} to PDF...")
        result = await converter.convert(url)

        logger.info("Conversion successful:")
        logger.info(f"- PDF saved to: {result.pdf_path}")
        logger.info(f"- Page title: {result.title}")
        logger.info(f"- Created at: {result.created_at}")

        # Demonstrate metadata retrieval
        metadata = converter.get_pdf_metadata(url)
        logger.info(f"Found {len(metadata)} conversion records for this URL")

    except ConversionError as e:
        logger.error(f"Conversion error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")


async def test_error_handling(converter: UrlToPdfConverter) -> None:
    """Demonstrate error handling with invalid inputs.

    Args:
        converter: Configured UrlToPdfConverter instance
    """
    invalid_urls = [
        "not-a-url",
        "ftp://invalid-protocol.com",
        "https://nonexistent-domain-123456789.com",
    ]

    for url in invalid_urls:
        try:
            logger.info(f"Testing invalid URL: {url}")
            await converter.convert(url)
        except ConversionError as e:
            logger.warning(f"Expected error occurred: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")


async def main() -> None:
    """Run example conversions with proper setup and error handling."""
    # Use a custom output directory and enable debug logging for the converter
    converter = UrlToPdfConverter(
        output_dir="example_pdfs", page_timeout=15000  # 15 seconds timeout
    )

    try:
        logger.info("Starting URL to PDF conversion examples...")

        # Test successful conversion
        await test_desktop_layout(converter)

        # Test error handling
        await test_error_handling(converter)

        logger.info("Examples completed successfully!")

    except KeyboardInterrupt:
        logger.info("Examples interrupted by user")
    except Exception as e:
        logger.error(f"Example execution failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
