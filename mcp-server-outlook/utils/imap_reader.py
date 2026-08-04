"""Utilities for reading and parsing emails from an IMAP mailbox."""

from email.header import decode_header as _decode_header
from email.message import Message
import email
import logging
import imaplib


log = logging.getLogger(__name__)


def read_by_uid(client: imaplib.IMAP4_SSL, folder: str, uid: str) -> dict:
    """
    Reads a single email message from a folder by its UID.

    Parameters
    ----------
    client : imaplib.IMAP4_SSL
        IMAP client instance.
    folder : str
        The folder from which to read the email (e.g., "INBOX", "CVG").
    uid : str
        The unique identifier of the email message to fetch.

    Returns
    -------
    dict
        The extracted information of the email.

    Raises
    ------
    RuntimeError
        If the IMAP fetch fails, or no email with the given UID exists in the folder.
    """

    try:
        client.select(folder, readonly=True)

        status, raw = client.uid("FETCH", uid, "(RFC822)")

        if status != "OK":
            raise RuntimeError(
                f"Error fetching mail UID {uid} in {folder}"
            )

        for item in raw:
            if isinstance(item, tuple) and item[1]:
                return _parse_message(uid.encode(), item[1])

        raise RuntimeError(
            f"Mail UID {uid} not found in {folder}"
        )
    
    except Exception as e:
        log.error(f"Error reading mail UID {uid} in {folder}: {e}")
        raise


def search(client: imaplib.IMAP4_SSL, folder: str, criterion: str, limit: int) -> list[dict]:
    """
    Searches emails in a specified folder based on a search criterion and limit.

    If `limit` is zero or negative, returns an empty list without querying the server.

    Parameters
    ----------
    client : imaplib.IMAP4_SSL
        IMAP client instance.
    folder : str
        The folder from which to read emails (e.g., "CVG", "Mail_Institucional").
    criterion : str
        The search criterion for fetching emails (e.g., "UNSEEN", "ALL").
    limit : int
        The maximum number of emails to fetch. Non-positive values short-circuit to an empty list.

    Returns
    -------
    list[dict]
        A list of dictionaries containing the extracted information of the emails.

    Raises
    ------
    RuntimeError
        If the IMAP search request fails.
    """
    if limit <= 0:
        return []
    
    mails = []

    try:
        client.select(folder, readonly=True)

        status, datos = client.uid(
            "SEARCH",
            None,
            criterion
        )

        if status != "OK":
            raise RuntimeError(
                f"Error fetching mails ({criterion}) in {folder}"
            )

        uids = datos[0].split()

        log.info(
            f"Found emails ({criterion}): {len(uids)} "
            f"— processing {min(len(uids), limit)}"
        )

        for uid in uids[-limit:]:
            status, raw = client.uid(
                "FETCH",
                uid,
                "(RFC822)"
            )

            if status != "OK":
                log.warning(
                    f"Could not fetch mail UID {uid.decode()}"
                )
                continue

            for item in raw:
                if isinstance(item, tuple) and item[1]:
                    mails.append(
                        _parse_message(uid, item[1])
                    )

    except Exception as e:
        log.error(f"Error searching mails ({criterion}) in {folder}: {e}")
        raise

    return mails


# Helper functions
def _decodificate_header(value: str | None) -> str:
    """
    Decodes an email header value.
    
    Parameters
    ----------
    value : str | None
        The header value to decode.

    Returns
    -------
    str
        The decoded header value.
    """
    if not value:
        return ""

    result = []

    for part, encoding in _decode_header(value):
        if isinstance(part, bytes):
            result.append(
                part.decode(
                    encoding or "utf-8",
                    errors="replace"
                )
            )
        else:
            result.append(part)

    return "".join(result)


def _extract_body(message: Message) -> str:
    """
    Extracts the body of an email message.

    Parameters
    ----------
    message : Message
        The email message object.

    Returns
    -------
    str
        The extracted body of the email.
    """
    if message.is_multipart():
        for part in message.walk():
            if (
                part.get_content_type() == "text/plain"
                and part.get_content_disposition() != "attachment"
            ):
                payload = part.get_payload(decode=True)

                if payload:
                    return payload.decode(
                        part.get_content_charset() or "utf-8",
                        errors="replace",
                    )

    else:
        payload = message.get_payload(decode=True)

        if payload:
            return payload.decode(
                message.get_content_charset() or "utf-8",
                errors="replace",
            )

    return ""


def _parse_message(uid: bytes, raw: bytes) -> dict:
    """
    Parses an email message and extracts relevant information.
    
    Parameters
    ----------
    uid : bytes
        The unique identifier of the email message.
    raw : bytes
        The raw email message in bytes.

    Returns
    -------
    dict
        The extracted information of the email.
    """
    message = email.message_from_bytes(raw)

    return {
        "mail_id": uid.decode(),
        "subject": _decodificate_header(message.get("Subject")),
        "sender": _decodificate_header(message.get("From")),
        "date": _decodificate_header(message.get("Date")),
        "body": _extract_body(message),
    }
