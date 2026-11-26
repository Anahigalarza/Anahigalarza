# Legado Constructora — Sistema operativo de obras

## Cómo usarlo
Habla con Claude en esta sesión y sube lo que tengas. El residente deriva a cada agente:

| Quieres… | Dile algo como… | Agente |
|---|---|---|
| Registrar gastos | "Te subo 5 facturas de la obra Casa Pérez" | contador-obra |
| Saber cuánto queda | "¿Cuánto llevamos gastado en Casa Pérez?" | contador-obra |
| Plan de mañana | "¿Qué llevamos mañana a la obra?" | planificador-obra |
| Cronograma | "Arma el cronograma de la losa del 2do piso" | secretario |
| Duda técnica | "¿Este armado de columna está bien?" + foto | residente-obra |
| Proforma nueva | "Haz la proforma para ampliación de 60 m²" | presupuestos |
| Pedir precios | "Arma la solicitud de cotización de hierro y cemento" | compras-proveedores |
| Redes | "Haz el antes y después de esta obra" | redes-sociales |
| Facturar / SRI | "Prepara la factura de la proforma 1047" | contabilidad-sri |

## Estructura
- `obras/` — una carpeta por obra (copiar `_PLANTILLA_OBRA`)
- `proformas/` — modelos, emitidas y pedidos a proveedores
- `precios/` — base de precios histórica
- `redes/` — calendario y publicaciones
- `empresa/` — equipo y datos de la empresa
- `.claude/agents/` — definición de cada agente
