from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from recommender import get_recommendations_by_cuisine

app = FastAPI(title="Recipe Recommendation API", version="1.0")

# กำหนดโครงสร้าง Request Body ด้วย Pydantic
class RecommendationRequest(BaseModel):
    ingredients: List[str]
    cuisines: str

@app.get("/")
def home():
    return {"message": "Recipe Recommendation API is running successfully!"}

@app.post("/recommend")
def recommend_recipes(request: RecommendationRequest):
    try:
        # เรียกใช้ฟังก์ชันประมวลผลจาก recommender.py
        results = get_recommendations_by_cuisine(
            user_ingredients=request.ingredients,
            target_cuisine=request.cuisines,
            top_n=3
        )
        
        if not results:
            return {
                "status": "success",
                "message": f"No recipes found for cuisine: {request.cuisines}",
                "data": []
            }

        return {
            "status": "success",
            "cuisine": request.cuisines,
            "matched_count": len(results),
            "data": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))