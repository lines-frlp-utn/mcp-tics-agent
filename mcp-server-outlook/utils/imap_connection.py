import imaplib
import logging
import msal

from config import conf


log = logging.getLogger(__name__)

IMAP_HOST = "outlook.office365.com"
IMAP_PORT = 993


def _get_token() -> str:
    """
    Obtains an OAuth2 access token for the Outlook IMAP server using MSAL.

    Returns
    -------
    str
        OAuth2 access token for the Outlook IMAP server.
    """
    app = msal.ConfidentialClientApplication(
        conf.CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{conf.TENANT_ID}",
        client_credential=conf.CLIENT_SECRET,
    )

    result = app.acquire_token_for_client(scopes=["https://outlook.office365.com/.default"])

    if "access_token" not in result:
        raise RuntimeError(
            f"Couldn't get token: {result.get('error_description')}"
        )

    return result["access_token"]


def connect() -> imaplib.IMAP4_SSL:
    """
    Establishes an IMAP connection to the Outlook server using OAuth2 authentication.

    Returns
    -------
    imaplib.IMAP4_SSL
        Connected IMAP client instance.
    """

    token = _get_token()

    auth_string = (
        f"user={conf.EMAIL_ACCOUNT}\x01"
        f"auth=Bearer {token}\x01\x01"
    )

    client = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    client.authenticate(
        "XOAUTH2",
        lambda _: auth_string.encode()
    )

    log.info("IMAP connection established successfully.")

    return client