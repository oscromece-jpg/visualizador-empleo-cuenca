import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os

# Configuración de página
st.set_page_config(
    page_title="Visualizador SAE Empleo Cuenca",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo visual moderno y limpio
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1F4E78;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #555555;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #1F4E78;
    }
    .metric-label {
        font-size: 0.82rem;
        color: #64748B;
        text-transform: uppercase;
        font-weight: 600;
    }
    .ficha-card {
        background-color: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.04);
    }
    .ficha-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1F4E78;
        border-bottom: 2px solid #2B579A;
        padding-bottom: 6px;
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)

# 1. Cargar Base de Datos y Cartografía GeoJSON
@st.cache_data(show_spinner=False)
def load_data(cache_version="v2.3"):
    candidates = [
        "Visualizador_Cuenca/data/base_visualizador_empleo_cuenca.parquet",
        "data/base_visualizador_empleo_cuenca.parquet",
        "SAE_Empleo_Cuenca/03_resultados/base_visualizador_empleo_cuenca.parquet",
        "base_visualizador_empleo_cuenca.parquet"
    ]
    path_data = next((c for c in candidates if os.path.exists(c)), None)
    if not path_data:
        # Fallback a CSV si no existe parquet
        csv_candidates = [
            "Visualizador_Cuenca/data/base_visualizador_empleo_cuenca.csv",
            "data/base_visualizador_empleo_cuenca.csv",
            "SAE_Empleo_Cuenca/03_resultados/base_visualizador_empleo_cuenca.csv",
            "base_visualizador_empleo_cuenca.csv"
        ]
        path_data = next((c for c in csv_candidates if os.path.exists(c)), None)
        df = pd.read_csv(path_data, dtype={
            'id_sector': str,
            'codigo_canton': str,
            'codigo_parroquia': str,
            'zona': str,
            'sector': str,
            'codigo_categoria': str
        })
    else:
        df = pd.read_parquet(path_data)
        df['id_sector'] = df['id_sector'].astype(str).str.zfill(12)
        df['codigo_categoria'] = df['codigo_categoria'].astype(str)
    
    # Garantizar compatibilidad y defensividad en columnas de calidad
    if 'calidad_tasa' not in df.columns:
        if 'calidad_estimacion' in df.columns:
            df['calidad_tasa'] = df['calidad_estimacion']
        else:
            df['calidad_tasa'] = 'Confiable (CV < 15%)'
            
    if 'calidad_personas' not in df.columns:
        if 'calidad_estimacion' in df.columns:
            df['calidad_personas'] = df['calidad_estimacion']
        else:
            df['calidad_personas'] = 'Confiable (CV < 15%)'

    # Columna territorial unificada (nombre parroquial urbano o rural específico)
    df['parroquia_territorial'] = np.where(
        df['area'] == 'Urbana',
        df['parroquia_detalle'],
        df['parroquia']
    )
    return df

@st.cache_data
def load_geojson():
    candidates = [
        "Visualizador_Cuenca/cuenca_sectores.geojson",
        "cuenca_sectores.geojson",
        "data/cuenca_sectores.geojson"
    ]
    geojson_path = next((c for c in candidates if os.path.exists(c)), None)
    if not geojson_path:
        return None
    with open(geojson_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

@st.cache_data
def compute_centroids(geojson_data):
    if not geojson_data:
        return {}
    centroids = {}
    for feat in geojson_data['features']:
        sec = feat['properties']['id_sector']
        coords = feat['geometry']['coordinates']
        lons, lats = [], []
        def extract_pts(c):
            if isinstance(c[0], (int, float)):
                lons.append(c[0])
                lats.append(c[1])
            else:
                for sub in c:
                    extract_pts(sub)
        extract_pts(coords)
        if lons and lats:
            centroids[sec] = (sum(lats)/len(lats), sum(lons)/len(lons))
    return centroids

df_raw = load_data()
geojson_cuenca = load_geojson()
sector_centroids = compute_centroids(geojson_cuenca)

# Título y encabezado
st.markdown('<div class="main-title">🗺️ Visualizador Espacial y Estadístico de Empleo y Demografía a Nivel de Sector Censal</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title"><b>Cantón Cuenca</b> | Metodología Small Area Estimation (SAE Unit-Level) y Logit-Benchmarking con ENEMDU 2025</div>', unsafe_allow_html=True)

# 2. Barra Lateral de Filtros (Sidebar)
st.sidebar.header("🔍 Filtros de Consulta")

# Dimensión
dimensiones = list(df_raw['dimension'].unique())
dim_seleccionada = st.sidebar.selectbox("1. Dimensión Analítica:", dimensiones, index=0)

# Categoría dependiente de la dimensión
df_dim = df_raw[df_raw['dimension'] == dim_seleccionada]
categorias_disponibles = list(df_dim['categoria_label'].unique())

# Preselección lógica para la categoría
index_cat = 0
if "Empleo Adecuado/Pleno" in categorias_disponibles:
    index_cat = categorias_disponibles.index("Empleo Adecuado/Pleno")
elif "Población Total" in categorias_disponibles:
    index_cat = categorias_disponibles.index("Población Total")
elif "Superior universitario" in categorias_disponibles:
    index_cat = categorias_disponibles.index("Superior universitario")

cat_seleccionada = st.sidebar.selectbox("2. Categoría / Indicador:", categorias_disponibles, index=index_cat)

st.sidebar.markdown("---")

# Filtros Territoriales Dinámicos en Cascada
areas = ["Todas", "Urbana", "Rural"]
area_sel = st.sidebar.selectbox("3. Área:", areas, index=0)

# Las parroquias mostradas se filtran de forma ESTRICTA según el área seleccionada
if area_sel == "Urbana":
    df_area_filtrada = df_raw[df_raw['area'] == "Urbana"]
    parroquias_disponibles = ["Todas (Área Urbana)"] + sorted(list(df_area_filtrada['parroquia_territorial'].dropna().unique()))
elif area_sel == "Rural":
    df_area_filtrada = df_raw[df_raw['area'] == "Rural"]
    parroquias_disponibles = ["Todas (Área Rural)"] + sorted(list(df_area_filtrada['parroquia_territorial'].dropna().unique()))
else:
    parroquias_disponibles = ["Todas"] + sorted(list(df_raw['parroquia_territorial'].dropna().unique()))

parroquia_sel = st.sidebar.selectbox(
    "4. Parroquia:",
    parroquias_disponibles,
    index=0,
    key=f"parroquia_sel_{area_sel}"  # Resetea automáticamente la selección al cambiar de área
)

# Filtrar datos de la dimensión y categoría seleccionada
df_filtrado = df_raw[
    (df_raw['dimension'] == dim_seleccionada) &
    (df_raw['categoria_label'] == cat_seleccionada)
].copy()

if area_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado['area'] == area_sel]

if not parroquia_sel.startswith("Todas"):
    df_filtrado = df_filtrado[df_filtrado['parroquia_territorial'] == parroquia_sel]

# Determinar base de referencia / denominador (PEA vs Población Total)
if dim_seleccionada == 'Grupo de Edad (Demografía)':
    df_denom = df_raw[
        (df_raw['dimension'] == 'Grupo de Edad (Demografía)') &
        (df_raw['codigo_categoria'] == 'POB_TOTAL')
    ].copy()
    label_denom_kpi = "Población Total Proyectada"
    sub_denom_kpi = "Universo demográfico territorial"
    label_tasa = "% sobre Población Total" if cat_seleccionada != "Población Total" else "% Total"
else:
    df_denom = df_raw[
        (df_raw['dimension'] == 'Condición de Actividad (Mercado Laboral)') &
        (df_raw['codigo_categoria'] == 'PEA')
    ].copy()
    label_denom_kpi = "PEA Total Proyectada"
    sub_denom_kpi = "Universo laboral territorial"
    label_tasa = "% sobre la PEA"

if area_sel != "Todas":
    df_denom = df_denom[df_denom['area'] == area_sel]

if not parroquia_sel.startswith("Todas"):
    df_denom = df_denom[df_denom['parroquia_territorial'] == parroquia_sel]

# 3. Métricas Principales (KPIs)
total_denom_sel = df_denom['personas_proyectadas_2025'].sum()
total_cat_sel = df_filtrado['personas_proyectadas_2025'].sum()
tasa_promedio = (total_cat_sel / total_denom_sel * 100.0) if total_denom_sel > 0 else 0.0
n_sectores = df_filtrado['id_sector'].nunique()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Personas Proyectadas (2025)</div>
        <div class="metric-value">{total_cat_sel:,.0f}</div>
        <div style="font-size: 0.8rem; color: #888;">{cat_seleccionada}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label_tasa}</div>
        <div class="metric-value">{tasa_promedio:.2f}%</div>
        <div style="font-size: 0.8rem; color: #888;">Promedio territorial ponderado</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label_denom_kpi}</div>
        <div class="metric-value">{total_denom_sel:,.0f}</div>
        <div style="font-size: 0.8rem; color: #888;">{sub_denom_kpi}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Sectores Censales</div>
        <div class="metric-value">{n_sectores:,}</div>
        <div style="font-size: 0.8rem; color: #1F4E78; font-weight: 600;">Estimación Sintética Calibrada</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 4. Pestañas de Visualización
tab_mapa, tab_parroquia, tab_dimension, tab_tabla, tab_ficha = st.tabs([
    "🗺️ Mapa Cartográfico de Sectores Censales",
    "📈 Análisis Territorial por Parroquia",
    "📊 Composición de la Dimensión",
    "📋 Explorador de Sectores",
    "📄 Ficha Técnica Metodológica"
])

# -------------------------------------------------------------
# TAB 1: MAPA CARTOGRÁFICO DE SECTORES CENSALES
# -------------------------------------------------------------
with tab_mapa:
    if geojson_cuenca is None:
        st.error("No se encontró el archivo cartográfico 'Visualizador_Cuenca/cuenca_sectores.geojson'.")
    elif len(df_filtrado) == 0:
        st.warning("No se encontraron sectores censales para la combinación seleccionada.")
    else:
        # Controles superiores del mapa
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1.5, 1, 1])
        with col_ctrl1:
            variable_mapa = st.radio(
                "Variable para colorear sectores censales:",
                [f"Porcentaje ({label_tasa})", "Personas Proyectadas (2025)"],
                horizontal=True
            )
        with col_ctrl2:
            paleta_color = st.selectbox(
                "Paleta cromática:",
                ["Viridis", "Blues", "Teal", "Plasma", "Turbo", "YlOrRd"],
                index=0
            )
        with col_ctrl3:
            estilo_mapa = st.selectbox(
                "Estilo de mapa base:",
                ["carto-positron", "open-street-map", "carto-darkmatter"],
                index=0
            )

        col_var = 'porcentaje_sobre_pea' if "Porcentaje" in variable_mapa else 'personas_proyectadas_2025'
        label_var_cb = label_tasa if col_var == 'porcentaje_sobre_pea' else 'Personas 2025'

        # Calcular centro y zoom dinámico
        sub_sectores = df_filtrado['id_sector'].tolist()
        sub_pts = [sector_centroids[s] for s in sub_sectores if s in sector_centroids]
        
        if sub_pts and not parroquia_sel.startswith("Todas"):
            center_lat = float(np.mean([p[0] for p in sub_pts]))
            center_lon = float(np.mean([p[1] for p in sub_pts]))
            zoom_level = 12.3
        elif area_sel == "Urbana":
            center_lat = -2.8974
            center_lon = -79.0045
            zoom_level = 11.5
        elif area_sel == "Rural":
            center_lat = -2.8500
            center_lon = -79.1500
            zoom_level = 9.8
        else:
            center_lat = -2.8974
            center_lon = -79.0200
            zoom_level = 10.2

        # Configuración defensiva de hover y etiquetas
        hover_dict = {
            'parroquia_territorial': True,
            'area': True,
            'personas_proyectadas_2025': ':.0f',
            'porcentaje_sobre_pea': ':.2f',
        }
        labels_dict = {
            'id_sector': 'Sector Censal',
            'porcentaje_sobre_pea': label_tasa,
            'personas_proyectadas_2025': 'Personas (2025)',
            'parroquia_territorial': 'Parroquia',
            'area': 'Área',
        }
        if 'calidad_tasa' in df_filtrado.columns:
            hover_dict['calidad_tasa'] = True
            labels_dict['calidad_tasa'] = 'Calidad Tasa (%)'
        if 'calidad_personas' in df_filtrado.columns:
            hover_dict['calidad_personas'] = True
            labels_dict['calidad_personas'] = 'Calidad Personas'
        elif 'calidad_estimacion' in df_filtrado.columns:
            hover_dict['calidad_estimacion'] = True
            labels_dict['calidad_estimacion'] = 'Calidad'

        # Generar mapa con Plotly Express
        fig_map = px.choropleth_map(
            df_filtrado,
            geojson=geojson_cuenca,
            locations='id_sector',
            featureidkey='properties.id_sector',
            color=col_var,
            color_continuous_scale=paleta_color,
            map_style=estilo_mapa,
            zoom=zoom_level,
            center={'lat': center_lat, 'lon': center_lon},
            opacity=0.78,
            hover_name='id_sector',
            hover_data=hover_dict,
            labels=labels_dict
        )
        fig_map.update_layout(
            margin=dict(l=0, r=0, t=10, b=10),
            height=680,
            coloraxis_colorbar=dict(
                title=dict(text=label_var_cb, font=dict(size=12)),
                ticksuffix="%" if col_var == 'porcentaje_sobre_pea' else "",
                thickness=16,
                len=0.75
            )
        )
        st.plotly_chart(fig_map, use_container_width=True)
        st.caption(f"💡 <b>Pasa el cursor sobre cualquier sector censal</b> para ver su identificador de 12 dígitos, parroquia, personas estimadas y tasa. Mostrando {len(df_filtrado):,} sectores censales en pantalla.")

# -------------------------------------------------------------
# TAB 2: ANÁLISIS TERRITORIAL POR PARROQUIA
# -------------------------------------------------------------
with tab_parroquia:
    df_parr_cat = df_filtrado.groupby('parroquia_territorial')['personas_proyectadas_2025'].sum().reset_index()
    df_parr_denom = df_denom.groupby('parroquia_territorial')['personas_proyectadas_2025'].sum().reset_index()
    df_parr = pd.merge(df_parr_cat, df_parr_denom, on='parroquia_territorial', suffixes=('_cat', '_denom'))
    df_parr['tasa_pct'] = (df_parr['personas_proyectadas_2025_cat'] / df_parr['personas_proyectadas_2025_denom']) * 100.0
    df_parr = df_parr.sort_values(by='tasa_pct', ascending=True)

    fig_bar = px.bar(
        df_parr,
        x='tasa_pct',
        y='parroquia_territorial',
        orientation='h',
        title=f"Porcentaje de <b>{cat_seleccionada}</b> por Parroquia ({label_tasa})",
        labels={'tasa_pct': label_tasa, 'parroquia_territorial': 'Parroquia'},
        color='tasa_pct',
        color_continuous_scale='Blues',
        text_auto='.1f'
    )
    altura_grafico = max(450, len(df_parr) * 25)
    fig_bar.update_layout(height=altura_grafico, margin=dict(l=10, r=20, t=40, b=20))
    st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------------------------------------
# TAB 3: COMPOSICIÓN DE LA DIMENSIÓN
# -------------------------------------------------------------
with tab_dimension:
    df_dim_total = df_raw[df_raw['dimension'] == dim_seleccionada].copy()
    if area_sel != "Todas":
        df_dim_total = df_dim_total[df_dim_total['area'] == area_sel]
    if not parroquia_sel.startswith("Todas"):
        df_dim_total = df_dim_total[df_dim_total['parroquia_territorial'] == parroquia_sel]

    # Excluir la categoría totalizadora (PEA en actividad o Población Total en demografía)
    df_pie_data = df_dim_total[~df_dim_total['codigo_categoria'].isin(['PEA', 'POB_TOTAL'])].groupby('categoria_label')['personas_proyectadas_2025'].sum().reset_index()
    
    col_chart1, col_chart2 = st.columns([1, 1])
    
    with col_chart1:
        fig_pie = px.pie(
            df_pie_data,
            values='personas_proyectadas_2025',
            names='categoria_label',
            title=f"Distribución de <b>{dim_seleccionada}</b>",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_chart2:
        fig_hist = px.histogram(
            df_filtrado,
            x='porcentaje_sobre_pea',
            nbins=35,
            title=f"Distribución de <b>{cat_seleccionada}</b> en los Sectores Filtrados",
            labels={'porcentaje_sobre_pea': f'% ({label_tasa})'},
            color_discrete_sequence=['#1F4E78']
        )
        fig_hist.update_layout(yaxis_title="Cantidad de Sectores Censales", margin=dict(l=10, r=20, t=40, b=20))
        st.plotly_chart(fig_hist, use_container_width=True)

# -------------------------------------------------------------
# TAB 4: EXPLORADOR DE SECTORES Y DESCARGA
# -------------------------------------------------------------
with tab_tabla:
    st.subheader(f"Listado Detallado de Sectores Censales ({n_sectores:,} sectores)")
    
    cols_tabla = [
        'id_sector', 'parroquia_territorial', 'area', 'zona', 'sector',
        'personas_proyectadas_2025', 'porcentaje_sobre_pea', 'personas_censo_2022'
    ]
    rename_dict = {
        'id_sector': 'ID Sector (12 dígitos)',
        'parroquia_territorial': 'Parroquia',
        'area': 'Área',
        'zona': 'Zona',
        'sector': 'Sector',
        'personas_proyectadas_2025': f"Personas {cat_seleccionada} (2025)",
        'porcentaje_sobre_pea': label_tasa,
        'personas_censo_2022': 'Recuento Censo 2022',
    }
    if 'calidad_tasa' in df_filtrado.columns:
        cols_tabla.append('calidad_tasa')
        rename_dict['calidad_tasa'] = 'Calidad Tasa (%)'
    if 'calidad_personas' in df_filtrado.columns:
        cols_tabla.append('calidad_personas')
        rename_dict['calidad_personas'] = 'Calidad Personas'
    elif 'calidad_estimacion' in df_filtrado.columns:
        cols_tabla.append('calidad_estimacion')
        rename_dict['calidad_estimacion'] = 'Calidad'

    col_personas_label = f"Personas {cat_seleccionada} (2025)"
    df_mostrar = df_filtrado[cols_tabla].rename(columns=rename_dict)
    
    # Formatear recuentos de personas como enteros (sin decimales) para mayor claridad visual
    if col_personas_label in df_mostrar.columns:
        df_mostrar[col_personas_label] = df_mostrar[col_personas_label].fillna(0).round(0).astype(int)
    if 'Recuento Censo 2022' in df_mostrar.columns:
        df_mostrar['Recuento Censo 2022'] = df_mostrar['Recuento Censo 2022'].fillna(0).round(0).astype(int)
    if label_tasa in df_mostrar.columns:
        df_mostrar[label_tasa] = df_mostrar[label_tasa].round(2)

    st.dataframe(
        df_mostrar,
        use_container_width=True,
        hide_index=True,
        column_config={
            col_personas_label: st.column_config.NumberColumn(format="%d"),
            'Recuento Censo 2022': st.column_config.NumberColumn(format="%d"),
            label_tasa: st.column_config.NumberColumn(format="%.2f%%")
        }
    )
    
    csv_down = df_mostrar.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Descargar datos filtrados (CSV)",
        data=csv_down,
        file_name=f"sectores_cuenca_{cat_seleccionada.replace(' ', '_').lower()}.csv",
        mime="text/csv"
    )

# -------------------------------------------------------------
# TAB 5: FICHA TÉCNICA METODOLÓGICA
# -------------------------------------------------------------
with tab_ficha:
    st.markdown('<div class="main-title" style="font-size: 1.8rem;">📄 Ficha Técnica Metodológica Oficial</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Especificación del Modelo SAE Unit-Level, Logit-Benchmarking y Estándares de Calidad Estadística</div>', unsafe_allow_html=True)
    
    # Tarjetas de diagnóstico superior
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">AUC-ROC Global PEA</div>
            <div class="metric-value">0.9128</div>
            <div style="font-size: 0.8rem; color: #2E7D32; font-weight: 600;">CV UPM: 0.8763</div>
        </div>
        """, unsafe_allow_html=True)
    with fc2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Discrepancia Calibración</div>
            <div class="metric-value">0.0000%</div>
            <div style="font-size: 0.8rem; color: #2E7D32; font-weight: 600;">Cuadre exacto con ENEMDU 2025</div>
        </div>
        """, unsafe_allow_html=True)
    with fc3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Pseudo-R² McFadden</div>
            <div class="metric-value">0.3783</div>
            <div style="font-size: 0.8rem; color: #1F4E78; font-weight: 600;">Brier Score: 0.1196</div>
        </div>
        """, unsafe_allow_html=True)
    with fc4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Calidad Tasa Confiable</div>
            <div class="metric-value">94.7%</div>
            <div style="font-size: 0.8rem; color: #2E7D32; font-weight: 600;">CV &lt; 15% (2,021 sectores)</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Contenido detallado de la ficha técnica
    candidates_ficha = [
        "Visualizador_Cuenca/ficha_tecnica_metodologica.md",
        "ficha_tecnica_metodologica.md"
    ]
    ficha_md_path = next((c for c in candidates_ficha if os.path.exists(c)), None)
    if ficha_md_path and os.path.exists(ficha_md_path):
        with open(ficha_md_path, "r", encoding="utf-8") as f_md:
            ficha_text = f_md.read()
        
        st.markdown(ficha_text)
        
        # Botón de descarga de la ficha técnica
        st.download_button(
            label="📥 Descargar Ficha Técnica Completa (Markdown .md)",
            data=ficha_text.encode('utf-8-sig'),
            file_name="ficha_tecnica_metodologica_cuenca_sae.md",
            mime="text/markdown"
        )
    else:
        st.info("El archivo de la Ficha Técnica está siendo generado...")

st.markdown("---")
st.caption("Fuente cartográfica: Cartografía Censal Digital 2022 (INEC) | Fuente de microdatos: Censo de Población y Vivienda 2022 y ENEMDU Anual 2025 (INEC). Metodología: Small Area Estimation (Unit-Level) y Logit-Benchmarking.")
