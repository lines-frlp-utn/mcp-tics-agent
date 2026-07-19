import imaplib
import logging

log = logging.getLogger(__name__)


def create_folder(client: imaplib.IMAP4_SSL, folder_name: str) -> None:
    """
    Creates a folder. Does not fail if it already exists.
    
    Parameters
    ----------
    client : imaplib.IMAP4_SSL
        IMAP client instance.
    folder_name : str
        Name of the folder to create.

    Returns
    -------
    None
    """
    status, resp = client.create(folder_name)
    if status == "OK":
        log.info(f"Folder '{folder_name}' created")
    else:
        log.info(f"Folder '{folder_name}': {resp}")


def move_mail(client: imaplib.IMAP4_SSL, uid: str, folder_source: str, folder_destination: str) -> bool:
    """
    Move a mail. Tries MOVE, with fallback to COPY + DELETE.
    
    Parameters
    ----------
    client : imaplib.IMAP4_SSL
        IMAP client instance.
    uid : str
        UID of the email to move.
    folder_source : str
        Source folder name.
    folder_destination : str
        Destination folder name.

    Returns
    -------
    bool
        True if the mail was moved successfully, False otherwise.
    """
    client.select(folder_source, readonly=False)

    try:
        status, resp = client.uid("MOVE", uid, folder_destination)

        print("\n===== MOVE =====")
        print("UID:", uid)
        print("STATUS:", status)
        print("RESP:", resp)

        if status == "OK":
            # Verificamos si el mail sigue existiendo
            s2, r2 = client.uid("SEARCH", None, f"UID {uid}")
            print("SEARCH luego del MOVE:", s2, r2)
            return True
    except imaplib.IMAP4.error as e:
        log.warning(f"MOVE no soportado: {e}")

    status, _ = client.uid("COPY", uid, folder_destination)
    log.info(f"COPY status: {status}")
    if status != "OK":
        return False

    client.uid("STORE", uid, "+FLAGS", "(\\Deleted)")
    client.expunge()

    return True