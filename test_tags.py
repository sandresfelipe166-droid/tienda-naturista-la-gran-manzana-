#!/usr/bin/env python3
"""
Test script to verify tag functionality in the FastAPI application.
This script tests that all routers have proper tags configured and
that the OpenAPI documentation correctly groups endpoints by tags.
"""

import json
from typing import Any, Dict, List

import requests
from fastapi.testclient import TestClient

from main import app


def test_openapi_tags():
    """Test that OpenAPI schema contains all expected tags."""
    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200

    openapi_schema = response.json()

    # Expected tags based on router configuration
    expected_tags = [
        {"name": "Authentication", "description": "Authentication endpoints"},
        {"name": "Inventory", "description": "Inventory management endpoints"},
        {"name": "Laboratorios", "description": "Laboratory management endpoints"},
        {"name": "Productos", "description": "Product management endpoints"},
        {"name": "Secciones", "description": "Section management endpoints"},
        {"name": "Users", "description": "User management endpoints"},
        {"name": "Alertas", "description": "Alert management endpoints"},
    ]

    # Check if tags are present in OpenAPI schema
    actual_tags = openapi_schema.get("tags", [])

    print("Expected tags:")
    for tag in expected_tags:
        print(f"  - {tag['name']}: {tag['description']}")

    print("\nActual tags found in OpenAPI schema:")
    for tag in actual_tags:
        print(f"  - {tag['name']}: {tag.get('description', 'No description')}")

    # Verify all expected tags are present
    expected_tag_names = {tag["name"] for tag in expected_tags}
    actual_tag_names = {tag["name"] for tag in actual_tags}

    missing_tags = expected_tag_names - actual_tag_names
    extra_tags = actual_tag_names - expected_tag_names

    if missing_tags:
        print(f"\n❌ Missing tags: {missing_tags}")
        return False
    else:
        print("\n✅ All expected tags are present!")

    if extra_tags:
        print(f"\nℹ️  Extra tags found: {extra_tags}")

    return True


def test_tag_grouping():
    """Test that endpoints are properly grouped by tags."""
    client = TestClient(app)

    # Get OpenAPI schema
    response = client.get("/openapi.json")
    assert response.status_code == 200

    openapi_schema = response.json()
    paths = openapi_schema.get("paths", {})

    # Group endpoints by tags
    tag_endpoints = {}
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if isinstance(operation, dict):
                tags = operation.get("tags", [])
                for tag in tags:
                    if tag not in tag_endpoints:
                        tag_endpoints[tag] = []
                    tag_endpoints[tag].append(f"{method.upper()} {path}")

    print("\nEndpoints grouped by tags:")
    for tag, endpoints in tag_endpoints.items():
        print(f"\n{tag}:")
        for endpoint in endpoints:
            print(f"  - {endpoint}")

    return tag_endpoints


def test_router_tags():
    """Test that routers have correct tags configured."""
    from app.api.v1.router import api_router
    from app.routers import alertas, auth, inventory, laboratorios, productos, secciones, users

    routers_to_check = [
        (auth.router, ["Authentication"]),
        (secciones.router, ["Secciones"]),
        (alertas.router, ["Alertas"]),
        (laboratorios.router, ["Laboratorios"]),
        (productos.router, ["Productos"]),
        (inventory.router, ["Inventory"]),
        (users.router, ["Users"]),
    ]

    print("\nChecking router tag configurations:")
    all_correct = True

    for router, expected_tags in routers_to_check:
        actual_tags = getattr(router, 'tags', [])
        if actual_tags == expected_tags:
            print(f"✅ {router.prefix or '/'} - Tags: {actual_tags}")
        else:
            print(f"❌ {router.prefix or '/'} - Expected: {expected_tags}, Got: {actual_tags}")
            all_correct = False

    return all_correct


def main():
    """Run all tag tests."""
    print("🧪 Testing Tag Functionality in FastAPI Application")
    print("=" * 60)

    try:
        # Test 1: OpenAPI tags
        print("\n1. Testing OpenAPI Tags...")
        tags_ok = test_openapi_tags()

        # Test 2: Tag grouping
        print("\n2. Testing Endpoint Grouping...")
        tag_endpoints = test_tag_grouping()

        # Test 3: Router tags
        print("\n3. Testing Router Configurations...")
        routers_ok = test_router_tags()

        # Summary
        print("\n" + "=" * 60)
        print("📊 Test Summary:")
        print(f"  OpenAPI Tags: {'✅ PASS' if tags_ok else '❌ FAIL'}")
        print(f"  Router Tags: {'✅ PASS' if routers_ok else '❌ FAIL'}")
        print(f"  Total Tags Found: {len(tag_endpoints)}")

        if tags_ok and routers_ok:
            print("\n🎉 All tag functionality tests passed!")
            return True
        else:
            print("\n⚠️  Some tag functionality tests failed.")
            return False

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
