# from fastapi import FastAPI, Depends
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from database import get_db, create_tables
# from models import Ingredient, Recipe
# from ai import generate_recipe
# import random

# app = FastAPI()
# # asyncio.run(create_tables())
# # Get surplus ingredients & suggest recipes
# # @app.get("/suggest_recipe/")
# # async def suggest_recipe(db: AsyncSession = Depends(get_db)):
# #     result = await db.execute(select(Ingredient).filter(Ingredient.quantity > 0))
# #     ingredients = result.scalars().all()
# #     ingredient_names = [ing.name for ing in ingredients]

# #     recipe = generate_recipe(ingredient_names)

# #     return {"suggested_recipe": recipe}
# @app.get("/suggest_recipe/")
# async def suggest_recipe(db: AsyncSession = Depends(get_db)):
#     await create_tables()
#     # Fetch available ingredients
#     result = await db.execute(select(Ingredient).filter(Ingredient.quantity > 0))
#     ingredients = result.scalars().all()
    
#     # Extract ingredient names
#     ingredient_names = [ing.name for ing in ingredients]
    
#     # Select 3 to 5 random ingredients
#     if len(ingredient_names) > 5:
#         ingredient_names = random.sample(ingredient_names, random.randint(3, 5))
    
#     # Generate recipe using AI
#     recipe_text = generate_recipe(ingredient_names)
    
#     # Example: Splitting AI-generated response into name & instructions (modify as needed)
#     recipe_name = f"Special Dish with {' & '.join(ingredient_names)}"
#     instructions = recipe_text.strip()

#     # Estimate cost (sum of selected ingredient costs)
#     estimated_cost = sum(ing.price_per_unit for ing in ingredients if ing.name in ingredient_names)
    
#     # Save to database
#     new_recipe = Recipe(
#         name=recipe_name,
#         ingredients=", ".join(ingredient_names),  # Store as comma-separated names
#         instructions=instructions,
#         estimated_cost=estimated_cost
#     )
#     db.add(new_recipe)
#     await db.commit()
    
#     return {"suggested_recipe": recipe_name, "instructions": instructions, "estimated_cost": estimated_cost}


# # Add a new ingredient
# @app.post("/add_ingredient/")
# async def add_ingredient(name: str, quantity: float, unit: str, price_per_unit: float, db: AsyncSession = Depends(get_db)):
#     new_ingredient = Ingredient(name=name, quantity=quantity, unit=unit, price_per_unit=price_per_unit)
#     db.add(new_ingredient)
#     await db.commit()
#     return {"message": "Ingredient added successfully"}

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from database import get_db, create_tables
from models import Ingredient, Recipe
from ai import generate_recipe
import random
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.on_event("startup")
async def startup_event():
    await create_tables()  # Ensure tables are created when the app starts

# ✅ Fetch all ingredients
@app.get("/ingredients/")
async def get_ingredients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ingredient))
    ingredients = result.scalars().all()
    return ingredients

# ✅ Fetch all recipes
@app.get("/recipes/")
async def get_recipes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Recipe))
    recipes = result.scalars().all()
    return recipes

# ✅ Suggest a new recipe using AI
@app.get("/suggest_recipe/")
async def suggest_recipe(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ingredient).filter(Ingredient.quantity > 0))
    ingredients = result.scalars().all()
    
    ingredient_names = [ing.name for ing in ingredients]
    
    if len(ingredient_names) > 5:
        ingredient_names = random.sample(ingredient_names, random.randint(3, 5))

    recipe_text = generate_recipe(ingredient_names)

    recipe_name = f"Special Dish with {' & '.join(ingredient_names)}"
    instructions = recipe_text.strip()

    estimated_cost = sum(ing.price_per_unit for ing in ingredients if ing.name in ingredient_names)

    new_recipe = Recipe(
        name=recipe_name,
        ingredients=", ".join(ingredient_names),
        instructions=instructions,
        estimated_cost=estimated_cost
    )
    db.add(new_recipe)
    await db.commit()
    
    return {
    "suggested_recipe": recipe_name,  # String
    "instructions": instructions,     # String
    "estimated_cost": estimated_cost  # Float
}

# ✅ Add a new ingredient
@app.post("/add_ingredient/")
async def add_ingredient(name: str, quantity: float, unit: str, price_per_unit: float, db: AsyncSession = Depends(get_db)):
    new_ingredient = Ingredient(name=name, quantity=quantity, unit=unit, price_per_unit=price_per_unit)
    db.add(new_ingredient)
    await db.commit()
    return {"message": "Ingredient added successfully"}

# ✅ Delete an ingredient
@app.delete("/delete_ingredient/{ingredient_id}")
async def delete_ingredient(ingredient_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Ingredient).filter(Ingredient.id == ingredient_id))
        ingredient = result.scalar_one()
        await db.delete(ingredient)
        await db.commit()
        return {"message": "Ingredient deleted successfully"}
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Ingredient not found")

# ✅ Delete a recipe
@app.delete("/delete_recipe/{recipe_id}")
async def delete_recipe(recipe_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Recipe).filter(Recipe.id == recipe_id))
        recipe = result.scalar_one()
        await db.delete(recipe)
        await db.commit()
        return {"message": "Recipe deleted successfully"}
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Recipe not found")
