# This file has been modified by the Nextpy Team in 2023 using AI tools and automation scripts. 
# We have rigorously tested these modifications to ensure reliability and performance. Based on successful test results, we are confident in the quality and stability of these changes.

"""Building the app and initializing all prerequisites."""

from __future__ import annotations

import os
import re
import subprocess
import sys

from nextpy import constants
from nextpy.utils import console
from security import safe_command


def generate_requirements():
    """Generate a requirements.txt file based on the current environment."""
    # Run the command and get the output
    result = safe_command.run(subprocess.run, [sys.executable, "-m", "pipdeptree", "--warn", "silence"],
        capture_output=True,
        text=True,
    )

    # Filter the output lines using a regular expression
    lines = result.stdout.split("\n")
    filtered_lines = [line for line in lines if re.match(r"^\w+", line)]

    # Write the filtered lines to requirements.txt
    with open("requirements.txt", "w") as f:
        for line in filtered_lines:
            f.write(line + "\n")


def check_requirements():
    """Check if the requirements are installed."""
    if not os.path.exists(constants.RequirementsTxt.FILE):
        console.warn("It seems like there's no requirements.txt in your project.")
        response = console.ask(
            "Would you like us to auto-generate one based on your current environment?",
            choices=["y", "n"],
        )

        if response == "y":
            generate_requirements()
        else:
            console.error(
                "Please create a requirements.txt file in your project's root directory and try again."
            )
            exit()
