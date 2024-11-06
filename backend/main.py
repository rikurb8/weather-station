import asyncio
from backend.url_to_pdf import UrlToPdfConverter


async def main():
    # Create converter instance
    converter = UrlToPdfConverter(output_dir="pdfs")

    # Convert URL to PDF
    result = await converter.convert("https://rwc-finland.fmi.fi/")

    # Access result properties
    print(f"PDF saved to: {result.pdf_path}")
    print(f"Page title: {result.title}")
    print(f"Created at: {result.created_at}")
    print(f"Source URL: {result.url}")


if __name__ == "__main__":
    asyncio.run(main())
