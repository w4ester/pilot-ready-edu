"""Shared base class for API schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ApiBaseModel(BaseModel):
    """Base model that relaxes protected namespace guards for API fields."""

    model_config = ConfigDict(protected_namespaces=())
