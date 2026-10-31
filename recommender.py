import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

DB_PATH = "/data/recipes.db" if os.path.exists("/data") else "recipes.db"

def get_recommendations_by_cuisine(user_ingredients: list, target_cuisine: str, top_n: int = 3):
    """
    1. Query ข้อมูลจาก recipes.db เฉพาะ cuisine ที่ตรงกัน
    2. ทำ TF-IDF เฉพาะกลุ่มที่กรองมา
    3. คำนวณ Cosine Similarity เทียบกับ user_ingredients
    """
    # 1. เชื่อมต่อฐานข้อมูล SQLite และ Query เฉพาะ cuisine ที่ต้องการ
    # (ใช้ LIKE หรือเทียบตรงๆ ขึ้นอยู่กับการเก็บข้อมูลในตาราง cuisines)
    conn = sqlite3.connect(DB_PATH)
    
    # สมมติชื่อตารางคือ 'recipes' และคอลัมน์เก็บ cuisine ชื่อ 'cuisines'
    query = f"""
        SELECT name, ingredients, ingredients_raw, steps, servings, cuisines 
        FROM recipes 
        WHERE cuisines LIKE ?
    """
    # ค้นหาแบบกว้างๆ เผื่อเก็บเป็น Array string หรือ JSON ใน SQLite
    df = pd.read_sql_query(query, conn, params=(f"%{target_cuisine}%",))
    conn.close()

    if df.empty:
        return []

    # ทำความสะอาดข้อมูลคอลัมน์ ingredients ให้เป็น string ต่อกันด้วยช่องว่าง
    # สมมติใน DB เก็บเป็น string หรือ list ที่แปลงเป็น string แล้ว
    df['clean_ingredients'] = df['ingredients'].astype(str).str.lower()

    # 2. ทำ TF-IDF Vectorization เฉพาะกลุ่มข้อมูลที่ถูกกรองมาแล้ว (ประหยัดแรมมหาศาล)
    vectorizer = TfidfVectorizer(stop_words='english')
    recipe_matrix = vectorizer.fit_transform(df['clean_ingredients'])

    # 3. แปลง User Ingredients ให้เป็น Vector ชุดเดียวกัน
    user_query = " ".join(user_ingredients).lower()
    user_vector = vectorizer.transform([user_query])

    # 4. คำนวณ Cosine Similarity
    scores = cosine_similarity(user_vector, recipe_matrix).flatten()

    # 5. จัดอันดับ (Sorting) เลือก Top-N
    df['similarity_score'] = scores
    top_recipes = df.sort_values(by='similarity_score', ascending=False).head(top_n)

    # แปลงผลลัพธ์เป็น List ของ Dictionary เพื่อเตรียมส่งออกเป็น JSON
    results = []
    for _, row in top_recipes.iterrows():
        results.append({
            "name": row["name"],
            "ingredients": row["ingredients"],
            "ingredients_raw": row["ingredients_raw"],
            "steps": row["steps"],
            "servings": row["servings"],
            "cuisines": row["cuisines"],
            "score": round(float(row["similarity_score"]), 4)
        })

    return results