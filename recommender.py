import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from database import get_db_connection

def get_recommendations_by_cuisine_and_ingredients(
    user_ingredients: list, target_cuisine: str
):
  """1. กรองข้อมูลจาก Turso Cloud เฉพาะ cuisine ที่ตรงกัน

  2. คำนวณ Cosine Similarity เทียบกับ user_ingredients 3. คืนค่า Top 3 เสมอ
  """
  conn = get_db_connection()

  # Query กรองตาม Cuisine (ใช้ LIKE เผื่อรูปแบบการเก็บข้อมูลในฐานข้อมูล)
  query = """
        SELECT * FROM recipes 
        WHERE cuisines LIKE ?
    """
  cursor = conn.execute(query, (f"%{target_cuisine}%",))
  rows = cursor.fetchall()
  column_names = [description[0] for description in cursor.description]
  conn.close()

  df = pd.DataFrame(rows, columns=column_names)

  # เผื่อกรณีที่หา Cuisine นั้นไม่เจอ ให้ลองค้นหาจากข้อมูลทั้งหมดแทนเพื่อไม่ให้แอปพัง
  if df.empty:
    conn = get_db_connection()
    cursor = conn.execute("SELECT * FROM recipes")
    rows = cursor.fetchall()
    column_names = [description[0] for description in cursor.description]
    conn.close()
    df = pd.DataFrame(rows, columns=column_names)

  if df.empty:
    return []

  # ทำความสะอาดข้อมูลส่วนผสมสำหรับทำ TF-IDF
  df["clean_ingredients"] = df["ingredients"].astype(str).str.lower()

  vectorizer = TfidfVectorizer(stop_words="english")
  recipe_matrix = vectorizer.fit_transform(df["clean_ingredients"])

  # แปลงส่วนผสมที่ผู้ใช้ส่งมาเป็น Vector
  user_query = " ".join(user_ingredients).lower()
  user_vector = vectorizer.transform([user_query])

  # คำนวณ Cosine Similarity
  scores = cosine_similarity(user_vector, recipe_matrix).flatten()
  df["similarity_score"] = scores

  # จัดอันดับเลือก Top 3 เสมอ
  top_recipes = df.sort_values(by="similarity_score", ascending=False).head(3)

  results = []
  for _, row in top_recipes.iterrows():
    ingredients_val = row["ingredients"]
    if isinstance(ingredients_val, str) and (
        ingredients_val.startswith("[") or ingredients_val.startswith("{")
    ):
      try:
        ingredients_val = json.loads(ingredients_val)
      except:
        pass

    steps_val = row["steps"] if "steps" in row else None
    if isinstance(steps_val, str) and (
        steps_val.startswith("[") or steps_val.startswith("{")
    ):
      try:
        steps_val = json.loads(steps_val)
      except:
        pass

    # เพิ่มการจัดการและดึงค่า ingredients_raw
    ingredients_raw_val = row.get("ingredients_raw") if "ingredients_raw" in row else None
    if isinstance(ingredients_raw_val, str) and (
        ingredients_raw_val.startswith("[") or ingredients_raw_val.startswith("{")
    ):
      try:
        ingredients_raw_val = json.loads(ingredients_raw_val)
      except:
        pass

    results.append({
        "name": row.get("name"),
        "ingredients": ingredients_val,
        "ingredients_raw": ingredients_raw_val,
        "steps": steps_val,
        "cuisines": row.get("cuisines"),
        "score": round(float(row["similarity_score"]), 4),
    })

  return results