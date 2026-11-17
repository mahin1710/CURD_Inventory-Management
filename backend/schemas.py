from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# ==========================================
# CATEGORY SCHEMAS (Preview)
# ==========================================

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# PRODUCT SCHEMAS
# ==========================================

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Product name (required)")
    sku: str = Field(..., min_length=1, max_length=100, description="Unique Stock Keeping Unit (required)")
    description: Optional[str] = Field(None, max_length=1000, description="Optional product description")
    price: float = Field(..., ge=0.0, description="Unit price (cannot be negative)")
    quantity: int = Field(default=0, ge=0, description="Initial stock quantity (cannot be negative)")
    low_stock_threshold: int = Field(default=5, ge=0, description="Minimum stock threshold for alerts")
    category_id: Optional[int] = Field(None, description="Optional Category ID foreign key")

class ProductCreate(ProductBase):
    """Schema for validating product creation requests"""
    pass

class ProductResponse(ProductBase):
    """Schema for formatting product response data"""
    id: int
    created_at: datetime
    updated_at: datetime

    # ConfigDict(from_attributes=True) allows Pydantic to read SQLAlchemy ORM objects
    model_config = ConfigDict(from_attributes=True)
