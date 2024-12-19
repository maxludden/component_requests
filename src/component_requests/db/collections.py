"""Component Request Collection"""

import asyncio
import os
from datetime import datetime
from enum import Enum
from typing import List, Optional

from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import Field, ValidationError
from pymongo.errors import ConnectionFailure


# Enum Definitions
class Status(str, Enum):
    """The status of a component request."""

    NEW = "New"
    IN_PROGRESS = "In Progress"
    NEEDS_FOOTPRINT = "Needs Footprint"
    QC = "QC"
    COMPLETE = "Complete"
    REJECTED = "Rejected"
    REMOVED = "Removed"
    DELETE = "Delete"


class RequestType(str, Enum):
    """The type of component request."""

    COMPONENT_FULL = "Component Full"
    SYMBOL_ONLY = "Symbol Only"
    COMPONENT_FOOTPRINT = "Component Footprint"
    FOOTPRINT_ONLY = "Footprint Only"


class Librarian(str, Enum):
    """The librarian fulfilling the request."""

    RAYMOND_GLOVER = "Raymond Glover"
    RENE_BROWN = "René Brown"
    MARK_HOUCK = "Mark Houck"
    PAUL_SHAVER = "Paul Shaver"
    MAX_LUDDEN = "Max Ludden"


class Solution(str, Enum):
    """The method of solution."""

    FOOTPRINT_EXPERT_BUILD = "Footprint Expert Build"
    FOOTPRINT_EXPERT_DOWNLOAD = "Footprint Expert Download"
    EXISTING = "Existing"
    MANUFACTURER_SPECIFICATION = "Manufacturer Specification"
    COPIED_FROM = "Copied From"


# Request Schema
class ComponentRequest(Document):
    """A component request document."""

    requester: str = Field(
        ..., description="The name of the person making the request."
    )
    request_date: datetime = Field(
        default_factory=datetime.now, description="Date request made"
    )
    status: Status = Field(..., description="Status of the request.")
    request_type: RequestType = Field(..., description="The type of component request.")
    librarian: Librarian = Field(
        ..., description="The librarian fulfilling the request."
    )
    project: str = Field(
        ..., description="The project the request is for."
    )  # Use Harvest API to fetch options
    task: str = Field(
        ..., description="The task for the project."
    )  # Use Harvest API to fetch options
    concord_id: Optional[str] = Field(
        None,
        pattern=r"[a-zA-Z]{1,6}[-_ ]\d+[-_ ]\d+",
        description="The Concord ID of the requested component.",
    )
    concord_folder: str = Field(
        ..., description="Folder the requested component belongs to."
    )
    manufacturer: Optional[str] = Field(
        None, description="The requested component's manufacturer."
    )
    part_number: Optional[str] = Field(
        None, description="The requested component's part number."
    )
    manufacturer_link: Optional[str] = Field(
        None, description="The URL of the component's data sheet."
    )
    solution: Solution = Field(..., description="The method of solution.")
    concord_footprint_id: Optional[str] = Field(
        None,
        pattern=r"[a-zA-Z]{1,6}[-_ ]\d+[-_ ]\d+",
        description="Concord Footprint ID.",
    )
    footprint_name: Optional[str] = Field(
        None, description="The name of the footprint."
    )

    class Settings:
        """The settings for the ComponentRequest collection"""

        uri = os.getenv("MONGO_URI")  # MongoDB URI
        db = os.getenv("MONGO_DB", "requests")  # Database name
        name = os.getenv("MONGO_COLLECTION", "request")  # Collection name

    @classmethod
    async def init_db(cls) -> AsyncIOMotorDatabase:
        """Initialize the Beanie database connection."""
        client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
        database = client[os.getenv("MONGO_DB", "requests")]
        await init_beanie(database=database, document_models=[ComponentRequest])
        return database

    @classmethod
    async def create_request(
        cls,
        requester: Optional[str] = None,
        status: Optional[Status] = None,
        request_type: Optional[RequestType] = None,
        librarian: Optional[Librarian] = None,
        project: Optional[str] = None,
        task: Optional[str] = None,
        concord_id: Optional[str] = None,
        concord_folder: Optional[str] = None,
        manufacturer: Optional[str] = None,
        part_number: Optional[str] = None,
        manufacturer_link: Optional[str] = None,
        solution: Optional[Solution] = None,
        concord_footprint_id: Optional[str] = None,
        footprint_name: Optional[str] = None,
        test: bool = False,
    ) -> None:
        """Create a new component request.

        Args:
            requester (str): The name of the person making the request.
            status (Status): Status of the request.
            request_type (RequestType): The type of component request.
            librarian (Librarian): The librarian fulfilling the request.
            project (str): The project the request is for.
            task (str): The task for the project.
            concord_id (str): The Concord ID of the requested component.
            concord_folder (str): Folder the requested component belongs to.
            manufacturer (str): The requested component's manufacturer.
            part_number (str): The requested component's part number.
            manufacturer_link (HttpUrl): The URL of the component's data sheet.
            solution (Solution): The method of solution.
            concord_footprint_id (str): Concord Footprint ID.
            footprint_name (str): The name of the footprint.
        """
        if test:
            new_request = ComponentRequest(
                requester="Max Ludden",
                status=Status.NEW,
                request_type=RequestType.COMPONENT_FULL,
                librarian=Librarian.MAX_LUDDEN,
                project="[INT] Internal",
                task="Training",
                concord_id="INT-123-456",
                concord_folder="Capacitor",
                manufacturer="Murata",
                part_number="GRM155R71H103KA01D",
                manufacturer_link="https://www.murata.com/en-us/\
products/productdetail?partno=GRM155R71H103KA01D",
                solution=Solution.COPIED_FROM,
                concord_footprint_id="INT-123-456",
                footprint_name="0805_h1.5_n",
            )
        else:

            new_request = ComponentRequest(
                requester=requester if requester is not None else "",
                status=status if status is not None else Status.NEW,
                request_type=(
                    request_type
                    if request_type is not None
                    else RequestType.COMPONENT_FULL
                ),
                librarian=(
                    librarian if librarian is not None else Librarian.RAYMOND_GLOVER
                ),
                project=project if project is not None else "",
                task=task if task is not None else "",
                concord_id=concord_id,
                concord_folder=concord_folder if concord_folder is not None else "",
                manufacturer=manufacturer,
                part_number=part_number,
                manufacturer_link=manufacturer_link,
                solution=solution if solution is not None else Solution.EXISTING,
                concord_footprint_id=concord_footprint_id,
                footprint_name=footprint_name,
            )
        await new_request.insert()

    @classmethod
    async def get_all_requests(cls) -> List["ComponentRequest"]:
        """Get all component requests.

        Returns:
            List[ComponentRequest]: A list of all component requests.
        """
        return await ComponentRequest.find_all().to_list()

    @classmethod
    async def update_request(cls, request_id: str, status: Status) -> bool:
        """Update a component request's status.

        Args:
            request_id (str): The ID of the request to update.
            status (Status): The new status of the request.

        Returns:
            bool: True if the request was successfully updated, False otherwise.
        """
        request = await ComponentRequest.get(request_id)
        if request:
            request.status = status
            try:
                await request.save()
            except ValidationError:
                return False
        return False

    @classmethod
    async def delete_request(cls, request_id: str) -> bool:
        """Delete a component request."""
        request = await ComponentRequest.get(request_id)
        if request:
            try:
                await request.delete()
                # Removed duplicate ValidationError except clause
                return False
            except ValidationError as e:
                print(f"Validation error occurred while deleting the request: {e}")
                return False
            except ConnectionFailure as e:
                print(f"Database error occurred while deleting the request: {e}")
                return False
        return False


async def main():
    """Example usage of the ComponentRequest class."""
    try:
        await ComponentRequest.init_db()

        # Create a new request
        await ComponentRequest.create_request()

        # Retrieve and print all requests
        requests = await ComponentRequest.get_all_requests()
        for req in requests:
            print(req)
    except ValidationError as e:
        print(f"An error occurred: {e}")

    asyncio.run(main())
