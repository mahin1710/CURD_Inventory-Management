from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

# ==========================================
# CATEGORY SCHEMAS
# ==========================================

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")

class CategorySummary(BaseModel):
    """Compact category details for embedding inside product responses"""
    id: int
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

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

class ProductUpdate(BaseModel):
    """
    Schema for complete product update (PUT).
    Note: 'quantity' is excluded to preserve stock audit integrity.
    Stock movements must be recorded through the dedicated stock module.
    """
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    sku: str = Field(..., min_length=1, max_length=100, description="Unique Stock Keeping Unit")
    description: Optional[str] = Field(None, max_length=1000, description="Product description")
    price: float = Field(..., ge=0.0, description="Unit price (cannot be negative)")
    low_stock_threshold: int = Field(default=5, ge=0, description="Low stock alert threshold")
    category_id: Optional[int] = Field(None, description="Optional Category ID")

class ProductPartialUpdate(BaseModel):
    """
    Schema for partial product update (PATCH).
    All fields are optional. 'quantity' is excluded to protect stock audit records.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Product name")
    sku: Optional[str] = Field(None, min_length=1, max_length=100, description="Unique SKU")
    description: Optional[str] = Field(None, max_length=1000, description="Product description")
    price: Optional[float] = Field(None, ge=0.0, description="Unit price (cannot be negative)")
    low_stock_threshold: Optional[int] = Field(None, ge=0, description="Low stock alert threshold")
    category_id: Optional[int] = Field(None, description="Category ID")

class ProductResponse(ProductBase):
    """Schema for formatting product response data with category details"""
    id: int
    category: Optional[CategorySummary] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ProductDeleteResponse(BaseModel):
    """Schema for product deletion confirmation"""
    status: str = Field(..., example="success")
    message: str = Field(..., example="Product successfully deleted")
    deleted_product_id: int
    deleted_stock_movements_count: int
