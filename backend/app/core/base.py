"""
Base Model for CareFlow AI

Defines the base ORM model with common fields and functionality.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """
    Base class for all ORM models.
    Provides common table naming convention.
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Generate table name from class name.
        Converts CamelCase to snake_case plural.
        """
        name = cls.__name__
        # Convert CamelCase to snake_case
        result = [name[0].lower()]
        for c in name[1:]:
            if c.isupper():
                result.extend(["_", c.lower()])
            else:
                result.append(c)
        table_name = "".join(result)
        # Make plural
        if table_name.endswith("y"):
            return table_name[:-1] + "ies"
        elif not table_name.endswith("s"):
            return table_name + "s"
        return table_name

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model instance to dictionary.

        Returns:
            Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def update_from_dict(self, data: Dict[str, Any]) -> None:
        """
        Update model instance from dictionary.

        Args:
            data: Dictionary with fields to update
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class TimestampMixin:
    """
    Mixin for created_at and updated_at timestamps.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality.
    """

    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    @property
    def is_deleted(self) -> bool:
        """Check if record is soft deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark record as deleted."""
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore soft deleted record."""
        self.deleted_at = None


class BaseModel(Base, TimestampMixin):
    """
    Base model with common fields for all entities.
    Includes UUID primary key and timestamps.
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    def __repr__(self) -> str:
        """String representation of model."""
        class_name = self.__class__.__name__
        return f"<{class_name}(id={self.id})>"
