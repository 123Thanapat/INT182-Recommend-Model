from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from recommender import get_recommendations_by_cuisine_and_ingredients
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Recipe Recommendation API",
    description=(
        "API แนะนำสูตรอาหารจากส่วนผสมและประเภทอาหาร (คืนค่า Top 3 เสมอ)"
    ),
    version="3.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # อนุญาตทุก Origin (หรือเปลี่ยนเป็น URL เว็บคุณ)
    allow_credentials=True,
    allow_methods=["*"],  # อนุญาตทุก Method (GET, POST, OPTIONS ฯลฯ)
    allow_headers=["*"],  # อนุญาตทุก Header
)

@app.api_route("/", methods=["GET", "HEAD"])
def read_root():
    return {"message": "Recipe Recommendation API is ready!"}


# Pydantic Model สำหรับรับ ingredients และ cuisines
class CuisineIngredientRequest(BaseModel):
  ingredients: List[str]  # เช่น ["chicken", "garlic", "chili"]
  cuisines: str  # เช่น "Thai", "Italian", "Mexican"


@app.post("/recommend")
def recommend_by_cuisine_endpoint(payload: CuisineIngredientRequest):
  """รับ JSON Body ที่มีทั้งส่วนผสมและประเภทอาหาร และคืนค่าผลลัพธ์ Top 3 เสมอ"""
  try:
    if not payload.ingredients:
      raise HTTPException(
          status_code=400, detail="กรุณาระบุรายการส่วนผสม (ingredients)"
      )
    if not payload.cuisines:
      raise HTTPException(
          status_code=400, detail="กรุณาระบุประเภทอาหาร (cuisines)"
      )

    recommendations = get_recommendations_by_cuisine_and_ingredients(
        user_ingredients=payload.ingredients, target_cuisine=payload.cuisines
    )

    if not recommendations:
      raise HTTPException(
          status_code=404, detail="ไม่พบสูตรอาหารที่ตรงกับเงื่อนไข"
      )

    return {
        "ingredients": payload.ingredients,
        "cuisines": payload.cuisines,
        "recipes": recommendations,  # ส่งกลับมา Top 3 เสมอ
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))