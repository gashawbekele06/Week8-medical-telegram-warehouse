"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class TopProduct(BaseModel):
    product_term: str
    mention_count: int


class ChannelActivity(BaseModel):
    post_date: date
    message_count: int
    avg_views: float


class MessageSearchResult(BaseModel):
    message_id: int
    channel_name: str
    message_text: str
    view_count: int
    message_timestamp: date


class VisualContentStats(BaseModel):
    channel_name: str
    total_images: int
    promotional_count: int
    product_display_count: int
    lifestyle_count: int
    other_count: int
    visual_percentage: float
