import json

import pytest
from fastapi.testclient import TestClient

from mealie.schema.openai.recipe import (
    OpenAIRecipe,
    OpenAIRecipeIngredient,
    OpenAIRecipeInstruction,
    OpenAIRecipeNotes,
)
from mealie.services.openai import OpenAIService
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser

def test_openai_create_recipe_from_text(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    unique_user: TestUser,
):
    # Mock OpenAI response
    async def mock_get_response(self, prompt: str, message: str, *args, **kwargs) -> str | None:
        data = OpenAIRecipe(
            name=random_string(),
            description=random_string(),
            recipe_yield=random_string(),
            total_time=random_string(),
            prep_time=random_string(),
            perform_time=random_string(),
            ingredients=[OpenAIRecipeIngredient(text=random_string()) for _ in range(random_int(5, 10))],
            instructions=[OpenAIRecipeInstruction(text=random_string()) for _ in range(1, random_int(5, 10))],
            notes=[OpenAIRecipeNotes(text=random_string()) for _ in range(random_int(2, 5))],
        )
        return data.model_dump_json()

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    # Test basic recipe creation from text
    recipe_text = "Test recipe with some ingredients and instructions"
    r = api_client.post(
        api_routes.recipes_create_from_text,
        data={"text": recipe_text},
        headers=unique_user.token,
    )
    assert r.status_code == 201

    # Verify recipe was created
    slug: str = json.loads(r.text)
    r = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token)
    assert r.status_code == 200

def test_openai_create_recipe_from_text_with_translation(
    api_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    unique_user: TestUser,
):
    # Mock OpenAI response with translated content
    async def mock_get_response(self, prompt: str, message: str, *args, **kwargs) -> str | None:
        # Check if translation is requested in the message
        is_spanish = "translate the recipe to Spanish" in message

        data = OpenAIRecipe(
            name="Paella" if is_spanish else "Seafood Rice",
            description="Delicioso arroz con mariscos" if is_spanish else "Delicious rice with seafood",
            recipe_yield="4 porciones" if is_spanish else "4 servings",
            total_time="1 hora" if is_spanish else "1 hour",
            prep_time="20 minutos" if is_spanish else "20 minutes",
            perform_time="40 minutos" if is_spanish else "40 minutes",
            ingredients=[
                OpenAIRecipeIngredient(text="Arroz" if is_spanish else "Rice"),
                OpenAIRecipeIngredient(text="Mariscos" if is_spanish else "Seafood"),
            ],
            instructions=[
                OpenAIRecipeInstruction(text="Cocinar el arroz" if is_spanish else "Cook the rice"),
                OpenAIRecipeInstruction(text="Añadir mariscos" if is_spanish else "Add seafood"),
            ],
            notes=[OpenAIRecipeNotes(text="Servir caliente" if is_spanish else "Serve hot")],
        )
        return data.model_dump_json()

    monkeypatch.setattr(OpenAIService, "get_response", mock_get_response)

    # Test recipe creation with translation
    recipe_text = "Test recipe for translation"
    r = api_client.post(
        f"{api_routes.recipes_create_from_text}?translateLanguage=Spanish",
        data={"text": recipe_text},
        headers=unique_user.token,
    )
    assert r.status_code == 201

    # Verify recipe was created with translated content
    slug: str = json.loads(r.text)
    r = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token)
    assert r.status_code == 200
    recipe_data = r.json()
    assert "Paella" in recipe_data["name"]
    assert "porciones" in recipe_data["recipeYield"]
