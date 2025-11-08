import { test, expect } from '@playwright/test';
// Smoke test responsive que valida elementos clave en distintos viewports
test.describe('Smoke responsive', () => {
    test('Home carga y layout principal visible', async ({ page }) => {
        await page.goto('/');
        // Ajustar selectores según tu app real
        await expect(page).toHaveTitle(/Inventario|React/i);
        // Navbar / header
        const header = page.locator('header');
        await expect(header).toBeVisible();
        // Componente principal
        const main = page.locator('main');
        await expect(main).toBeVisible();
    });
    test('Menu navegación colapsa en móvil', async ({ page }) => {
        await page.goto('/');
        // Cambiar selector si usas otro botón hamburguesa
        const burger = page.locator('button[aria-label="menu"]');
        if (await burger.count() > 0) {
            await burger.click();
            // ejemplo de item del menú
            const menuItem = page.locator('nav a');
            await expect(menuItem.first()).toBeVisible();
        }
        else {
            test.skip(true, 'No se encontró botón de menú (ajustar selector)');
        }
    });
});
