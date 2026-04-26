from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    DEPENDENCY = "Dependency"
    EXPANSION = "Expansion"
    TORSION = "Torsion"


class Link(BaseModel):
    target_uid: UUID
    relationship_type: RelationshipType


class GeometricNode(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    content: str
    vector_id: Optional[str] = None
    links: List[Link] = Field(default_factory=list)
    weight: float = Field(default=1.0, ge=1.0, le=10.0)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    x: float = Field(default=50.0, ge=-100.0, le=100.0)  # Temporal (0 = Start, 100 = Final Goal)
    y: float = Field(default=50.0, ge=0.0, le=100.0)  # Resolution (0 = Vision, 100 = Code)
    z: float = Field(default=50.0, ge=0.0, le=100.0)  # Aesthetic (0 = Robotic, 100 = Persona)

    @property
    def is_locked(self) -> bool:
        """
        Nodes older than 24 hours are locked (Read-Only) according to the
        'Gade Murde' Read-Append protocol.
        """
        now = datetime.now(timezone.utc)
        age = now - self.timestamp
        return age.total_seconds() > 24 * 3600
