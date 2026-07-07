import os
import logging
from typing import Any

logger = logging.getLogger(__name__)

def get_credentials() -> Any:
    """
    Resolves Google Cloud credentials using Application Default Credentials (ADC)
    or checking path overrides in the environment.
    """
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_path:
        logger.info(f"Using Google Application Credentials from path: {credentials_path}")
    else:
        logger.info("Using Application Default Credentials (ADC)")
    
    # Deferred import to prevent startup collisions if google-auth package is missing.
    try:
        import google.auth
        credentials, project = google.auth.default()
        return credentials
    except ImportError:
        logger.warning("google-auth package is not installed. Native calls will fail.")
        return None
