import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Plant

app = FastAPI(title="Spiritual Plant Catalog API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Spiritual Plant Catalog API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# Utility to convert Mongo _id to str
class PlantOut(BaseModel):
    id: str
    name: str
    species: Optional[str] = None
    pot_style: Optional[str] = None
    chakra: Optional[str] = None
    mantra: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tags: List[str] = []
    featured: bool = False
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


def serialize_plant(doc) -> PlantOut:
    return PlantOut(
        id=str(doc.get("_id")),
        name=doc.get("name"),
        species=doc.get("species"),
        pot_style=doc.get("pot_style"),
        chakra=doc.get("chakra"),
        mantra=doc.get("mantra"),
        description=doc.get("description"),
        price=doc.get("price"),
        tags=doc.get("tags", []),
        featured=doc.get("featured", False),
        image_url=doc.get("image_url"),
    )

# Seed some example plants if collection empty
@app.post("/api/plants/seed")
def seed_plants():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    count = db["plant"].count_documents({})
    if count > 0:
        return {"inserted": 0, "message": "Already seeded"}

    samples: List[Plant] = [
        Plant(
            name="Red Spider Lily",
            species="Lycoris radiata",
            pot_style="Matte porcelain, pale pink",
            chakra="Root",
            mantra="I am grounded and safe.",
            description="A serene arrangement where a single glowing orb invites a grounding breath.",
            price=120.0,
            tags=["minimalist", "grounding", "red"],
            featured=True,
            image_url="https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=1200&q=60",
        ),
        Plant(
            name="White Peace Lily",
            species="Spathiphyllum",
            pot_style="Sand-textured ceramic",
            chakra="Heart",
            mantra="I breathe in calm, I breathe out love.",
            description="Soft curves and gentle leaves that soften any room.",
            price=95.0,
            tags=["peace", "white", "air-purifier"],
            featured=False,
            image_url="https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1200&q=60",
        ),
        Plant(
            name="Golden Pothos",
            species="Epipremnum aureum",
            pot_style="Brushed brass large pot",
            chakra="Solar Plexus",
            mantra="I shine with quiet confidence.",
            description="Trailing vines spill like sunlit ribbons.",
            price=80.0,
            tags=["gold", "vining"],
            featured=False,
            image_url="https://images.unsplash.com/photo-1524594081293-190a2fe0baae?auto=format&fit=crop&w=1200&q=60",
        ),
    ]

    inserted = 0
    for s in samples:
        create_document("plant", s)
        inserted += 1
    return {"inserted": inserted}

@app.get("/api/plants", response_model=List[PlantOut])
def list_plants(q: Optional[str] = None, featured: Optional[bool] = None, limit: int = 50):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    filt = {}
    if q:
        filt["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"species": {"$regex": q, "$options": "i"}},
            {"tags": {"$regex": q, "$options": "i"}},
            {"chakra": {"$regex": q, "$options": "i"}},
        ]
    if featured is not None:
        filt["featured"] = featured

    docs = get_documents("plant", filt, limit)
    return [serialize_plant(d) for d in docs]

@app.post("/api/plants", response_model=PlantOut)
def create_plant(plant: Plant):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    inserted_id = create_document("plant", plant)
    doc = db["plant"].find_one({"_id": ObjectId(inserted_id)})
    return serialize_plant(doc)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
