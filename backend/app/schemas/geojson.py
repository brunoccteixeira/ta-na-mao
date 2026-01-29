"""GeoJSON Pydantic schemas."""

from typing import Optional, List, Any, Dict
from pydantic import BaseModel


class GeoJSONGeometry(BaseModel):
    """GeoJSON Geometry object."""

    type: str
    coordinates: Any


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature object."""

    type: str = "Feature"
    properties: Dict[str, Any]
    geometry: Optional[GeoJSONGeometry] = None


class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection object."""

    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]
    metadata: Optional[Dict[str, Any]] = None
