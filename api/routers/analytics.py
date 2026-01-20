"""
Analytical endpoints router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from api.database import get_db
from api.schemas import TopProduct, ChannelActivity, MessageSearchResult, VisualContentStats
from typing import List

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/reports/top-products", response_model=List[TopProduct])
def top_products(limit: int = 10, db: Session = Depends(get_db)):
    """Top mentioned terms/products across all messages (simple word count)"""
    query = text("""
    WITH words AS (
        SELECT UNNEST(STRING_TO_ARRAY(LOWER(message_text), ' ')) AS word
        FROM public_marts.fct_messages
        WHERE message_text IS NOT NULL
    )
    SELECT word AS product_term, COUNT(*) AS mention_count
    FROM words
    WHERE LENGTH(word) > 3  -- filter short/common words
      AND word NOT IN ('the', 'and', 'for', 'with', 'from')  -- add more stop words if needed
    GROUP BY word
    ORDER BY mention_count DESC
    LIMIT :limit
    """)
    result = db.execute(query, {"limit": limit}).fetchall()
    if not result:
        raise HTTPException(status_code=404, detail="No products found")
    return [{"product_term": row[0], "mention_count": row[1]} for row in result]


@router.get("/channels/{channel_name}/activity", response_model=List[ChannelActivity])
def channel_activity(channel_name: str, db: Session = Depends(get_db)):
    """Posting activity and trends for a specific channel"""
    query = text("""
    SELECT 
        DATE(message_timestamp) AS post_date,
        COUNT(*) AS message_count,
        AVG(view_count) AS avg_views
    FROM public_marts.fct_messages f
    JOIN public_marts.dim_channels c ON f.channel_key = c.channel_key
    WHERE LOWER(c.channel_name) = LOWER(:channel_name)
    GROUP BY post_date
    ORDER BY post_date DESC
    """)
    result = db.execute(query, {"channel_name": channel_name}).fetchall()
    if not result:
        raise HTTPException(
            status_code=404, detail=f"Channel {channel_name} not found or no activity")
    return [{"post_date": row[0], "message_count": row[1], "avg_views": row[2]} for row in result]


@router.get("/search/messages", response_model=List[MessageSearchResult])
def search_messages(query: str, limit: int = 20, db: Session = Depends(get_db)):
    """Search messages containing a keyword"""
    search_term = f"%{query.lower()}%"
    sql_query = text("""
    SELECT 
        f.message_id,
        c.channel_name,
        f.message_text,
        f.view_count,
        DATE(f.message_timestamp) AS message_timestamp
    FROM public_marts.fct_messages f
    JOIN public_marts.dim_channels c ON f.channel_key = c.channel_key
    WHERE LOWER(f.message_text) LIKE :search_term
    ORDER BY f.view_count DESC
    LIMIT :limit
    """)
    result = db.execute(
        sql_query, {"search_term": search_term, "limit": limit}).fetchall()
    if not result:
        raise HTTPException(
            status_code=404, detail=f"No messages found for query '{query}'")
    return [{"message_id": row[0], "channel_name": row[1], "message_text": row[2], "view_count": row[3], "message_timestamp": row[4]} for row in result]


@router.get("/reports/visual-content", response_model=List[VisualContentStats])
def visual_content_stats(db: Session = Depends(get_db)):
    """Statistics about image usage across channels (from Task 3 enrichment)"""
    query = text("""
    SELECT 
        c.channel_name,
        COUNT(y.message_id) AS total_images,
        SUM(CASE WHEN y.image_category = 'promotional' THEN 1 ELSE 0 END) AS promotional_count,
        SUM(CASE WHEN y.image_category = 'product_display' THEN 1 ELSE 0 END) AS product_display_count,
        SUM(CASE WHEN y.image_category = 'lifestyle' THEN 1 ELSE 0 END) AS lifestyle_count,
        SUM(CASE WHEN y.image_category = 'other' THEN 1 ELSE 0 END) AS other_count,
        ROUND(COUNT(y.message_id)::numeric / COUNT(f.message_id) * 100, 1) AS visual_percentage
    FROM public_marts.fct_messages f
    LEFT JOIN public_marts.fct_image_detections y USING (message_id)
    JOIN public_marts.dim_channels c ON f.channel_key = c.channel_key
    GROUP BY c.channel_name
    ORDER BY total_images DESC
    """)
    result = db.execute(query).fetchall()

    if not result:
        # Return empty list if no data (safe for Pydantic list model)
        return []

    return [{
        "channel_name": row[0],
        "total_images": row[1],
        "promotional_count": row[2],
        "product_display_count": row[3],
        "lifestyle_count": row[4],
        "other_count": row[5],
        "visual_percentage": row[6] or 0.0  # handle NULL
    } for row in result]
