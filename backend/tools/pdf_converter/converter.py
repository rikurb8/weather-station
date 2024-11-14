"""URL to PDF conversion functionality with enhanced error handling and logging."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from urllib.parse import urlparse

from playwright.async_api import (
    async_playwright,
    Browser,
    Page,
    Error as PlaywrightError,
)
from slugify import slugify
from sqlmodel import Session, create_engine, select

from .models import PdfMetadata, PdfOutput

# Configure logging
logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """Custom exception for conversion-related errors."""

    pass


class UrlToPdfConverter:
    """Handles conversion of URLs to PDF files with proper organization and metadata tracking.

    This class provides a robust interface for converting web pages to PDFs while
    maintaining proper file organization and metadata tracking. It includes features
    like automatic file organization by date, metadata storage in SQLite, and
    optimized PDF generation settings.

    Attributes:
        output_dir: Path object pointing to the base directory for PDF storage
        _engine: SQLAlchemy engine for database operations
    """

    def __init__(
        self,
        output_dir: str = "pdfs",
        database_url: Optional[str] = None,
        page_timeout: int = 30000,
    ) -> None:
        """Initialize the converter with customizable settings.

        Args:
            output_dir: Base directory for PDF storage
            database_url: Optional database URL (defaults to SQLite)
            page_timeout: Maximum time in milliseconds to wait for page load

        Raises:
            ValueError: If output_dir is empty or invalid
            SQLAlchemyError: If database connection fails
        """
        if not output_dir:
            raise ValueError("Output directory cannot be empty")

        self.output_dir = Path(output_dir)
        self.page_timeout = page_timeout

        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Initialized PDF storage directory: {self.output_dir}")
        except Exception as e:
            raise ValueError(f"Failed to create output directory: {str(e)}")

        # Initialize database
        try:
            self._engine = create_engine(
                database_url or "sqlite:///pdfs.db",
                connect_args={"check_same_thread": False},
            )
            PdfMetadata.metadata.create_all(self._engine)
            logger.info("Database initialized successfully")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize database: {str(e)}")

    def _validate_url(self, url: str) -> None:
        """Validate URL format.

        Args:
            url: URL string to validate

        Raises:
            ValueError: If URL is invalid
        """
        try:
            result = urlparse(url)
            if not all([result.scheme, result.netloc]):
                raise ValueError
        except Exception:
            raise ValueError(f"Invalid URL format: {url}")

    def _generate_pdf_path(self, url: str, title: Optional[str] = None) -> Path:
        """Generate an appropriate PDF file path with date-based organization.

        Args:
            url: The source URL
            title: Optional page title to use in filename

        Returns:
            Path object for the PDF file
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base_name = title if title else url.split("//")[-1].split("/")[0]
        safe_name = slugify(base_name)
        filename = f"{safe_name}-{timestamp}.pdf"

        # Organize files by year/month
        date_dir = self.output_dir / datetime.now().strftime("%Y/%m")
        date_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Generated PDF path: {date_dir / filename}")

        return date_dir / filename

    async def _setup_browser(self) -> Browser:
        """Set up and configure the browser for PDF generation.

        Returns:
            Configured browser instance

        Raises:
            PlaywrightError: If browser setup fails
        """
        try:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch()
            logger.debug("Browser launched successfully")
            return browser
        except Exception as e:
            raise ConversionError(f"Failed to launch browser: {str(e)}")

    async def convert(self, url: str) -> PdfOutput:
        """Convert a URL to PDF and store metadata.

        This method handles the entire conversion process, including:
        - URL validation
        - Browser setup
        - Page rendering
        - PDF generation
        - Metadata storage

        Args:
            url: The URL to convert to PDF

        Returns:
            PdfOutput object containing the result details

        Raises:
            ConversionError: If any part of the conversion process fails
            ValueError: If URL is invalid
        """
        self._validate_url(url)
        logger.info(f"Starting conversion for URL: {url}")

        browser = None
        try:
            browser = await self._setup_browser()

            # Create context with desktop settings
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                device_scale_factor=1,
            )

            page = await context.new_page()
            await page.set_extra_http_headers(
                {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "DNT": "1",
                    "Upgrade-Insecure-Requests": "1",
                }
            )

            try:
                await page.goto(
                    url, wait_until="networkidle", timeout=self.page_timeout
                )
            except PlaywrightError as e:
                raise ConversionError(f"Failed to load page: {str(e)}")

            # Force desktop mode and wait for layout
            await page.emulate_media(media="screen")
            await page.wait_for_timeout(2000)

            title = await page.title() or urlparse(url).netloc
            pdf_path = self._generate_pdf_path(url, title)

            # Generate PDF with optimized settings
            await page.pdf(
                path=str(pdf_path),
                format="A3",
                landscape=True,
                print_background=True,
                margin={
                    "top": "0.5cm",
                    "right": "0.5cm",
                    "bottom": "0.5cm",
                    "left": "0.5cm",
                },
                scale=0.9,
                prefer_css_page_size=True,
                width="1920px",
            )

            logger.info(f"PDF generated successfully: {pdf_path}")

            # Create output object
            output = PdfOutput(
                url=url,
                pdf_path=pdf_path,
                created_at=datetime.now(),
                title=title,
            )

            # Store metadata
            self._store_metadata(output)
            return output

        except Exception as e:
            logger.error(f"Conversion failed: {str(e)}")
            raise ConversionError(f"PDF conversion failed: {str(e)}")

        finally:
            if browser:
                await browser.close()
                logger.debug("Browser closed")

    def _store_metadata(self, output: PdfOutput) -> None:
        """Store PDF metadata in the database.

        Args:
            output: PdfOutput object containing conversion results

        Raises:
            ConversionError: If metadata storage fails
        """
        try:
            metadata = PdfMetadata(
                url=str(output.url),
                pdf_path=str(output.pdf_path),
                created_at=output.created_at,
                title=output.title,
            )

            with Session(self._engine) as session:
                session.add(metadata)
                session.commit()
                logger.debug(f"Metadata stored for: {output.url}")

        except Exception as e:
            logger.error(f"Failed to store metadata: {str(e)}")
            raise ConversionError(f"Failed to store metadata: {str(e)}")

    def get_pdf_metadata(self, url: Optional[str] = None) -> List[PdfMetadata]:
        """Retrieve PDF metadata from the database.

        Args:
            url: Optional URL to filter by

        Returns:
            List of PdfMetadata objects matching the criteria

        Raises:
            ConversionError: If metadata retrieval fails
        """
        try:
            with Session(self._engine) as session:
                if url:
                    statement = select(PdfMetadata).where(PdfMetadata.url.contains(url))
                else:
                    statement = select(PdfMetadata)
                return session.exec(statement).all()
        except Exception as e:
            logger.error(f"Failed to retrieve metadata: {str(e)}")
            raise ConversionError(f"Failed to retrieve metadata: {str(e)}")
