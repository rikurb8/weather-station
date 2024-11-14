"""Database models for PDF conversion with enhanced validation and documentation."""

from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from pydantic import HttpUrl, Field, validator
from sqlmodel import Field as SQLField, SQLModel


class PdfMetadata(SQLModel, table=True):
    """Database model for storing PDF conversion metadata.

    This model tracks all PDF conversions, storing essential information about
    the source URL, output location, and conversion timing.

    Attributes:
        id: Unique identifier for the PDF conversion record
        url: The source URL that was converted
        pdf_path: File system path where the PDF was saved
        created_at: Timestamp of when the conversion occurred
        title: Title of the webpage that was converted
    """

    id: Optional[int] = SQLField(default=None, primary_key=True)
    url: str = SQLField(index=True)
    pdf_path: str = SQLField(description="Absolute path to the generated PDF file")
    created_at: datetime = SQLField(
        default_factory=datetime.now, description="Timestamp when the PDF was generated"
    )
    title: str = SQLField(description="Title of the converted webpage", max_length=500)

    @validator("url")
    def validate_url(cls, v: str) -> str:
        """Ensure the URL is properly formatted."""
        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError
            return v
        except Exception:
            raise ValueError("Invalid URL format")

    @validator("pdf_path")
    def validate_path(cls, v: str) -> str:
        """Ensure the path is properly formatted."""
        try:
            path = Path(v)
            if not str(path).endswith(".pdf"):
                raise ValueError("Path must end with .pdf")
            return str(path)
        except Exception as e:
            raise ValueError(f"Invalid path format: {str(e)}")


class PdfOutput(SQLModel):
    """Represents the result of a successful PDF conversion.

    This model provides a standardized way to return conversion results,
    including all relevant metadata about the generated PDF.

    Attributes:
        url: The source URL that was converted (validated as proper HTTP URL)
        pdf_path: Path object pointing to the generated PDF file
        created_at: Timestamp of when the conversion completed
        title: Title of the webpage that was converted
    """

    url: HttpUrl = Field(description="Source URL that was converted to PDF")
    pdf_path: Path = Field(description="Path to the generated PDF file")
    created_at: datetime = Field(
        default_factory=datetime.now, description="Timestamp when the PDF was generated"
    )
    title: str = Field(description="Title of the converted webpage", max_length=500)

    @validator("pdf_path")
    def validate_pdf_path(cls, v: Path) -> Path:
        """Ensure the path is a PDF file."""
        if not str(v).endswith(".pdf"):
            raise ValueError("Path must end with .pdf")
        return v

    @validator("title")
    def validate_title(cls, v: str) -> str:
        """Ensure the title is not empty and properly formatted."""
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        return v
