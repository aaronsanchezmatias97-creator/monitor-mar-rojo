"""Recolector diario del Monitor del Mar Rojo.

Lee los canales RSS configurados en scripts/fuentes.json, se queda con las noticias
que contienen palabras clave (en inglés y en árabe) y las añade a data/pendientes.json
para que el analista las verifique. No publica nada en el mapa por sí mismo.

Solo usa la biblioteca estándar de Python. Se ejecuta con GitHub Actions
(.github/workflows/actualizar.yml) o a mano:  python scripts/recolectar.py
"""
import hashlib
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = RAIZ / "scripts" / "fuentes.json"
SALIDA = RAIZ / "data" / "pendientes.json"
MAX_PENDIENTES = 300


def descargar(url):
    req = urllib.request.Request(url, headers={"User-Agent": "MonitorMarRojo/1.0 (investigacion academica)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def fecha_iso(texto):
    if not texto:
        return datetime.now(timezone.utc).date().isoformat()
    try:
        return parsedate_to_datetime(texto).date().isoformat()
    except Exception:
        m = re.match(r"\d{4}-\d{2}-\d{2}", texto)
        return m.group(0) if m else datetime.now(timezone.utc).date().isoformat()


def leer_rss(fuente):
    raiz = ET.fromstring(descargar(fuente["url"]))
    items = raiz.findall(".//item") or raiz.findall(".//{http://www.w3.org/2005/Atom}entry")
    for it in items:
        def txt(tag):
            el = it.find(tag)
            if el is None:
                el = it.find("{http://www.w3.org/2005/Atom}" + tag)
            return (el.text or "").strip() if el is not None and el.text else ""
        enlace = txt("link")
        if not enlace:
            el = it.find("{http://www.w3.org/2005/Atom}link")
            enlace = el.get("href", "") if el is not None else ""
        yield {
            "titulo": re.sub(r"\s+", " ", txt("title")),
            "resumen": re.sub(r"<[^>]+>", " ", txt("description") or txt("summary"))[:500],
            "enlace": enlace,
            "fecha": fecha_iso(txt("pubDate") or txt("updated") or txt("published")),
        }


def main():
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    claves = [c.lower() for c in cfg["palabras_clave"]]
    datos = json.loads(SALIDA.read_text(encoding="utf-8")) if SALIDA.exists() else {"pendientes": []}
    # Los ejemplos ficticios se eliminan en cuanto entra el primer dato real.
    pend = [p for p in datos.get("pendientes", []) if not p["id"].startswith("P-ejemplo")]
    vistos = {p["id"] for p in pend}
    nuevos = 0
    for fuente in cfg["fuentes"]:
        try:
            for n in leer_rss(fuente):
                texto = (n["titulo"] + " " + n["resumen"]).lower()
                if not any(c in texto for c in claves):
                    continue
                pid = hashlib.sha1((n["enlace"] or n["titulo"]).encode("utf-8")).hexdigest()[:12]
                if pid in vistos:
                    continue
                vistos.add(pid)
                pend.append({"id": pid, "fecha": n["fecha"], "fuente": fuente["nombre"],
                             "titulo": n["titulo"], "enlace": n["enlace"]})
                nuevos += 1
        except Exception as e:  # una fuente caída no detiene a las demás
            print(f"[aviso] {fuente['nombre']}: {e}")
    pend.sort(key=lambda p: p["fecha"], reverse=True)
    salida = {"aviso": "Recogido automáticamente. Pendiente de verificación por el analista.",
              "actualizado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "pendientes": pend[:MAX_PENDIENTES]}
    SALIDA.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{nuevos} elementos nuevos; {len(salida['pendientes'])} pendientes en total.")


if __name__ == "__main__":
    main()
