# Guía de Diseño y UI/UX (DESING)

Este documento describe la identidad visual, paleta cromática y lineamientos de experiencia de usuario en **Incienso Shop**.

---

## 1. Identidad Visual & Paleta de Colores

La atmósfera de Incienso Shop evoca serenidad, misticismo y conexión con la naturaleza botánica:

| Color | Hex | Uso en UI |
| :--- | :--- | :--- |
| **Ámbar Incienso** | `#d97706` | Acentos primarios, botones de acción (`.btn-warning`), llamada a la acción. |
| **Sándalo & Terracota**| `#78350f` / `#9a3412` | Maderas nobles, encabezados y detalles de tierra. |
| **Humo & Carbón** | `#1c1917` / `#292524` | Fondos de navbar y footer (`bg-dark`), textos principales. |
| **Salvia & Hierbas** | `#065f46` | Estados de éxito, stock disponible e insumos herbales. |
| **Lino & Ceniza Clara**| `#f8fafc` / `#ffffff` | Fondo general (`bg-light`), tarjetas de producto limpias. |

---

## 2. Badges de Familias Aromáticas

Cada producto cuenta con una insignia distintiva gestionada por `<incienso-aroma-badge>`:

- **Resinas**: Fondo crema cálido con icono `bi-gem`.
- **Maderas**: Fondo naranja tierra con icono `bi-tree`.
- **Florales**: Fondo rosa lavanda suave con icono `bi-flower1`.
- **Herbales**: Fondo verde salvia con icono `bi-droplet-half`.
- **Especiados**: Fondo terracota suave con icono `bi-fire`.
- **Cítricos**: Fondo lima luminoso con icono `bi-sun`.

---

## 3. Experiencia Reactiva & Carrito

- **Navegación SPA Ininterrumpida**: Unpoly permite cambiar entre el catálogo, filtros y detalles de producto sin parpadeos de recarga completa.
- **Micro-interacciones en Carrito**: Al pulsar "Agregar al Carrito", el badge superior se incrementa asíncronamente mediante `up-submit` sin perder la posición del scroll.
