# This file has been modified by the Nextpy Team in 2023 using AI tools and automation scripts. 
# We have rigorously tested these modifications to ensure reliability and performance. Based on successful test results, we are confident in the quality and stability of these changes.

"""Slack toolkit."""

import ssl
from datetime import datetime
from typing import List, Optional

from pydantic import Field, validator

from nextpy.ai.tools.basetool import BaseTool
from nextpy.ai.tools.toolkits.base import BaseToolkit
from nextpy.ai.tools.toolkits.slack_toolkit.slack_tool.base import (
    FetchChannel,
    LoadData,
    SendMessage,
)
from nextpy.ai.tools.toolkits.slack_toolkit.slack_tool.utils import SlackReader


class SlackToolkit(BaseToolkit):
    """Slack toolkit."""

    reader: Optional[SlackReader] = Field(None)
    slack_token: Optional[str] = Field(None)
    earliest_date: Optional[datetime] = Field(None)
    latest_date: Optional[datetime] = Field(None)

    class Config:
        arbitrary_types_allowed = True

    @validator("reader", pre=True, always=True)
    def set_reader(cls, v, values):
        # Create the SSLContext object here
        ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
        return SlackReader(
            slack_token=values.get("slack_token"),
            ssl=ssl_context,
            earliest_date=values.get("earliest_date"),
            latest_date=values.get("latest_date"),
        )

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        return [
            LoadData(
                slack_token=self.slack_token,
                ssl=self.ssl,
                earliest_date=self.earliest_date,
                latest_date=self.latest_date,
            ),
            FetchChannel(
                slack_token=self.slack_token,
                ssl=self.ssl,
                earliest_date=self.earliest_date,
                latest_date=self.latest_date,
            ),
            SendMessage(
                slack_token=self.slack_token,
                ssl=self.ssl,
                earliest_date=self.earliest_date,
                latest_date=self.latest_date,
            ),
        ]

