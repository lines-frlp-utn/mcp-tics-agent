from email.header import decode_header as _decode_header
import email
import logging

from utils.imap_connection import connect


log = logging.getLogger(__name__)


def decodificate_header(value: str | None) -> str:
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


def extract_body(message) -> str:
    """
    Extracts the body of an email message.
    
    Parameters
    ----------
    message : email.message.Message
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


def parse_message(uid: bytes, raw: bytes) -> dict:
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
        "subject": decodificate_header(message.get("Subject")),
        "sender": decodificate_header(message.get("From")),
        "date": decodificate_header(message.get("Date")),
        "body": extract_body(message),
    }


def read_by_uid(folder: str, uid: str) -> dict:
    """
    Reads a single email message from a folder by its UID.

    Parameters
    ----------
    folder : str
        The folder from which to read the email (e.g., "INBOX", "CVG").
    uid : str
        The unique identifier of the email message to fetch.

    Returns
    -------
    dict
        The extracted information of the email.
    """
    client = connect()

    try:
        client.select(folder, readonly=True)

        status, raw = client.uid("FETCH", uid, "(RFC822)")

        if status != "OK":
            raise RuntimeError(
                f"Error fetching mail UID {uid} in {folder}"
            )

        for item in raw:
            if isinstance(item, tuple) and item[1]:
                return parse_message(uid.encode(), item[1])

        raise RuntimeError(
            f"Mail UID {uid} not found in {folder}"
        )

    finally:
        try:
            client.logout()
        except Exception:
            pass


def search(folder: str, criterion: str, limit: int) -> list[dict]:
    """
    Searches emails in a specified folder based on a search criterion and limit.
    
    Parameters
    ----------
    folder : str
        The folder from which to read emails (e.g., "CVG", "Mail_Institucional").
    criterion : str
        The search criterion for fetching emails (e.g., "UNSEEN", "ALL").
    limit : int
        The maximum number of emails to fetch.

    Returns
    -------
    list[dict]
        A list of dictionaries containing the extracted information of the emails.
    """
    mails = []
    client = connect()

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
                        parse_message(uid, item[1])
                    )

    finally:
        try:
            client.logout()
        except Exception:
            pass

    return mails


def read_unread_items(
    folder: str = "INBOX",
    limit: int = 10
) -> list[dict]:
    """
    Returns unread emails without marking them as read.
    
    Parameters
    ----------
    folder : str
        The folder from which to read emails (e.g., "CVG", "Mail_Institucional").
    limit : int
        The maximum number of emails to fetch.

    Returns
    -------
    list[dict]
        A list of dictionaries containing the extracted information of the unread emails.
    """
    return search(folder, "UNSEEN", limit)


def read_all(
    folder: str = "INBOX",
    limit: int = 10
) -> list[dict]:
    """
    Returns the latest emails from a folder.
    
    Parameters
    ----------
    folder : str
        The folder from which to read emails (e.g., "INBOX", "CVG", "Mail_Institucional").
    limit : int
        The maximum number of emails to fetch.

    Returns
    -------
    list[dict]
        A list of dictionaries containing the extracted information of the emails.
    """
    return search(folder, "ALL", limit)