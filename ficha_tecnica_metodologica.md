# FICHA TÉCNICA METODOLÓGICA
## ESTIMACIÓN Y PROYECCIÓN DEL EMPLEO ADECUADO Y VARIABLES SOCIODEMOGRÁFICAS A NIVEL DE SECTOR CENSAL
### Metodología de Estimación en Áreas Pequeñas (Small Area Estimation - SAE Unit-Level) con Logit-Benchmarking y Diseño Complejo

---

### 1. IDENTIFICACIÓN Y GENERALIDADES

| Parámetro | Detalle |
| :--- | :--- |
| **Nombre de la Operación** | Estimación y Proyección Sintética Calibrada de Empleo Adecuado, Demografía y Educación a Nivel de Sector Censal (SAE Cuenca 2025) |
| **Naturaleza Estadística** | Estadística Experimental a Escala Microterritorial (Estimación Indirecta Calibrada) |
| **Ámbito de Aplicación** | Banco de Desarrollo del Ecuador (BDE) / Piloto Cantonal Cuenca |
| **Población Objetivo** | Residentes habituales del cantón Cuenca y Población Económicamente Activa (PEA $\ge 15$ años) |
| **Unidad de Análisis Primaria** | Sector Censal (código territorial oficial de 12 dígitos `id_sector`) |
| **Cobertura Geográfica** | Cantón Cuenca (Provincia del Azuay, código cantonal `0101`) |
| **Desagregación Territorial** | 2,134 sectores censales (953 urbanos en 16 parroquias urbanas; 1,181 rurales en 21 parroquias rurales) |
| **Periodo de Referencia** | Censo CPV (Noviembre 2022) proyectado y calibrado a ENEMDU Anual 2025 |
| **Periodicidad de Actualización** | Anual (alineada a la publicación de la ENEMDU Anual por el INEC) |

---

### 2. FUENTES DE INFORMACIÓN Y MICRODATOS

1. **Censo de Población y Vivienda 2022 (CPV 2022 - INEC):**
   * *Cobertura:* Censo universal exhaustivo del cantón Cuenca.
   * *Volumen procesado:* 596,089 personas en el universo cantonal; 291,394 personas en la Población Económicamente Activa (PEA).
   * *Aporte al modelo:* Matriz auxiliar completa de covariables sociodemográficas, educativas y ocupacionales a nivel de individuo y sector censal.

2. **Encuesta Nacional de Empleo, Desempleo y Subempleo Anual 2025 (ENEMDU Anual 2025 - INEC):**
   * *Cobertura:* Muestra probabilística de la PEA del cantón Cuenca ($n = 13,353$ registros de PEA expandidos; $11,990$ ocupados remunerados analizados en el modelo).
   * *Aporte al modelo:* Variable objetivo de mercado laboral (Empleo Adecuado/Pleno, $Y \in \{0, 1\}$), diseño muestral complejo (620 UPMs, estratos) y factores de expansión (`fexp`).

3. **Cartografía Censal Digital 2022 (INEC):**
   * *Formato original:* Shapefile nacional `sector_censal_2022.shp` (EPSG:4326 WGS84).
   * *Polígonos de Cuenca:* 2,119 polígonos mapeados y optimizados mediante algoritmo Ramer-Douglas-Peucker (RDP) a 4.49 MB.
   * *Sectores especiales:* 15 sectores sin vivienda/en tránsito (terminación `888`).

---

### 3. METODOLOGÍA DE ESTIMACIÓN (SAE UNIT-LEVEL)

#### 3.1. Modelo Econométrico con Diseño Muestral Complejo
Se implementó un modelo de probabilidad a nivel de unidad (**Unit-Level Survey-Weighted Logistic GLM**):

$$\text{logit}(P(Y_i = 1 \mid \mathbf{x}_i)) = \ln\left(\frac{p_i}{1 - p_i}\right) = \mathbf{x}_i' \boldsymbol{\beta}$$

Donde:
* $Y_i = 1$ si la persona $i$ está en **Empleo Adecuado/Pleno** según la definición oficial del INEC (percibe ingresos laborales $\ge \text{SBU}$ y trabaja $\ge 40$ horas semanales o no desea trabajar más).
* $\mathbf{x}_i$ es el vector de características armonizadas observables tanto en el Censo 2022 como en la ENEMDU 2025.
* $\boldsymbol{\beta}$ es el vector de coeficientes estimados mediante Máxima Verosimilitud Ponderada con pesos de diseño $w_i = \text{fexp}_i$.
* **Covarianza Cluster-Robusta por UPM:** La matriz de covarianza de los coeficientes se calculó mediante el estimador *Sandwich / Taylor Series Linearization* agrupando por las **620 Unidades Primarias de Muestreo (UPM)**:

$$V_{\text{cluster}} = J^{-1} \left( \frac{n_c}{n_c - 1} \sum_{c=1}^{n_c} \mathbf{s}_c \mathbf{s}_c' \right) J^{-1}$$

#### 3.2. Vector de Covariables Homologadas
* **Demografía:** Sexo (hombre/mujer), 4 tramos etarios (15-24, 25-34, 35-49, 50-64; base: 65+ años), jefatura de hogar.
* **Educación:** Secundaria/bachillerato, Superior técnico, Superior universitario, Posgrado (Base balanceada: Primaria/básica o menor).
* **Seguridad Social Formal:** Mapeada en Censo con variable **P30** (*"Aporta o está afiliado a algún sistema de seguridad social: IESS general, voluntario, campesino, ISSFA, ISSPOL"*), equivalente a **p05a** en ENEMDU.
* **Categoría de Ocupación:** Empleado público, cuenta propia, patrono/empleador (Base: empleado privado).
* **Ceros Estructurales:** Por definición del mercado laboral, los **desocupados** y los **trabajadores no remunerados** reciben probabilidad cero ($P(Y=1) = 0$).
* **Grupo Ocupacional (CIUO-08):** Directores y profesionales, técnicos y administrativos, servicios y comercio, operarios y ocupaciones elementales (Base: actividades agropecuarias).
* **Área Geográfica:** Urbana / Rural.

#### 3.3. Diagnósticos del Modelo
* **Capacidad Discriminante Fuera de Conglomerado (AUC-ROC CV UPM):** **0.8761** (Validación cruzada 5-folds agrupada por UPM).
* **AUC-ROC Global PEA:** **0.9127**.
* **Calibración Probabilística (Brier Score):** **0.1196**.
* **Multicolinealidad (VIF):** Factor de Inflación de la Varianza máximo de **6.81** (ausencia de colinealidad patológica).

---

### 4. ACTUALIZACIÓN TEMPORAL Y LOGIT-BENCHMARKING (CALIBRACIÓN)

Para garantizar consistencia agregada entre la proyección intercensal y la encuesta oficial 2025, se aplicó un procedimiento formal de dos etapas:

#### 4.1. Factores de Crecimiento Intercensal de la PEA
$$\phi_{\text{Urbana}} = 1.176634 \quad (+17.66\%)$$
$$\phi_{\text{Rural}} = 1.130495 \quad (+13.05\%)$$

#### 4.2. Calibración Logit (Non-Linear Shift Calibration)
Ajuste aditivo de intercepto territorial $\gamma_a$ en el espacio logit por área $a \in \{\text{Urbana}, \text{Rural}\}$:

$$\tilde{p}_i = \frac{1}{1 + \exp\left(-\left(\mathbf{x}_i' \hat{\boldsymbol{\beta}} + \gamma_a\right)\right)}$$

$$\sum_{i \in \text{Censo}_a} \phi_a \cdot \tilde{p}_i = \text{Total ENEMDU 2025}_a$$

**Resultado del cuadre:** **Discrepancia del 0.000000%** frente a los agregados directos de la ENEMDU 2025:
* **Empleo Adecuado Cantonal 2025:** **174,054.20 personas** (Urbana: 127,582.56 | Rural: 46,471.64).
* **PEA Total Cantonal 2025:** **338,020.11 personas** (Urbana: 219,332.80 | Rural: 118,687.30).
* **Tasa Directa de Empleo Adecuado Cuenca:** **51.49%** (Urbana: 58.17% | Rural: 39.15%).

---

### 5. EVALUACIÓN DE INCERTIDUMBRE Y CALIDAD ESTADÍSTICA

* **Método de Estimación de Varianza:** Bootstrap Paramétrico Conjunto por Conglomerados ($B = 100$ réplicas), donde se perturba simultáneamente el vector de coeficientes $\boldsymbol{\beta}^{(b)} \sim \mathcal{N}(\hat{\boldsymbol{\beta}}, V_{\text{cluster}})$ y las metas directas considerando la covarianza muestral real entre PEA y Empleo Adecuado ($\rho = 0.9558$ urbano, $\rho = 0.9239$ rural; CV directo: $7.95\%$ urbano, $25.32\%$ rural).
* **Diagnóstico Sectorial de Coeficiente de Variación (CV%):**
  * **CV% Promedio Cantonal:** **7.84%**.
  * **CV% Mediana Cantonal:** **5.97%**.
  * **Rango:** $1.65\%$ a $61.99\%$.
* **Clasificación Oficial de Calidad (Estándar CEPAL / INEC):**
  * **Confiable ($CV < 15\%$):** **1,955 sectores** (**91.6%** de los sectores censales).
  * **Referencial ($15\% \le CV \le 25\%$):** **169 sectores** (**7.9%** de los sectores censales).
  * **Experimental / Cautela ($CV > 25\%$):** **10 sectores** (**0.5%** de los sectores censales, típicamente de muy baja densidad poblacional o rural dispersa).

---

### 6. ESTRUCTURA DE LA BASE MULTIDIMENSIONAL UNIFICADA

La base final consolidada posee **36,278 registros** ($2,134 \text{ sectores} \times 17 \text{ categorías}$) organizados en formato *tidy long*:

| Dimensión Analítica | Código | Categoría / Indicador | Denominador de Referencia | Naturaleza del Dato |
| :--- | :--- | :--- | :--- | :--- |
| **Mercado Laboral** | `1` | Empleo Adecuado/Pleno | PEA del sector | Modelo SAE Calibrado (Incertidumbre evaluada) |
| **Mercado Laboral** | `2-6` | Subempleo y otro empleo no pleno | PEA del sector | Residual Censal Calibrado |
| **Mercado Laboral** | `7-8` | Desempleo (abierto y oculto) | PEA del sector | Recuento Censal Calibrado |
| **Mercado Laboral** | `PEA` | Población Económicamente Activa (PEA) | PEA del sector (100%) | Recuento Censal Calibrado |
| **Demografía** | `POB_TOTAL` | Población Total | Población Total (100%) | Recuento Censal Calibrado |
| **Demografía** | `1` | Menores de 16 años | Población Total del sector | Recuento Censal Calibrado |
| **Demografía** | `2` | 16 a 29 años | Población Total del sector | Recuento Censal Calibrado |
| **Demografía** | `3` | 30 a 64 años | Población Total del sector | Recuento Censal Calibrado |
| **Demografía** | `4` | 65 años o más | Población Total del sector | Recuento Censal Calibrado |
| **Educación** | `1` | Ninguno | PEA del sector | Recuento Censal Calibrado |
| **Educación** | `2` | Inicial / preescolar | PEA del sector | Recuento Censal Calibrado |
| **Educación** | `3` | Alfabetización | PEA del sector | Recuento Censal Calibrado |
| **Educación** | `4` | Básica / primaria | PEA del sector | Recuento Censal Calibrado |
| **Educación** | `5` | Secundaria / bachillerato | PEA del sector | Recuento Censal Calibrado |
| **Educación** | `6` | Superior no universitario / técnico | PEA del sector | Recuento Censal Calibrado |
| **Educación** | `7` | Superior universitario | PEA del sector | Recuento Censal Calibrado |
| **Educación** | `8` | Posgrado | PEA del sector | Recuento Censal Calibrado |

---

### 7. LIMITACIONES Y RECOMENDACIONES DE USO

1. **Incertidumbre específica por indicador:** La clasificación de calidad estadística (*Confiable, Referencial, Experimental*) aplica **exclusivamente al modelo SAE de Empleo Adecuado**. Para la PEA, Población Total, Grupos de Edad y Educación, las cifras representan recuentos censales calibrados por el factor de crecimiento demográfico intercensal.
2. **Naturaleza de Estimación Sintética:** Los resultados microterritoriales del empleo adecuado son estimaciones indirectas obtenidas mediante modelado estadístico y calibración agregada; no corresponden a un censo continuo de empleo en 2025.
3. **Interpretación de Sectores con CV > 25%:** Los 10 sectores catalogados como *"Experimental / Cautela"* deben interpretarse agregados a nivel parroquial o de zona contigua, evitando conclusiones aisladas.
4. **Sectores Especiales sin Geometría Cartográfica (16 sectores):** Existen 16 sectores en la base de datos sin polígono en la cartografía SHP: 15 sectores colectivos/flotantes (con código `*888`) y 1 sector de dispersión territorial sin manzana cartografiada. Todos constan en las tablas de datos, pero no se dibujan en el mapa.
5. **Reproducibilidad Total:** Todos los módulos del pipeline se encuentran encadenados dinámicamente mediante parámetros calculados en `SAE_Empleo_Cuenca/scripts/`.
