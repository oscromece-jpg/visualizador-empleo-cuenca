# Visualizador Interactivo SAE: Empleo y Demografía en Cuenca

Este módulo contiene la aplicación interactiva en **Python (Streamlit + Plotly)** para explorar y visualizar los resultados de Small Area Estimation (SAE) y calibración ENEMDU 2025 a nivel de **sector censal** en el cantón Cuenca.

---

## 🚀 Cómo Iniciar la Aplicación

### Opción 1: Con un solo clic (Windows)
Haz doble clic sobre el archivo ejecutable:
👉 [`lanzar_visualizador.bat`](lanzar_visualizador.bat)

### Opción 2: Desde la consola / terminal
Ejecuta el siguiente comando desde la raíz del proyecto:
```bash
python -m streamlit run Visualizador_Cuenca/app.py
```

La aplicación se abrirá automáticamente en tu navegador web en `http://localhost:8501`.

---

## 📊 Funcionalidades del Visualizador

1. **Segmentador Multidimensional en Tiempo Real:**
   * **Condición de Actividad:** Empleo Adecuado/Pleno, Subempleo, Desempleo, PEA Total.
   * **Nivel de Instrucción:** Los 8 niveles de educación (Ninguno, Básica, Secundaria, Superior Técnico, Universitario, Posgrado).
   * **Grupo de Edad:** Menores de 16 años, 16 a 29 años, 30 a 64 años, 65 años o más.
2. **Filtros Territoriales:**
   * Área (Urbana / Rural / Todas).
   * Parroquias (las 22 parroquias de Cuenca con nombres oficiales).
3. **Panel de KPIs Dinámicos:**
   * Personas proyectadas al corte 2025.
   * Tasa o porcentaje promedio ponderado territorial.
   * Total de la PEA del territorio filtrado.
   * Conteo de sectores censales evaluados.
4. **Gráficos Interactivos Plotly:**
   * Ranking comparativo por parroquia.
   * Diagrama de composición / distribución interna.
   * Histograma de dispersión territorial entre los 2,134 sectores.
5. **Explorador y Descargador de Datos:**
   * Tabla con buscador por código de sector o parroquia.
   * Botón de descarga en formato CSV con codificación UTF-8.
