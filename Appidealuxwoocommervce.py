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
    """Concatena evitando vuoti e doppioni di spazi"""
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

def build_short_desc(row):
    cat = safe(row["Categoria Articolo"])
    fam = safe(row["Famiglia Articolo"])
    color = safe(row["Colore Rosone"])
    fin = safe(row["Finitura"])
    mat = safe(row["Materiale"])
    att = safe(row["Attacco Portalampada"])
    feat = ""

    # feature principale
    watt = safe(row["Watt"])
    ip = safe(row["IP"])
    dim = safe(row["Dimmer"])
    luci = safe(row["Luci"])

    if watt:
        feat = watt
    elif ip:
        feat = ip
    elif dim:
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

    return clean_join(parts)

def build_description(row):
    desc2 = safe(row["Descrizione 2"])
    desc = safe(row["Descrizione"])

    if desc2 == desc:
        base = desc2
    else:
        base = clean_join([desc2, desc])

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

    return attrs

def build_images(row):
    return safe(row["Indirizzo Immagine"])

def build_short_html_with_docs(row, short_text):
    scheda = safe(row["Indirizzo Scheda Tecnica"])
    cert = safe(row["Indirizzo Certificazione"])

    html = short_text

    if scheda or cert:
        html += "<br><b>Specifiche tecniche:</b><ul>"

        if scheda:
            html += f'<li><a href="{scheda}" target="_blank" rel="noopener">Scheda tecnica prodotto (PDF)</a></li>'
        if cert:
            html += f'<li><a href="{cert}" target="_blank" rel="noopener">Scheda sicurezza (PDF)</a></li>'

        html += "</ul>"

    return html


# -------------------------
# MAIN PROCESS
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

        if attrs:
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
