# This file has been modified by the Nextpy Team in 2023 using AI tools and automation scripts. 
# We have rigorously tested these modifications to ensure reliability and performance. Based on successful test results, we are confident in the quality and stability of these changes.

"""Simple Reader that loads highlights from Readwise.io."""
import datetime
import json
from typing import List, Optional

from nextpy.ai.rag.document_loaders.basereader import BaseReader
from nextpy.ai.schema import DocumentNode
from security import safe_requests


def _get_readwise_data(api_key: str, updated_after: Optional[datetime.datetime] = None):
    """Uses Readwise's export API to export all highlights, optionally after a specified date.

    See https://readwise.io/api_deets for details.

    Args:
        updated_after (datetime.datetime): The datetime to load highlights after. Useful for updating indexes over time.
    """
    result = []
    next_page = None
    while True:
        response = safe_requests.get(
            url="https://readwise.io/api/v2/export/",
            params={
                "pageCursor": next_page,
                "updatedAfter": updated_after.isoformat() if updated_after else None,
            },
            headers={"Authorization": f"Token {api_key}"},
        )
        response.raise_for_status()
        result.extend(response.json()["results"])
        next_page = response.json().get("nextPageCursor")
        if not next_page:
            break
    return result


class ReadwiseReader(BaseReader):
    """Reader for Readwise highlights."""

    def __init__(self, api_key: str):
        self._api_key = api_key

    def load_data(
        self,
        updated_after: Optional[datetime.datetime] = None,
    ) -> List[DocumentNode]:
        """Load your Readwise.io highlights.

        Args:
            updated_after (datetime.datetime): The datetime to load highlights after. Useful for updating indexes over time.
        """
        metadata = {"updated_after": updated_after}

        readwise_response = _get_readwise_data(
            api_key=self._api_key, updated_after=updated_after
        )
        result = [
            DocumentNode(text=json.dumps(d), extra_info=metadata)
            for d in readwise_response
        ]
        return result
