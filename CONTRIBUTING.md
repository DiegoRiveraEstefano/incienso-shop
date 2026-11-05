# Guía de Contribución (CONTRIBUTING)

## 1. Convención de Ramas
- `main`: Código listo para producción.
- `feat/<nombre>`: Nuevas características.
- `fix/<nombre>`: Corrección de errores.

## 2. Conventional Commits
- `feat: agregar pasarela de pagos con django-payments`
- `fix: corregir cálculo de envío en el carrito`
- `docs: actualizar documentación de unpoly`

## 3. Checklist Previo a PR
- [ ] `uv run pytest` pasa sin fallos.
- [ ] `uv run ruff check` pasa sin advertencias.
- [ ] `uv run djlint .` formatea correctamente las plantillas.
