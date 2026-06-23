import streamlit as st
import pandas as pd
import numpy as np
import re

st.set_page_config(page_title="WooCommerce Product Generator", layout="wide")
st.title("🛒 WooCommerce Product Generator")

# -------------------------
# UPLOAD FILE
# -------------------------
file = st.file_uploader("Carica file CSV o Excel", type=["csv", "xlsx"])

# -------------------------
# UTILS
# -------------------------
def safe(val):
    if pd.isna(val):
        return ""
    return str(val).strip()

def clean_join(parts):
    return " ".join([p for p in parts if p and str(p).strip() != ""]).strip()

def clean_lower_tags(parts):
    seen = set()
    out = []
    for p in parts:
        if p:
            t = str(p).strip().lower()
            if t and t not in seen:
                seen.add(t)
                out.append(t)
    return ", ".join(out)

def extract_color_temp(text):
    if not text:
        return ""
    match = re.search(r"\d{3,5}K", str(text))
    return match.group(0) if match else ""

# -------------------------
# SHORT DESCRIPTION
# -------------------------
def build_short_desc(row):

    cat = safe(row["Categoria Articolo"])
    fam = safe(row["Famiglia Articolo"])
    color = safe(row["Colore Rosone"])
    fin = safe(row["Finitura"])
    mat = safe(row["Materiale"])
    att = safe(row["Attacco Portalampada"])

    watt = safe(row["Watt"])
    ip = safe(row["IP"])
    dimmer = safe(row.get("Dimmer", ""))
    luci = safe(row["Luci"])

    color_temp = extract_color_temp(row.get("Descrizione", ""))

    feat = ""

    if watt:
        feat = watt
    elif ip:
        feat = ip
    elif dimmer:
        feat = "dimmerabile"
    elif luci and luci != "0":
        feat = f"{luci} luci"

    if color_temp:
        feat = f"{feat} {color_temp}".strip()

    identity = color or fin or mat

    parts = [
        cat,
        fam,
        identity,
        f"con attacco {att}" if att else "",
        feat
    ]

    short = clean_join(parts)

    # Lampadina inclusa
    lamp = safe(row.get("LampadinaInclusa", "")).lower()
    if lamp in ["si", "sì", "yes"]:
        short += " lampadina inclusa"

    return short

# -------------------------
# DESCRIPTION (SEMPLIFICATA)
# -------------------------
def build_description(row):

    base = safe(row["Descrizione"])   # 🔥 SOLO DESCRIZIONE

    parts = [base]

    dim = safe(row["Dimensione Articolo"])
    att = safe(row["Attacco Portalampada"])
    volt = safe(row["Volt"])
    luci = safe(row["Luci"])
    mat = safe(row["Materiale"])
    fin = safe(row["Finitura"])
    ip = safe(row["IP"])
    classe = safe(row["Classe"])

    color_temp = extract_color_temp(row.get("Descrizione", ""))

    if dim:
        parts.append(f"di dimensioni {dim}")
    if att:
        parts.append(f"con attacco {att}")
    if volt:
        parts.append(f"compatibile con tensione {volt}")
    if luci:
        parts.append(f"numero luci {luci}")
    if mat:
        parts.append(f"realizzata in {mat}")
    if fin:
        parts.append(f"con finitura {fin}")
    if ip:
        parts.append(f"protezione IP {ip}")
    if classe:
        parts.append(f"Classe {classe}")

    if color_temp:
        parts.append(f"temperatura colore {color_temp}")

    lamp = safe(row.get("LampadinaInclusa", "")).lower()
    if lamp in ["si", "sì", "yes"]:
        parts.append("lampadina inclusa")

    return clean_join(parts)

# -------------------------
# TAGS
# -------------------------
def build_tags(row):
    return clean_lower_tags([
        row["Categoria Articolo"],
        row["Famiglia Articolo"],
        row["Gruppo Prodotto"],
        row["Materiale"],
        row["Finitura"],
        row["Colore Rosone"],
        row["Attacco Portalampada"],
        row["Watt"],
        row["IP"]
    ])

# -------------------------
# ATTRIBUTES
# -------------------------
def build_attributes(row):

    mapping = {
        "Attacco Portalampada": "Attacco",
        "Luci": "Luci",
        "Reattore": "Reattore",
        "Trasformatore": "Trasformatore",
        "Volt": "Volt",
        "Peso Netto": "Peso",
        "Peso Lordo": "Peso Lordo",
        "Watt": "Potenza",
        "IP": "IP",
        "Classe": "Classe energetica",
        "Materiale": "Materiale",
        "Finitura": "Finitura",
        "Colore Rosone": "Colore"
    }

    attrs = []
    i = 1

    for k, v in mapping.items():
        val = safe(row.get(k, ""))
        if val:
            attrs.append({
                f"Attribute {i} name": v,
                f"Attribute {i} value(s)": val,
                f"Attribute {i} visible": 1,
                f"Attribute {i} global": 1
            })
            i += 1

    # Temperatura colore
    color_temp = extract_color_temp(row.get("Descrizione", ""))
    if color_temp:
        attrs.append({
            f"Attribute {i} name": "Temperatura Colore",
            f"Attribute {i} value(s)": color_temp,
            f"Attribute {i} visible": 1,
            f"Attribute {i} global": 1
        })
        i += 1

    # Lampadina inclusa
    lamp = safe(row.get("LampadinaInclusa", "")).lower()
    if lamp in ["si", "sì", "yes"]:
        attrs.append({
            f"Attribute {i} name": "Lampadina inclusa",
            f"Attribute {i} value(s)": "Si",
            f"Attribute {i} visible": 1,
            f"Attribute {i} global": 1
        })

    return attrs

# -------------------------
# IMAGES
# -------------------------
def build_images(row):
    return safe(row["Indirizzo Immagine"])

# -------------------------
# PROCESS MAIN
# -------------------------
if file:

    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    st.write("📊 Anteprima dati")
    st.dataframe(df.head())

    output_rows = []

    for _, row in df.iterrows():

        sku = safe(row["Nr"])
        name = build_short_desc(row).title()

        short = build_short_desc(row)
        desc = build_description(row)
        tags = build_tags(row)
        img = build_images(row)

        # SHORT HTML + documenti
        short_html = short

        scheda = safe(row["Indirizzo Scheda Tecnica"])
        cert = safe(row["Indirizzo Certificazione"])

        if scheda or cert:
            short_html += "<br><b>Specifiche tecniche:</b><ul>"
            if scheda:
                short_html += f'<li><a href="{scheda}" target="_blank">Scheda tecnica prodotto</a></li>'
            if cert:
                short_html += f'<li><a href="{cert}" target="_blank">Scheda sicurezza</a></li>'
            short_html += "</ul>"

        base = {
            "SKU": sku,
            "Name": name,
            "Categories": safe(row["Categoria Articolo"]),
            "Tags": tags,
            "Short description": short_html,
            "Description": desc,
            "Stock": safe(row["Magazzino"]),
            "Images": img,
            "PREZZO_LISTINO": safe(row["Prezzo Al Pubblico"]),
            "PREZZO_IN_OFFERTA": ""
        }

        attrs = build_attributes(row)

        for a in attrs:
            base.update(a)

        output_rows.append(base)

    out_df = pd.DataFrame(output_rows)

    st.success("✔ CSV WooCommerce generato correttamente")

    st.dataframe(out_df.head())

    csv = out_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Scarica CSV WooCommerce",
        csv,
        "woocommerce_export.csv",
        "text/csv"
    )
