#!/usr/bin/env python3
"""
Script de prueba para el sistema de recuperación de contraseña
Ejecutar: python scripts/test_password_reset_flow.py
"""

import requests  # type: ignore[import-not-found]
import json
import time
from typing import Optional

BASE_URL = "http://localhost:8000/api/v1"

# Colores para output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text: str):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text:^60}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def print_success(text: str):
    print(f"{GREEN}✅ {text}{RESET}")


def print_error(text: str):
    print(f"{RED}❌ {text}{RESET}")


def print_info(text: str):
    print(f"{YELLOW}ℹ️  {text}{RESET}")


def print_step(step: int, text: str):
    print(f"{BLUE}[Paso {step}]{RESET} {text}")


def test_request_password_reset(email: str) -> Optional[str]:
    """Solicitar código de recuperación"""
    print_step(1, f"Solicitando código para: {email}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/reset-password-request",
            json={"email": email},
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            if "codigo" in data:
                print_success(f"Código recibido: {data['codigo']}")
                return data["codigo"]
            else:
                print_info("Código no devuelto (probablemente SMTP configurado)")
                return None
        else:
            print_error(f"Error: {data.get('detail', 'Unknown error')}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_error(f"Error de conexión: {e}")
        return None


def test_confirm_password_reset(
    email: str, 
    codigo: str, 
    new_password: str
) -> bool:
    """Confirmar cambio de contraseña"""
    print_step(2, f"Confirmando cambio de contraseña para: {email}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/reset-password-confirm",
            json={
                "email": email,
                "codigo": codigo,
                "new_password": new_password
            },
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            print_success("Contraseña cambiada exitosamente")
            return True
        else:
            print_error(f"Error: {data.get('detail', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Error de conexión: {e}")
        return False


def test_invalid_code(email: str) -> bool:
    """Probar con código inválido"""
    print_step(2, "Probando con código inválido")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/reset-password-confirm",
            json={
                "email": email,
                "codigo": "999999",
                "new_password": "newPassword123"
            },
            timeout=10
        )
        
        print(f"   Status Code: {response.status_code}")
        data = response.json()
        
        if response.status_code == 400:
            print_success("Correctamente rechazado código inválido")
            return True
        else:
            print_error(f"Debería retornar 400, recibió: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Error de conexión: {e}")
        return False


def test_brute_force_protection(email: str) -> bool:
    """Probar protección contra fuerza bruta"""
    print_step(3, "Probando protección contra intentos fallidos")
    
    failed_attempts = 0
    max_attempts = 6  # Después de 5 intentos, debe bloquearse
    
    for i in range(max_attempts):
        try:
            response = requests.post(
                f"{BASE_URL}/auth/reset-password-confirm",
                json={
                    "email": email,
                    "codigo": "000000",
                    "new_password": "testPassword123"
                },
                timeout=10
            )
            
            if response.status_code == 400:
                failed_attempts += 1
                print(f"   Intento {i+1}: Código rechazado (400)")
            elif response.status_code == 429:
                print_success(f"Usuario bloqueado después de {failed_attempts} intentos fallidos")
                return True
            
        except requests.exceptions.RequestException as e:
            print_error(f"Error en intento {i+1}: {e}")
            return False
    
    print_error("No se activó el bloqueo por intentos fallidos")
    return False


def main():
    print_header("PRUEBAS DEL SISTEMA DE RECUPERACIÓN DE CONTRASEÑA")
    
    # Email de prueba (cambiar si es necesario)
    test_email = "admin@example.com"
    test_password = "TestPassword123"
    
    print_info(f"Email de prueba: {test_email}")
    print_info(f"Nueva contraseña: {test_password}")
    
    # Test 1: Solicitar código
    print_header("Test 1: Solicitar Código de Recuperación")
    codigo = test_request_password_reset(test_email)
    
    if not codigo:
        print_error("No se pudo obtener el código. Verifica que el email exista.")
        print_info("Intenta crear un usuario de prueba primero:")
        print_info('  curl -X POST http://localhost:8000/api/v1/auth/register \\')
        print_info('    -H "Content-Type: application/json" \\')
        print_info('    -d \'{"username":"admin","email":"admin@example.com","password":"admin123","nombre_completo":"Admin User","rol_id":1}\'')
        return
    
    # Test 2: Confirmar con código válido
    print_header("Test 2: Confirmar con Código Válido")
    if test_confirm_password_reset(test_email, codigo, test_password):
        print_success("✨ Flujo normal completado exitosamente")
    else:
        print_error("Falló la confirmación")
        return
    
    # Test 3: Solicitar nuevo código
    print_header("Test 3: Solicitar Nuevo Código (después de cambio exitoso)")
    nuevo_codigo = test_request_password_reset(test_email)
    
    # Test 4: Código inválido
    print_header("Test 4: Validación de Seguridad - Código Inválido")
    if test_invalid_code(test_email):
        print_success("✨ Validación de código inválido funcionando")
    else:
        print_error("Error en validación")
    
    # Test 5: Protección contra fuerza bruta
    print_header("Test 5: Protección contra Fuerza Bruta")
    if test_brute_force_protection(test_email):
        print_success("✨ Protección contra fuerza bruta activa")
    else:
        print_error("Error en protección")
    
    print_header("RESUMEN DE PRUEBAS")
    print_success("Todos los tests completados. Revisa los resultados arriba.")
    print_info("Para pruebas completas, también verifica:")
    print_info("  - Validaciones de email en frontend")
    print_info("  - Validaciones de contraseña en frontend")
    print_info("  - Estilos de mensajes de error/éxito")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Pruebas interrumpidas por el usuario{RESET}")
    except Exception as e:
        print(f"{RED}Error inesperado: {e}{RESET}")
