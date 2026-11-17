from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models, schemas

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

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
    """
    Create a new inventory product with strict validation:
    - **name**: Required string (1-200 chars)
    - **sku**: Required unique SKU code
    - **price**: Non-negative float
    - **quantity**: Non-negative integer (default 0)
    - **low_stock_threshold**: Non-negative integer (default 5)
    - **category_id**: Optional ID of an existing category
    """
    # 1. Check for Duplicate SKU (SKU uniqueness constraint)
    existing_product = db.query(models.Product).filter(
        models.Product.sku == product_in.sku.strip()
    ).first()
    
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{product_in.sku}' already exists."
        )

    # 2. Check Category Existence if category_id is supplied
    if product_in.category_id is not None:
        category = db.query(models.Category).filter(
            models.Category.id == product_in.category_id
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {product_in.category_id} does not exist."
            )

    # 3. Create SQLAlchemy ORM Instance
    new_product = models.Product(
        name=product_in.name.strip(),
        sku=product_in.sku.strip(),
        description=product_in.description.strip() if product_in.description else None,
        price=product_in.price,
        quantity=product_in.quantity,
        low_stock_threshold=product_in.low_stock_threshold,
        category_id=product_in.category_id
    )

    # 4. Persist to Database
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    # 5. Record Initial Stock Movement (Audit Trail) if initial quantity > 0
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
