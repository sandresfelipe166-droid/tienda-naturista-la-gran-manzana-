#!/usr/bin/env python3
"""
Simple test to verify tag functionality without dealing with middleware issues.
"""

import os

from app.routers import alertas, auth, inventory, laboratorios, productos, secciones, users


def test_router_tags():
    """Test that routers have correct tags configured."""
    print("🧪 Testing Router Tag Configurations")
    print("=" * 50)

    routers_to_check = [
        (auth.router, ["Authentication"]),
        (secciones.router, ["Secciones"]),
        (alertas.router, ["Alertas"]),
        (laboratorios.router, ["Laboratorios"]),
        (productos.router, ["Productos"]),
        (inventory.router, ["Inventory"]),
        (users.router, ["Users"]),
    ]

    all_correct = True

    for router, expected_tags in routers_to_check:
        actual_tags = getattr(router, 'tags', [])
        prefix = getattr(router, 'prefix', '/')
        if actual_tags == expected_tags:
            print(f"✅ {prefix} - Tags: {actual_tags}")
        else:
            print(f"❌ {prefix} - Expected: {expected_tags}, Got: {actual_tags}")
            all_correct = False

    print("\n" + "=" * 50)
    if all_correct:
        print("🎉 All router tags are correctly configured!")
        return True
    else:
        print("⚠️  Some router tags are incorrect.")
        return False


def test_tag_functionality():
    """Test basic tag functionality by checking router attributes."""
    print("\n📋 Tag Functionality Summary:")
    print("=" * 50)

    routers = [auth, secciones, alertas, laboratorios, productos, inventory, users]
    total_routers = len(routers)

    routers_with_tags = 0
    for router in routers:
        tags = getattr(router.router, 'tags', [])
        if tags:
            routers_with_tags += 1
            print(f"  {getattr(router.router, 'prefix', '/')} -> {tags}")

    print(f"\n📊 Summary: {routers_with_tags}/{total_routers} routers have tags configured")

    if routers_with_tags == total_routers:
        print("✅ All routers have tags configured!")
        return True
    else:
        print("⚠️  Some routers are missing tags.")
        return False


def main():
    """Run all simple tag tests."""
    print("🔍 Simple Tag Functionality Test")
    print("=" * 50)

    router_test = test_router_tags()
    functionality_test = test_tag_functionality()

    print("\n" + "=" * 50)
    print("📋 Final Results:")
    print(f"  Router Tags: {'✅ PASS' if router_test else '❌ FAIL'}")
    print(f"  Tag Functionality: {'✅ PASS' if functionality_test else '❌ FAIL'}")

    if router_test and functionality_test:
        print("\n🎉 All tag functionality tests passed!")
        return True
    else:
        print("\n⚠️  Some tag functionality tests failed.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
