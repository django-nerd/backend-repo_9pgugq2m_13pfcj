"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

# Example schemas (retain for reference):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Plant catalog schema
class Plant(BaseModel):
    """
    Collection name: "plant"
    Represents a plant in a large pot with a spiritual twist.
    """
    name: str = Field(..., description="Display name")
    species: Optional[str] = Field(None, description="Botanical species")
    pot_style: Optional[str] = Field(None, description="Design of the big pot")
    chakra: Optional[str] = Field(None, description="Associated chakra or energy center")
    mantra: Optional[str] = Field(None, description="Short affirmation or mantra")
    description: Optional[str] = Field(None, description="Story or spiritual meaning")
    price: Optional[float] = Field(None, ge=0, description="Price in dollars")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    featured: bool = Field(False, description="Whether highlighted on homepage")
    image_url: Optional[HttpUrl] = Field(None, description="Photo URL of the plant in its pot")
