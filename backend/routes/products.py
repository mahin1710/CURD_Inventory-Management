from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from backend.database import get_db
from backend import models, schemas

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def _check_sku_uniqueness(db: Session, sku: str, current_product_id: Optional[int] = None):
    """
    Ensures no other product in the database shares the same SKU.
    """
    query = db.query(models.Product).filter(models.Product.sku == sku.strip())
    if current_product_id is not None:
        query = query.filter(models.Product.id != current_product_id)
    
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{sku.strip()}' already exists."
        )

def _verify_category_exists(db: Session, category_id: Optional[int]):
    """
    Ensures the target category exists if category_id is provided.
    """
    if category_id is not None:
        category = db.query(models.Category).filter(models.Category.id == category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {category_id} does not exist."
            )


# ==========================================
# 1. CREATE PRODUCT (POST /products/)
# ==========================================
@router.post(
    "/",
    response_model=schemas.ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product"
)
def create_product(
    product_in: schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    _check_sku_uniqueness(db, product_in.sku)
    _verify_category_exists(db, product_in.category_id)

    new_product = models.Product(
        name=product_in.name.strip(),
        sku=product_in.sku.strip(),
        description=product_in.description.strip() if product_in.description else None,
        price=product_in.price,
        quantity=product_in.quantity,
        low_stock_threshold=product_in.low_stock_threshold,
        category_id=product_in.category_id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    if new_product.quantity > 0:
        initial_movement = models.StockMovement(
            product_id=new_product.id,
            movement_type="INITIAL",
            quantity=new_product.quantity,
            previous_quantity=0,
            new_quantity=new_product.quantity,
            note="Initial inventory added on product creation"
        )
        db.add(initial_movement)
        db.commit()

    return new_product


# ==========================================
# 2. GET ALL PRODUCTS (GET /products/)
# ==========================================
@router.get(
    "/",
    response_model=List[schemas.ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve all products with optional search and category filter"
)
def get_all_products(
    search: Optional[str] = Query(None, description="Search term matching product name or SKU"),
    category_id: Optional[int] = Query(None, description="Filter products by specific category ID"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Product).options(joinedload(models.Product.category))

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                models.Product.name.ilike(term),
                models.Product.sku.ilike(term)
            )
        )

    if category_id is not None:
        query = query.filter(models.Product.category_id == category_id)

    return query.order_by(models.Product.id.asc()).all()


# ==========================================
# 3. GET SINGLE PRODUCT (GET /products/{id})
# ==========================================
@router.get(
    "/{product_id}",
    response_model=schemas.ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a single product by ID"
)
def get_product_by_id(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = (
        db.query(models.Product)
        .options(joinedload(models.Product.category))
        .filter(models.Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )

    return product


# ==========================================
# 4. FULL UPDATE (PUT /products/{id})
# ==========================================
@router.put(
    "/{product_id}",
    response_model=schemas.ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Complete update of product details (PUT)"
)
def update_product_full(
    product_id: int,
    product_in: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )

    _check_sku_uniqueness(db, product_in.sku, current_product_id=product_id)
    _verify_category_exists(db, product_in.category_id)

    product.name = product_in.name.strip()
    product.sku = product_in.sku.strip()
    product.description = product_in.description.strip() if product_in.description else None
    product.price = product_in.price
    product.low_stock_threshold = product_in.low_stock_threshold
    product.category_id = product_in.category_id
    product.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(product)
    return product


# ==========================================
# 5. PARTIAL UPDATE (PATCH /products/{id})
# ==========================================
@router.patch(
    "/{product_id}",
    response_model=schemas.ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Partial update of product details (PATCH)"
)
def update_product_partial(
    product_id: int,
    product_in: schemas.ProductPartialUpdate,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )

    update_data = product_in.model_dump(exclude_unset=True)

    if not update_data:
        return product

    if "sku" in update_data and update_data["sku"] is not None:
        _check_sku_uniqueness(db, update_data["sku"], current_product_id=product_id)
        product.sku = update_data["sku"].strip()

    if "category_id" in update_data:
        _verify_category_exists(db, update_data["category_id"])
        product.category_id = update_data["category_id"]

    if "name" in update_data and update_data["name"] is not None:
        product.name = update_data["name"].strip()

    if "description" in update_data:
        product.description = update_data["description"].strip() if update_data["description"] else None

    if "price" in update_data and update_data["price"] is not None:
        product.price = update_data["price"]

    if "low_stock_threshold" in update_data and update_data["low_stock_threshold"] is not None:
        product.low_stock_threshold = update_data["low_stock_threshold"]

    product.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(product)
    return product


# ==========================================
# 6. DELETE PRODUCT (DELETE /products/{id})
# ==========================================
@router.delete(
    "/{product_id}",
    response_model=schemas.ProductDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a product (DELETE)"
)
def delete_product(
    product_id: int,
    force: bool = Query(
        False,
        description="Force delete product even if active stock quantity is greater than 0"
    ),
    db: Session = Depends(get_db)
):
    """
    Safely delete a product from the inventory:
    - **Safe Deletion Policy**: If the product still has physical stock (`quantity > 0`),
      deletion is blocked with **400 Bad Request** unless `force=true` is explicitly provided.
    - **Orphan Prevention**: Related stock movement records are cleanly removed within
      the same atomic database transaction.
    - Returns **404 Not Found** if the product does not exist.
    """
    # 1. Check whether product exists
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )

    # 2. Safe Deletion Policy: Block deletion if product still has active inventory
    if product.quantity > 0 and not force:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Cannot delete product '{product.name}' because it currently has {product.quantity} items in stock. "
                "Adjust stock quantity to 0 first, or pass force=true to override."
            )
        )

    # 3. Atomic Database Transaction
    try:
        product_name = product.name
        product_sku = product.sku

        # Count stock movements before deletion for clean response summary
        movement_count = db.query(models.StockMovement).filter(
            models.StockMovement.product_id == product_id
        ).count()

        # Delete all associated stock movements first (prevents orphaned records)
        db.query(models.StockMovement).filter(
            models.StockMovement.product_id == product_id
        ).delete(synchronize_session=False)

        # Delete the product record
        db.delete(product)

        # Commit transaction atomically
        db.commit()

        return {
            "status": "success",
            "message": f"Product '{product_name}' (SKU: {product_sku}) and {movement_count} associated stock movement records have been deleted.",
            "deleted_product_id": product_id,
            "deleted_stock_movements_count": movement_count
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database transaction error during deletion: {str(e)}"
        )
