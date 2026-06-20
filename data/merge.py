"""
Lee los dos datasets desde data/ y los integra mediante merge por country + year.
Genera: data/merged.csv

Requisito previo: colocar los archivos CSV en la carpeta data/ antes de ejecutar.
    data/owid-energy-data.csv
    data/global-data-on-sustainable-energy.csv

Uso:
    python data/merge.py
"""

import os
import pandas as pd

# ─── Rutas locales ────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # carpeta data/

PATH_OWID   = os.path.join(BASE_DIR, "owid-energy-data.csv")
PATH_KAGGLE = os.path.join(BASE_DIR, "global-data-on-sustainable-energy.csv")
PATH_MERGED = os.path.join(BASE_DIR, "merged.csv")


# ─── Carga y limpieza de OWID ────────────────────────────────────────────────

def load_owid(path: str) -> pd.DataFrame:
    """
    Carga el dataset OWID y selecciona las columnas relevantes para el TB4.
    Solo se conservan filas de países (se excluyen agregados regionales
    que no tienen iso_code o cuyo nombre contiene paréntesis).
    """
    df = pd.read_csv(path, low_memory=False)

    # Filtrar filas que sean países reales (tienen iso_code y no son agregados)
    df = df[df["iso_code"].notna()].copy()
    df = df[~df["iso_code"].str.startswith("OWID", na=False)].copy()

    cols_owid = [
        "country", "year", "iso_code", "population", "gdp",
        # Energía per cápita y consumo
        "energy_per_capita",          # P5, P9
        "primary_energy_consumption",
        "fossil_fuel_consumption",
        "fossil_share_energy",        # P4
        # Electricidad por fuente (P6)
        "coal_electricity",
        "gas_electricity",
        "nuclear_electricity",
        "solar_electricity",
        "wind_electricity",
        "hydro_electricity",
        "oil_electricity",
        "biofuel_electricity",
        "other_renewable_electricity",
        # Shares eléctricas (útil para mix %)
        "coal_share_elec",
        "gas_share_elec",
        "nuclear_share_elec",
        "solar_share_elec",
        "wind_share_elec",
        "hydro_share_elec",
        # Intensidad de carbono (P2, P7)
        "carbon_intensity_elec",
        # Renovables (P1, P3, P8)
        "renewables_share_energy",
        "renewables_electricity",
    ]

    # Conservar solo columnas existentes (versiones del CSV pueden variar)
    cols_owid = [c for c in cols_owid if c in df.columns]
    df = df[cols_owid].copy()

    # Renombrar para consistencia
    df.rename(columns={"country": "country", "year": "year"}, inplace=True)
    return df


# ─── Carga y limpieza de Kaggle ──────────────────────────────────────────────

def load_kaggle(path: str) -> pd.DataFrame:
    """
    Carga el dataset de Kaggle y renombra columnas a nombres cortos y sin espacios.
    Cubre 2000–2020.
    """
    df = pd.read_csv(path, low_memory=False)

    rename_map = {
        "Entity":                                             "country",
        "Year":                                               "year",
        "Access to electricity (% of population)":           "access_to_electricity",
        "Access to clean fuels for cooking":                  "access_clean_fuels",
        "Renewable-electricity-generating-capacity-per-capita": "renew_elec_cap_per_capita",
        "Financial flows to developing countries (US $)":    "financial_flows_usd",
        "Renewable energy share in the total final energy consumption (%)":
                                                              "renewable_share_total_energy",
        "Electricity from fossil fuels (TWh)":               "elec_from_fossil_twh",
        "Electricity from nuclear (TWh)":                    "elec_from_nuclear_twh",
        "Electricity from renewables (TWh)":                 "elec_from_renewables_twh",
        "Low-carbon electricity (% electricity)":            "low_carbon_elec_pct",
        "Primary energy consumption per capita (kWh/person)":"primary_energy_per_capita_kwh",
        "Energy intensity level of primary energy (MJ/$2017 PPP GDP)":
                                                              "energy_intensity_primary",
        "Value_co2_emissions_kt_by_country":                 "co2_emissions_kt",
        "Renewables (% equivalent primary energy)":          "renewables_pct_primary",
        "gdp_growth":                                        "gdp_growth",
        "gdp_per_capita":                                    "gdp_per_capita",
        "Density\\n(P/Km2)":                                 "population_density",
        "Land Area(Km2)":                                    "land_area_km2",
        "Latitude":                                          "latitude",
        "Longitude":                                         "longitude",
    }

    df.rename(columns=rename_map, inplace=True)

    # Conservar solo columnas que existan después del rename
    keep = [v for v in rename_map.values() if v in df.columns]
    df = df[keep].copy()

    return df


# ─── Asignación de región ─────────────────────────────────────────────────────

REGION_MAP = {
    # América Latina y el Caribe
    "Argentina": "América Latina", "Bolivia": "América Latina",
    "Brazil": "América Latina", "Chile": "América Latina",
    "Colombia": "América Latina", "Costa Rica": "América Latina",
    "Cuba": "América Latina", "Dominican Republic": "América Latina",
    "Ecuador": "América Latina", "El Salvador": "América Latina",
    "Guatemala": "América Latina", "Haiti": "América Latina",
    "Honduras": "América Latina", "Jamaica": "América Latina",
    "Mexico": "América Latina", "Nicaragua": "América Latina",
    "Panama": "América Latina", "Paraguay": "América Latina",
    "Peru": "América Latina", "Trinidad and Tobago": "América Latina",
    "Uruguay": "América Latina", "Venezuela": "América Latina",
    "Belize": "América Latina", "Guyana": "América Latina",
    "Suriname": "América Latina",
    # Europa
    "Albania": "Europa", "Austria": "Europa", "Belgium": "Europa",
    "Bulgaria": "Europa", "Croatia": "Europa", "Cyprus": "Europa",
    "Czech Republic": "Europa", "Czechia": "Europa", "Denmark": "Europa",
    "Estonia": "Europa", "Finland": "Europa", "France": "Europa",
    "Germany": "Europa", "Greece": "Europa", "Hungary": "Europa",
    "Iceland": "Europa", "Ireland": "Europa", "Italy": "Europa",
    "Latvia": "Europa", "Lithuania": "Europa", "Luxembourg": "Europa",
    "Malta": "Europa", "Netherlands": "Europa", "Norway": "Europa",
    "Poland": "Europa", "Portugal": "Europa", "Romania": "Europa",
    "Serbia": "Europa", "Slovakia": "Europa", "Slovenia": "Europa",
    "Spain": "Europa", "Sweden": "Europa", "Switzerland": "Europa",
    "Ukraine": "Europa", "United Kingdom": "Europa",
    "Bosnia and Herzegovina": "Europa", "North Macedonia": "Europa",
    "Moldova": "Europa", "Belarus": "Europa",
    # América del Norte
    "Canada": "América del Norte", "United States": "América del Norte",
    # Asia Oriental y Pacífico
    "Australia": "Asia-Pacífico", "China": "Asia-Pacífico",
    "Japan": "Asia-Pacífico", "South Korea": "Asia-Pacífico",
    "New Zealand": "Asia-Pacífico", "Indonesia": "Asia-Pacífico",
    "Malaysia": "Asia-Pacífico", "Philippines": "Asia-Pacífico",
    "Thailand": "Asia-Pacífico", "Vietnam": "Asia-Pacífico",
    "Myanmar": "Asia-Pacífico", "Cambodia": "Asia-Pacífico",
    "Laos": "Asia-Pacífico", "Mongolia": "Asia-Pacífico",
    "Papua New Guinea": "Asia-Pacífico", "Singapore": "Asia-Pacífico",
    "Taiwan": "Asia-Pacífico", "Timor": "Asia-Pacífico",
    # Asia del Sur
    "Bangladesh": "Asia del Sur", "India": "Asia del Sur",
    "Nepal": "Asia del Sur", "Pakistan": "Asia del Sur",
    "Sri Lanka": "Asia del Sur", "Afghanistan": "Asia del Sur",
    "Bhutan": "Asia del Sur", "Maldives": "Asia del Sur",
    # Medio Oriente y Norte de África
    "Algeria": "Medio Oriente y N. África",
    "Egypt": "Medio Oriente y N. África",
    "Iran": "Medio Oriente y N. África",
    "Iraq": "Medio Oriente y N. África",
    "Jordan": "Medio Oriente y N. África",
    "Kuwait": "Medio Oriente y N. África",
    "Lebanon": "Medio Oriente y N. África",
    "Libya": "Medio Oriente y N. África",
    "Morocco": "Medio Oriente y N. África",
    "Oman": "Medio Oriente y N. África",
    "Qatar": "Medio Oriente y N. África",
    "Saudi Arabia": "Medio Oriente y N. África",
    "Syria": "Medio Oriente y N. África",
    "Tunisia": "Medio Oriente y N. África",
    "Turkey": "Medio Oriente y N. África",
    "United Arab Emirates": "Medio Oriente y N. África",
    "Yemen": "Medio Oriente y N. África",
    "Israel": "Medio Oriente y N. África",
    "Bahrain": "Medio Oriente y N. África",
    # África Subsahariana
    "Angola": "África Subsahariana", "Cameroon": "África Subsahariana",
    "Cote d'Ivoire": "África Subsahariana", "Democratic Republic of Congo": "África Subsahariana",
    "Ethiopia": "África Subsahariana", "Ghana": "África Subsahariana",
    "Kenya": "África Subsahariana", "Mozambique": "África Subsahariana",
    "Nigeria": "África Subsahariana", "Senegal": "África Subsahariana",
    "South Africa": "África Subsahariana", "Sudan": "África Subsahariana",
    "Tanzania": "África Subsahariana", "Uganda": "África Subsahariana",
    "Zambia": "África Subsahariana", "Zimbabwe": "África Subsahariana",
    "Rwanda": "África Subsahariana", "Mali": "África Subsahariana",
    "Niger": "África Subsahariana", "Burkina Faso": "África Subsahariana",
    "Malawi": "África Subsahariana", "Botswana": "África Subsahariana",
    "Namibia": "África Subsahariana", "Madagascar": "África Subsahariana",
    "Somalia": "África Subsahariana",
    # Asia Central
    "Kazakhstan": "Asia Central", "Uzbekistan": "Asia Central",
    "Turkmenistan": "Asia Central", "Kyrgyzstan": "Asia Central",
    "Tajikistan": "Asia Central", "Azerbaijan": "Asia Central",
    "Georgia": "Asia Central", "Armenia": "Asia Central",
    "Russia": "Asia Central",
}


def assign_region(df: pd.DataFrame) -> pd.DataFrame:
    df["region"] = df["country"].map(REGION_MAP).fillna("Otras regiones")
    return df


# ─── Merge principal ──────────────────────────────────────────────────────────

def build_merged(owid: pd.DataFrame, kaggle: pd.DataFrame) -> pd.DataFrame:
    """
    Left join de OWID (dataset completo) con Kaggle (2000–2020).
    La clave es country + year.
    Se mantienen todos los registros OWID; las columnas Kaggle
    se rellenan con NaN fuera del rango 2000–2020.
    """
    # Evitar duplicar columnas que existen en ambos (gdp_per_capita puede estar en OWID via gdp/pop)
    kaggle_only_cols = [c for c in kaggle.columns if c not in ["country", "year"]
                        and c not in owid.columns]
    kaggle_slim = kaggle[["country", "year"] + kaggle_only_cols].copy()

    merged = owid.merge(kaggle_slim, on=["country", "year"], how="left")

    # Si gdp_per_capita vino de Kaggle, derivar también desde OWID cuando sea posible
    if "gdp_per_capita" not in owid.columns and "gdp" in owid.columns and "population" in owid.columns:
        mask = merged["gdp_per_capita"].isna()
        merged.loc[mask, "gdp_per_capita"] = (
            merged.loc[mask, "gdp"] / merged.loc[mask, "population"]
        )

    merged = assign_region(merged)
    return merged


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("\n── TB4 · merge.py ──────────────────────────────")

    # 1. Verificar que los archivos existen
    print("\n[1] Verificando archivos en data/ …")
    for path in [PATH_OWID, PATH_KAGGLE]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"No se encontró: {path}\n"
                "Asegúrate de colocar ambos CSV en la carpeta data/ antes de ejecutar merge.py"
            )
        print(f"  [OK] {os.path.basename(path)}")

    # 2. Cargar
    print("\n[2] Cargando datasets …")
    owid   = load_owid(PATH_OWID)
    kaggle = load_kaggle(PATH_KAGGLE)
    print(f"  OWID:   {owid.shape[0]:,} filas × {owid.shape[1]} cols")
    print(f"  Kaggle: {kaggle.shape[0]:,} filas × {kaggle.shape[1]} cols")

    # 3. Merge
    print("\n[3] Fusionando por country + year …")
    merged = build_merged(owid, kaggle)
    print(f"  Merged: {merged.shape[0]:,} filas × {merged.shape[1]} cols")

    # 4. Guardar
    merged.to_csv(PATH_MERGED, index=False)
    print(f"\n[4] Guardado → {PATH_MERGED}")

    # 5. Reporte rápido de cobertura
    print("\n── Cobertura del merged (2000–2020) ────────────")
    sub = merged[(merged["year"] >= 2000) & (merged["year"] <= 2020)]
    print(f"  Países únicos : {sub['country'].nunique()}")
    print(f"  Años           : {sub['year'].min()} – {sub['year'].max()}")
    key_cols = [
        "carbon_intensity_elec", "renewables_share_energy",
        "renewable_share_total_energy", "access_to_electricity",
        "energy_per_capita", "gdp_per_capita",
    ]
    for col in key_cols:
        if col in merged.columns:
            pct = sub[col].notna().mean() * 100
            print(f"  {col:<38}: {pct:.1f}% no-nulo")
    print("────────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()