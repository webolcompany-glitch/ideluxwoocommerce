import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="WooCommerce Product Generator", layout="wide")

st.title("🛒 WooCommerce Product Generator")

# -------------------------
# UPLOAD FILE
# -------------------------
file = st.file_uploader("Carica file CSV o Excel", type=["csv", "xlsx"])

# -------------------------
# FUNZIONI UTILI
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

# -------------------------
# DESCRIPTION LUNGA
# -------------------------
def build_description(row):

    base = safe(row["Gruppo Prodotto"])

    parts = [base]

    dim = safe(row["Dimensione Articolo"])
    att = safe(row["Attacco Portalampada"])
    volt = safe(row["Volt"])
    luci = safe(row["Luci"])
    mat = safe(row["Materiale"])
    fin = safe(row["Finitura"])
    ip = safe(row["IP"])
    classe = safe(row["Classe"])

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

    return clean_join(parts)

# -------------------------
# SHORT DESCRIPTION + PDF
# -------------------------
def build_short_html_with_docs(row, short_text):

    scheda = safe(row.get("Indirizzo Scheda Tecnica", ""))
    cert = safe(row.get("Indirizzo Certificazione", ""))

    html = short_text

    links = []

    if scheda:
        links.append(
            f'<li><a href="{scheda}" target="_blank" rel="noopener">Scheda tecnica (PDF)</a></li>'
        )

    if cert:
        links.append(
            f'<li><a href="{cert}" target="_blank" rel="noopener">Certificazione (PDF)</a></li>'
        )

    if links:
        html += "<br><br><b>Documentazione:</b><ul>"
        html += "".join(links)
        html += "</ul>"

    return html

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
# ATTRIBUTI WOOCOMMERCE
# -------------------------
def build_attributes(row):

    fields = [
        "Attacco Portalampada",
        "Luci",
        "Reattore",
        "Trasformatore",
        "Volt",
        "Peso Netto",
        "Peso Lordo",
        "Watt",
        "IP",
        "Classe",
        "Materiale",
        "Finitura",
        "Colore Rosone"
    ]

    attrs = []
    i = 1

    for field in fields:

        val = safe(row.get(field, ""))

        if val:
            attrs.append({
                f"Attribute {i} name": field,
                f"Attribute {i} value(s)": val,
                f"Attribute {i} visible": 1,
                f"Attribute {i} global": 0
            })
            i += 1

    return attrs

# -------------------------
# IMMAGINI
# -------------------------
def build_images(row):
    return safe(row["Indirizzo Immagine"])

# -------------------------
# MAIN
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
        name = build_description(row).title()

        short = build_description(row)
        desc = build_description(row)
        tags = build_tags(row)
        img = build_images(row)

        short_html = build_short_html_with_docs(row, short)

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

    st.success("✔ Generazione completata")

    st.dataframe(out_df.head())

    csv = out_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Scarica CSV WooCommerce",
        csv,
        "woocommerce_export.csv",
        "text/csv"
    )
