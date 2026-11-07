# Monitor del Mar Rojo

Prototipo de herramienta para el TFM del Máster en Análisis de Inteligencia (URJC).
Verifica con fuentes abiertas los ataques a buques reivindicados por los hutíes y estima el riesgo por perfil de buque.

> **Los datos incluidos son ficticios.** Sirven solo para enseñar cómo funciona la herramienta.

## Qué contiene

| Archivo | Qué es |
| --- | --- |
| `index.html` | El Monitor: mapa, fichas de cada incidente, estadísticas, calculadora de riesgo y lista de pendientes |
| `nombres.html` | Generador de variantes de nombres árabes, con significado y pronunciación |
| `data/incidentes.json` | Incidentes verificados (lo mantiene el analista) |
| `data/pendientes.json` | Lo que recoge el recolector cada día, pendiente de verificar |
| `data/modelo_riesgo.json` | Pesos de la calculadora de riesgo (provisionales) |
| `scripts/recolectar.py` | Recolector automático (Python, sin dependencias) |
| `scripts/fuentes.json` | Fuentes RSS y palabras clave del recolector |
| `.github/workflows/actualizar.yml` | Ejecuta el recolector cada día en GitHub |

## Publicarlo en GitHub Pages

1. Crea un repositorio nuevo en GitHub (puede ser privado si tu cuenta lo permite con Pages; si no, público).
2. Sube todo el contenido de esta carpeta, **incluida la carpeta oculta `.github`**.
3. En el repositorio: **Settings → Pages → Source: Deploy from a branch → `main` / `(root)`**. En un par de minutos tendrás la dirección de la web.
4. En **Settings → Actions → General → Workflow permissions**, marca **Read and write permissions** para que el recolector pueda guardar los pendientes.
5. Para probar el recolector sin esperar al día siguiente: **Actions → Recoger pendientes → Run workflow**.

## Uso diario (modelo semiautomático)

1. **La máquina recoge.** Cada día a las 05:17 UTC el recolector revisa las fuentes y añade a *Pendientes de verificar* lo que parece un incidente.
2. **El analista verifica.** En la pestaña *Pendientes*, pulsa *Verificar*, contrasta con AIS, satélite y avisos oficiales, rellena el formulario y pulsa *Generar ficha*.
3. **Publicar.** Copia la ficha generada y pégala dentro de la lista `incidentes` de `data/incidentes.json` (desde la web de GitHub o la app del móvil: lápiz → pegar → *Commit*). La web se actualiza sola en uno o dos minutos. Actualiza también el campo `actualizado`.

## Mantenimiento

- Si una fuente cambia su dirección RSS, el recolector lo indica en el registro de Actions y sigue con las demás. Corrige la dirección en `scripts/fuentes.json`.
- Los pesos de `data/modelo_riesgo.json` son provisionales: en el TFM se calibrarán con los incidentes verificados.

## Límites y criterios éticos

- **La verificación siempre la hace una persona.** El recolector solo propone.
- **No se recogen canales de grupos armados.** Sus comunicados se toman de prensa y de archivos de investigación.
- **Datos de terceros:** respeta las licencias (por ejemplo, ACLED no permite republicar sus datos en abierto).
- Muchos buques apagan el AIS en la zona; la verificación se complementa con radar por satélite (Sentinel-1).
