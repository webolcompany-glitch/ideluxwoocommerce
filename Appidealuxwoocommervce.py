import streamlit as st
import pandas as pd
import re
import csv
import html

st.set_page_config(page_title="WooCommerce Generator", layout="wide")
st.title("🛒 WooCommerce Product Generator")

file = st.file_uploader("Carica file CSV o Excel", type=["csv", "xlsx"])

BRAND = "Ideal Lux"

# -------------------------
# UTILS
# -------------------------
def safe(val):
    if pd.isna(val):
        return ""
    return str(val).strip()

def clean_join(parts):
    return " ".join([p for p in parts if p]).strip()

def extract_color_temp(text):
    if not text:
        return ""
    m = re.search(r"\d{3,5}K", str(text))
    return m.group(0) if m else ""

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
    elif luci:
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

    if safe(row.get("LampadinaInclusa", "")).lower() in ["si", "sì", "yes"]:
        short += " lampadina inclusa"

    return short

# -------------------------
# DESCRIPTION TEXT
# -------------------------
def build_description_text(row):

    base = safe(row["Descrizione"])
    parts = [base]

    if row.get("Dimensione Articolo"):
        parts.append(f"di dimensioni {safe(row['Dimensione Articolo'])}")
    if row.get("Attacco Portalampada"):
        parts.append(f"con attacco {safe(row['Attacco Portalampada'])}")
    if row.get("Volt"):
        parts.append(f"compatibile con tensione {safe(row['Volt'])}")
    if row.get("Luci"):
        parts.append(f"numero luci {safe(row['Luci'])}")
    if row.get("Materiale"):
        parts.append(f"realizzata in {safe(row['Materiale'])}")
    if row.get("Finitura"):
        parts.append(f"con finitura {safe(row['Finitura'])}")
    if row.get("IP"):
        parts.append(f"protezione IP {safe(row['IP'])}")
    if row.get("Classe"):
        parts.append(f"Classe {safe(row['Classe'])}")

    if safe(row.get("LampadinaInclusa", "")).lower() in ["si", "sì", "yes"]:
        parts.append("lampadina inclusa")

    return clean_join(parts)

# -------------------------
# TABLE HTML (SAFE)
# -------------------------
def build_table(row):

    fields = [
        ("Dimensione Articolo", "Dimensione"),
        ("EAN", "EAN"),
        ("Pezzi Per Scatola", "Pezzi"),
        ("Attacco Portalampada", "Attacco"),
        ("Luci", "Luci"),
        ("Volt", "Volt"),
        ("Watt", "Watt"),
        ("IP", "IP"),
        ("Classe", "Classe"),
        ("Materiale", "Materiale"),
        ("Finitura", "Finitura"),
        ("Colore Rosone", "Colore")
    ]

    html_table = """
    <div style="margin-top:20px;">
    <h3 style="color:#333;font-size:15px;">Descrizione tecnica</h3>
    <table style="width:100%;border-collapse:collapse;font-size:14px;color:#333;">
    """

    for k, label in fields:
        val = safe(row.get(k, ""))
        if val:
            html_table += f"""
            <tr style="border-bottom:1px solid #e5e5e5;">
                <td style="padding:8px;background:#f5f5f5;font-weight:600;width:40%">{label}</td>
                <td style="padding:8px;">{html.escape(val)}</td>
            </tr>
            """

    html_table += "</table></div>"
    return html_table

# -------------------------
# FINAL DESCRIPTION (ANTI BREAK CSV)
# -------------------------
def build_description(row):

    text = build_description_text(row)
    table = build_table(row)
    img = safe(row.get("Indirizzo Immagine", ""))

    html_desc = f"""<div style="font-family:Arial;color:#333;">

<div style="border:1px solid #ddd;padding:15px;background:#f9f9f9;border-radius:6px;margin-bottom:15px;">
{text}
</div>

{f'<div style="text-align:center;margin-bottom:15px;"><img src="{img}" style="max-width:700px;width:100%;border-radius:6px;border:1px solid #ddd;"></div>' if img else ""}

{table}

</div>"""

    return html_desc

# -------------------------
# TAGS
# -------------------------
def build_tags(row):
    return ", ".join(filter(None, [
        safe(row.get("Categoria Articolo")),
        safe(row.get("Famiglia Articolo")),
        safe(row.get("Materiale")),
        safe(row.get("Finitura")),
        safe(row.get("Attacco Portalampada"))
    ]))

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
        "Classe": "Classe",
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

    rows = []

    for _, row in df.iterrows():

        sku = safe(row["Nr"])
        name = f"{BRAND} {build_short_desc(row)}".title()

        description = build_description(row)
        short = build_short_desc(row)

        base = {
            "SKU": sku,
            "Name": name,
            "Categories": safe(row["Categoria Articolo"]),
            "Tags": build_tags(row),
            "Short description": short,
            "Description": description,
            "Stock": safe(row["Magazzino"]),
            "Images": safe(row["Indirizzo Immagine"]),
            "PREZZO_LISTINO": safe(row["Prezzo Al Pubblico"]),
            "PREZZO_IN_OFFERTA": ""
        }

        attrs = build_attributes(row)
        for a in attrs:
            base.update(a)

        rows.append(base)

    out_df = pd.DataFrame(rows)

    # ordine colonne fisso (IMPORTANTE)
    base_cols = [
        "SKU","Name","Categories","Tags","Short description",
        "Description","Stock","Images","PREZZO_LISTINO","PREZZO_IN_OFFERTA"
    ]

    attr_cols = [c for c in out_df.columns if c not in base_cols]

    out_df = out_df[base_cols + attr_cols]

    st.success("Export completato")

    st.dataframe(out_df.head())

    csv = out_df.to_csv(
        index=False,
        encoding="utf-8",
        quoting=csv.QUOTE_ALL
    )

    st.download_button(
        "📥 Scarica CSV WooCommerce",
        csv,
        "woocommerce_export.csv",
        "text/csv"
    )
