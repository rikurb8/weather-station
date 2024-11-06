"""Tests for the PDF converter module."""

from datetime import datetime
from pathlib import Path
import os

import pytest
from pydantic import HttpUrl
from sqlmodel import Session, SQLModel, create_engine

from backend.pdf_converter import UrlToPdfConverter, PdfOutput, PdfMetadata


@pytest.fixture(name="test_db")
def test_db_fixture():
    """Create a test database."""
    # Use an in-memory SQLite database for testing
    database_url = "sqlite:///test.db"
    if os.path.exists("test.db"):
        os.remove("test.db")
    engine = create_engine(database_url)
    SQLModel.metadata.create_all(engine)
    yield database_url
    # Cleanup
    SQLModel.metadata.drop_all(engine)
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture
def converter(tmp_path, test_db):
    """Create a converter instance that uses a temporary directory."""
    return UrlToPdfConverter(output_dir=str(tmp_path), database_url=test_db)


def test_pdf_output_model():
    """Test that PdfOutput model validates correctly."""
    now = datetime.now()
    output = PdfOutput(
        url="https://example.com",
        pdf_path=Path("/tmp/test.pdf"),
        created_at=now,
        title="Example Domain",
    )

    # Verify the URL was converted to HttpUrl type
    assert str(output.url).rstrip("/") == "https://example.com"
    assert isinstance(output.pdf_path, Path)
    assert output.created_at == now
    assert output.title == "Example Domain"


def test_pdf_metadata_model(test_db):
    """Test that PdfMetadata model works correctly with database."""
    engine = create_engine(test_db)
    now = datetime.now()
    metadata = PdfMetadata(
        url="https://example.com",
        pdf_path="/tmp/test.pdf",
        created_at=now,
        title="Example Domain",
    )

    with Session(engine) as session:
        session.add(metadata)
        session.commit()
        session.refresh(metadata)

        # Verify the metadata was stored correctly
        assert metadata.id is not None
        assert metadata.url == "https://example.com"
        assert metadata.pdf_path == "/tmp/test.pdf"
        assert metadata.created_at == now
        assert metadata.title == "Example Domain"


def test_generate_pdf_path(converter):
    """Test PDF path generation with proper structure."""
    url = "https://example.com"
    title = "Example Page"

    path = converter._generate_pdf_path(url, title)

    assert path.parent.match(
        "*/[0-9][0-9][0-9][0-9]/[0-9][0-9]"
    )  # Year/month structure
    assert path.name.startswith("example-page-")  # Slugified title
    assert path.suffix == ".pdf"


@pytest.mark.asyncio
async def test_convert_url(converter):
    """Test actual URL conversion to PDF."""
    url = "https://example.com"

    result = await converter.convert(url)

    assert isinstance(result, PdfOutput)
    assert str(result.url).rstrip("/") == url
    assert result.pdf_path.exists()
    assert result.pdf_path.stat().st_size > 0  # PDF should not be empty
    assert "Example Domain" in result.title  # Known title for example.com

    # Verify metadata was stored in database
    metadata_list = converter.get_pdf_metadata("https://example.com")
    assert len(metadata_list) > 0
    metadata = metadata_list[0]
    assert str(result.url) in metadata.url
    assert metadata.title == result.title
    assert metadata.pdf_path == str(result.pdf_path)


@pytest.mark.asyncio
async def test_get_pdf_metadata(converter):
    """Test retrieving PDF metadata from database."""
    # Convert multiple URLs (properly separated)
    urls = ["https://example.com", "https://example.org"]

    for url in urls:
        await converter.convert(url)

    # Test retrieving all metadata
    all_metadata = converter.get_pdf_metadata()
    assert len(all_metadata) == len(urls)

    # Test retrieving metadata for specific URL
    url_metadata = converter.get_pdf_metadata(urls[0])
    assert len(url_metadata) == 1
    assert urls[0] in url_metadata[0].url

    # Test retrieving metadata for non-existent URL
    empty_metadata = converter.get_pdf_metadata("https://nonexistent.com")
    assert len(empty_metadata) == 0
