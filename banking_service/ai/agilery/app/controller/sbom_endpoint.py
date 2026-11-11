"""
Controller for generating and serving the application's SBOM (Software Bill of Materials).
"""

import json
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ai.agilery.app.exception.processing_exception import ProcessingException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/actuator", tags=["SBOM"])


@router.get(
    "/sbom",
    summary="Generate and return the application's SBOM",
    description=(
        "Dynamically generates and returns the CycloneDX SBOM "
        "in JSON format for the application's production dependencies."
    ),
    responses={
        200: {
            "description": "Successful SBOM Generation",
            "content": {"application/vnd.cyclonedx+json": {}},
        },
        500: {"description": "Internal Server Error during SBOM generation"},
    },
)
async def get_sbom():
    """
    Generates and returns the CycloneDX SBOM for the application's production dependencies.

    This endpoint:
    1. Exports production dependencies using Poetry.
    2. Generates a CycloneDX SBOM from the exported requirements.
    3. Returns the generated SBOM as JSON.

    Raises:
        ProcessingException: If any step of the SBOM generation fails.
    """
    logger.info("On-demand SBOM generation requested.")

    if shutil.which("poetry") is None:
        raise ProcessingException(
            "Poetry executable not found. Please install Poetry and ensure it is available in the system PATH."
        )

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            req_path = Path(tmpdir) / "requirements.txt"
            sbom_path = Path(tmpdir) / "sbom.json"

            # Step 1: Export production dependencies using Poetry
            export_cmd = (
                f"poetry export "
                f"--only main "
                f"--without-hashes "
                f"-f requirements.txt "
                f'-o "{req_path}"'
            )

            subprocess.run(
                export_cmd,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info("Successfully exported production dependencies.")

            # Step 2: Generate CycloneDX SBOM
            sbom_cmd = (
                f"poetry run cyclonedx-py "
                f'requirements "{req_path}" '
                f"--output-format JSON "
                f'-o "{sbom_path}"'
            )

            subprocess.run(
                sbom_cmd,
                shell=True,
                check=True,
                capture_output=True,
                text=True,
            )

            logger.info("Successfully generated SBOM.")

            # Step 3: Read generated SBOM
            with open(sbom_path, "r", encoding="utf-8") as file:
                sbom_data = json.load(file)

            return JSONResponse(
                content=sbom_data,
                media_type="application/vnd.cyclonedx+json",
            )

    except subprocess.CalledProcessError as e:
        error_message = (e.stderr or e.stdout or "Unknown error").strip()

        logger.error("Failed to generate SBOM: %s", error_message)

        raise ProcessingException(f"Failed to generate SBOM: {error_message}") from e

    except Exception as e:
        logger.exception("Unexpected error during SBOM generation")

        raise ProcessingException(
            "An unexpected error occurred during SBOM generation."
        ) from e
