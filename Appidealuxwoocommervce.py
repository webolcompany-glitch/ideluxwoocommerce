import streamlit as st
import pandas as pd
import numpy as np
import re
import csv

st.set_page_config(page_title="WooCommerce Generator", layout="wide")
st.title("🛒 WooCommerce Product Generator")

file = st.file_uploader("Carica file CSV o Excel", type=["csv", "xlsx"])

# -------------------------
# UTILS
# -------------------------
def safe(val):
    if pd.isna(val):
        return ""
    return str(val).strip()

def clean_join(parts):
    return " ".join([p for p in parts if p]).strip()

def clean_lower_tags(parts):
    seen = set()
    out = []
    for p in parts:
        if p:
            t = str(p).strip().lower()
            if t not in seen:
                seen.add(t)
                out.append(t)
    return ", ".join(out)

def extract_color_temp(text):
    if not text:
        return ""
    m = re.search(r"\d{3,5}K", str(text))
    return m.group(0) if m else ""

# -------------------------
# BRAND
# -------------------------
BRAND = "Ideal Lux"

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

    feat = ""

    if watt:
        feat = watt
    elif ip:
        feat = ip
    elif dimmer:
        feat = "dimmerabile"
    elif luci and luci != "0":
        feat = f"{luci} luci"

    identity = color or fin or mat

    parts = [
        cat,
        fam,
        identity,
        f"con attacco {att}" if att else "",
        feat
    ]

    short = clean_join(parts)

    lamp = safe(row.get("LampadinaInclusa", "")).lower()
    if lamp in ["si", "sì", "yes"]:
        short += " lampadina inclusa"

    return short

# -------------------------
# DESCRIPTION TEXT
# -------------------------
def build_description_text(row):

    base = safe(row["Descrizione"])

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
# TABLE HTML
# -------------------------
def build_attributes_table(row):

    fields = [
        ("Dimensione Articolo", "Dimensione"),
        ("EAN", "EAN"),
        ("Pezzi Per Scatola", "Pezzi Per Scatola"),
        ("Attacco Portalampada", "Attacco"),
        ("Luci", "Luci"),
        ("Volt", "Volt"),
        ("Watt", "Watt"),
        ("IP", "IP"),
        ("Classe", "Classe"),
        ("Materiale", "Materiale"),
        ("Finitura", "Finitura"),
        ("Colore Rosone", "Colore Rosone")
    ]

    html = """
    <div style="margin-top:20px;">
    <h3 style="color:#333;">Descrizione tecnica</h3>
    <table style="width:100%;border-collapse:collapse;font-size:14px;color:#333;">
    """

    for k, label in fields:
        val = safe(row.get(k, ""))
        if val:
            html += f"""
            <tr style="border-bottom:1px solid #ddd;">
                <td style="padding:8px;background:#f5f5f5;font-weight:600;">{label}</td>
                <td style="padding:8px;">{val}</td>
            </tr>
            """

    html += "</table></div>"
    return html

# -------------------------
# FINAL DESCRIPTION HTML
# -------------------------
def build_description_html(row, text, table):

    img = safe(row["Indirizzo Immagine"])

    html = f"""
<div>

    <div style="border:1px solid #ddd;padding:15px;background:#f9f9f9;color:#333;border-radius:6px;margin-bottom:15px;">
        {text}
    </div>

    {"<div style='text-align:center;margin-bottom:15px;'><img src='" + img + "' style='max-width:700px;width:100%;border-radius:6px;border:1px solid #ddd;'></div>" if img else ""}

    {table}

</div>
"""
    return html

# -------------------------
# ATTRIBUTES
# -------------------------
def build_attributes(row):

    mapping = {
        "Attacco Portalampada": "Attacco",
        "Luci": "Luci",
        "Volt": "Volt",
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

    return attrs

# -------------------------
# MAIN
# -------------------------
if file:

    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)

    output = []

    for _, row in df.iterrows():

        sku = safe(row["Nr"])

        name = f"{BRAND} {build_short_desc(row)}".title()

        short = build_short_desc(row)
        desc_text = build_description_text(row)
        table = build_attributes_table(row)
        description = build_description_html(row, desc_text, table)

        short_html = short

        base = {
            "SKU": sku,
            "Name": name,
            "Categories": safe(row["Categoria Articolo"]),
            "Tags": clean_lower_tags([
                row["Categoria Articolo"],
                row["Famiglia Articolo"],
                row["Materiale"],
                row["Finitura"],
                row["Attacco Portalampada"]
            ]),
            "Short description": short_html,
            "Description": description,
            "Stock": safe(row["Magazzino"]),
            "Images": safe(row["Indirizzo Immagine"]),
            "PREZZO_LISTINO": safe(row["Prezzo Al Pubblico"]),
            "PREZZO_IN_OFFERTA": ""
        }

        attrs = build_attributes(row)
        for a in attrs:
            base.update(a)

        output.append(base)

    out_df = pd.DataFrame(output)

    # ORDINE COLONNE FISSO
    base_cols = [
        "SKU","Name","Categories","Tags","Short description",
        "Description","Stock","Images","PREZZO_LISTINO","PREZZO_IN_OFFERTA"
    ]

    attr_cols = [c for c in out_df.columns if c not in base_cols]

    out_df = out_df[base_cols + attr_cols]

    st.success("Export completato")

    st.dataframe(out_df.head())

    csv = out_df.to_csv(index=False, encoding="utf-8", quoting=csv.QUOTE_ALL)

    st.download_button(
        "📥 Scarica CSV WooCommerce",
        csv,
        "woocommerce_export.csv",
        "text/csv"
    )
