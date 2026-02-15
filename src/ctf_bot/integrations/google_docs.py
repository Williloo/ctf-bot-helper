"""Google Docs integration for CTF bot."""
from typing import Optional, Tuple

from google.oauth2 import service_account
from googleapiclient.discovery import build

from ..config import SERVICE_ACCOUNT_FILE, SCOPES, FOLDER_ID, TARGET_DOC_NAME, TEMPLATE_DOC_NAME


# ----------------------------
# Google API helpers
# ----------------------------
def make_creds():
    return service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )


def make_docs_service(creds):
    return build("docs", "v1", credentials=creds, cache_discovery=False)


def make_drive_service(creds):
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def find_doc_in_folder(drive_service, folder_id: str, doc_name: str) -> str:
    """
    Find a Google Doc with exact name `doc_name` inside `folder_id`.
    If multiple matches exist, pick the most recently modified.
    Returns the doc fileId.
    """
    # Exact match on name. If you want "contains" matching later, we can adjust.
    q = (
        f"'{folder_id}' in parents and "
        f"mimeType='application/vnd.google-apps.document' and "
        f"name='{doc_name}' and trashed=false"
    )

    resp = drive_service.files().list(
        q=q,
        fields="files(id,name,modifiedTime)",
        orderBy="modifiedTime desc",
        pageSize=10,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()

    files = resp.get("files", [])
    if not files:
        # If the target document doesn't exist, create it from template
        # But only do this for the TARGET_DOC_NAME, not for templates
        if doc_name == TARGET_DOC_NAME:
            return copy_document_from_template(
                drive_service, TEMPLATE_DOC_NAME, doc_name, folder_id
            )
        else:
            raise RuntimeError(
                f"No Google Doc named '{doc_name}' found in the shared folder."
            )
    return files[0]["id"]


def paragraph_text(paragraph: dict) -> str:
    """Concatenate visible text from a paragraph."""
    parts = []
    for el in paragraph.get("elements", []):
        tr = el.get("textRun")
        if tr and "content" in tr:
            parts.append(tr["content"])
    return "".join(parts)


def find_agenda_table(doc: dict) -> Optional[Tuple[dict, int]]:
    """
    Find the first TABLE that appears AFTER a paragraph containing 'Agenda'
    (case-insensitive). Returns (table_struct, table_element_index_in_body_content).
    """
    content = doc.get("body", {}).get("content", [])
    agenda_idx = None

    # 1) find 'Agenda' paragraph
    for i, elem in enumerate(content):
        para = elem.get("paragraph")
        if not para:
            continue
        txt = paragraph_text(para).strip().lower()
        if "agenda items:" == txt or txt.startswith("agenda items:"):
            agenda_idx = i
            break

    if agenda_idx is None:
        return None

    # 2) find the next table after that
    for j in range(agenda_idx + 1, len(content)):
        tbl = content[j].get("table")
        if tbl:
            return tbl, j

    return None


def get_first_cell_start_index(table: dict, row_index: int, col_index: int) -> int:
    """
    Returns the startIndex where we can insert text for a given cell.
    We use the startIndex of the first element in the cell content.
    """
    cell = table["tableRows"][row_index]["tableCells"][col_index]
    cell_content = cell.get("content", [])
    if not cell_content:
        raise RuntimeError("Table cell has no content; can't determine insertion index.")

    first = cell_content[0]
    si = first.get("startIndex")
    if si is None:
        para = first.get("paragraph")
        if para and "elements" in para and para["elements"]:
            si = para["elements"][0].get("startIndex")
    if si is None:
        raise RuntimeError("Could not determine startIndex for table cell.")
    return si


def add_row_and_fill(docs_service, doc_id: str, text: str) -> None:
    """
    1) Locate the table under 'Agenda'
    2) Insert a new row at the bottom
    3) Re-fetch doc (indices shift)
    4) Insert text into first cell of new row
    """
    doc = docs_service.documents().get(documentId=doc_id).execute()
    found = find_agenda_table(doc)
    if not found:
        raise RuntimeError("Couldn't find an 'Agenda' heading followed by a table.")

    table, table_body_index = found
    rows = table.get("tableRows", [])
    if not rows:
        raise RuntimeError("Agenda table has no rows.")

    insert_below_row = len(rows) - 1

    requests = [
        {
            "insertTableRow": {
                "tableCellLocation": {
                    "tableStartLocation": {
                        "index": doc["body"]["content"][table_body_index]["startIndex"]
                    },
                    "rowIndex": insert_below_row,
                    "columnIndex": 0,
                },
                "insertBelow": True,
            }
        }
    ]

    docs_service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()

    doc2 = docs_service.documents().get(documentId=doc_id).execute()
    found2 = find_agenda_table(doc2)
    if not found2:
        raise RuntimeError("Agenda table disappeared after row insert (unexpected).")
    table2, _ = found2

    new_row_index = len(table2["tableRows"]) - 1
    cell_start = get_first_cell_start_index(table2, new_row_index, 0)

    requests2 = [
        {
            "insertText": {
                "location": {"index": cell_start},
                "text": text.strip(),
            }
        }
    ]

    docs_service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests2}
    ).execute()


def count_meeting_docs(drive_service, folder_id: str) -> int:
    """
    Count the number of documents in the folder that match the meeting pattern.
    Returns the count of documents containing 'MEETING' or 'meeting' in the name.
    """
    q = (
        f"'{folder_id}' in parents and "
        f"mimeType='application/vnd.google-apps.document' and "
        f"(name contains 'MEETING' or name contains 'meeting') and "
        f"trashed=false"
    )

    resp = drive_service.files().list(
        q=q,
        fields="files(id,name)",
        pageSize=1000,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()

    return len(resp.get("files", []))-2


def replace_meeting_number(docs_service, doc_id: str, meeting_number: int) -> None:
    """
    Find and replace 'XX' with the meeting number in the document.
    """
    # Simple replace all approach
    requests = [{
        'replaceAllText': {
            'containsText': {
                'text': 'XX',
                'matchCase': True
            },
            'replaceText': f'{meeting_number:02d}'
        }
    }]
    
    # Apply the replacement
    docs_service.documents().batchUpdate(
        documentId=doc_id, body={'requests': requests}
    ).execute()


def copy_document_from_template(drive_service, template_name: str, new_name: str, folder_id: str) -> str:
    """
    Copy a document from a template and place it in the specified folder.
    Returns the new document ID.
    """
    # Count existing meeting docs BEFORE creating the new one
    meeting_count = count_meeting_docs(drive_service, folder_id)
    meeting_number = meeting_count + 1  # Next meeting number
    
    # Find the template document (but avoid recursion by searching directly)
    template_q = (
        f"'{folder_id}' in parents and "
        f"mimeType='application/vnd.google-apps.document' and "
        f"name='{template_name}' and trashed=false"
    )
    
    template_resp = drive_service.files().list(
        q=template_q,
        fields="files(id,name,modifiedTime)",
        orderBy="modifiedTime desc",
        pageSize=1,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    
    template_files = template_resp.get("files", [])
    if not template_files:
        raise RuntimeError(f"Template '{template_name}' not found in folder.")
    
    template_id = template_files[0]["id"]
    
    # Copy the template
    copy_body = {
        'name': new_name,
        'parents': [folder_id]
    }
    
    result = drive_service.files().copy(
        fileId=template_id,
        body=copy_body,
        supportsAllDrives=True
    ).execute()

    # Create docs service with same credentials to replace XX
    try:
        creds = make_creds()  # Use the same credential function
        docs_service = make_docs_service(creds)
        replace_meeting_number(docs_service, result['id'], meeting_number)
    except Exception as replace_error:
        # Document was created but XX replacement failed - still return the document
        # The user can manually fix the XX if needed
        pass
    
    return result['id']

class GoogleDocsManager:
    """High-level interface for Google Docs operations."""
    
    def __init__(self):
        self.creds = make_creds()
        self.drive_service = make_drive_service(self.creds)
        self.docs_service = make_docs_service(self.creds)
    
    def add_agenda_item(self, item: str) -> None:
        """Add an item to the agenda table in the target document."""
        doc_id = find_doc_in_folder(self.drive_service, FOLDER_ID, TARGET_DOC_NAME)
        add_row_and_fill(self.docs_service, doc_id, item)
    
    def create_from_template(self, new_name: str, template_name: str = None) -> str:
        """Create a new document from template and return its ID."""
        if template_name is None:
            template_name = TEMPLATE_DOC_NAME
        
        doc_id = copy_document_from_template(
            self.drive_service, template_name, new_name, FOLDER_ID
        )
        return doc_id
