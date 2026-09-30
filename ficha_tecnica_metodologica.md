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
| **Desagregación Territorial** | 2,135 sectores censales (953 urbanos en 16 parroquias urbanas; 1,182 rurales en 21 parroquias rurales) |
| **Periodo de Referencia** | Censo CPV (Noviembre 2022) proyectado y calibrado a ENEMDU Anual 2025 |
| **Periodicidad de Actualización** | Anual (alineada a la publicación de la ENEMDU Anual por el INEC) |

---

### 2. FUENTES DE INFORMACIÓN Y MICRODATOS

1. **Censo de Población y Vivienda 2022 (CPV 2022 - INEC):**
   * *Cobertura:* Censo universal exhaustivo del cantón Cuenca (100% de la población censal).
   * *Volumen procesado:* **596,101 personas** en el universo cantonal (incluyendo el sector `010159999888`); **291,394 personas** en la Población Económicamente Activa (PEA).
   * *Aporte al modelo:* Matriz auxiliar completa de covariables sociodemográficas, educativas y ocupacionales a nivel de individuo y sector censal.

2. **Encuesta Nacional de Empleo, Desempleo y Subempleo Anual 2025 (ENEMDU Anual 2025 - INEC):**
   * *Cobertura:* Muestra probabilística de la PEA del cantón Cuenca ($n = 13,353$ registros de PEA expandidos; $11,990$ ocupados remunerados analizados en el modelo).
   * *Aporte al modelo:* Variable objetivo de mercado laboral (Empleo Adecuado/Pleno, $Y \in \{0, 1\}$), diseño muestral complejo (620 UPMs, estratos) y factores de expansión (`fexp`).

3. **Cartografía Censal Digital 2022 (INEC):**
   * *Formato original:* Shapefile nacional `sector_censal_2022.shp` (EPSG:4326 WGS84).
   * *Polígonos de Cuenca:* 2,119 polígonos mapeados y optimizados mediante algoritmo Ramer-Douglas-Peucker (RDP) a 2.44 MB.
   * *Sectores especiales:* 16 sectores sin polígono cartográfico (15 colectivos/flotantes terminación `888` y 1 sector de dispersión territorial). Todos se incluyen en las bases de datos y tablas de salida.

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
* **Categoría de Ocupación:** Empleado público, cuenta propia, patrono/empleador (Base: empleado privado). Ocupados con empleo secundario (`condact == 1` con `p42 in [7,8,9]`) son clasificados como empleados privados para evitar su exclusión indebida.
* **Ceros Estructurales:** Por definición del mercado laboral, los **desocupados** y los **trabajadores familiares no remunerados estrictos** reciben probabilidad cero ($P(Y=1) = 0$).
* **Grupo Ocupacional (CIUO-08):** Directores y profesionales, técnicos y administrativos, servicios y comercio, operarios y ocupaciones elementales (Base: actividades agropecuarias).
* **Área Geográfica:** Urbana / Rural.

#### 3.3. Diagnósticos del Modelo
* **Capacidad Discriminante Fuera de Conglomerado (AUC-ROC CV UPM):** **0.8763** (Validación cruzada 5-folds agrupada por UPM).
* **AUC-ROC Global PEA:** **0.9128**.
* **Pseudo-R² de McFadden:** **0.3783** ($1 - \ln L_{\text{modelo}} / \ln L_{\text{nulo}}$), indicativo de un ajuste logístico sobresaliente (valores $> 0.20$ son excelentes).
* **Calibración Probabilística (Brier Score):** **0.1196**.
* **Multicolinealidad (VIF):** Factor de Inflación de la Varianza máximo de **6.81** (muy inferior al umbral crítico de 10).

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

* Factores de desplazamiento calculados: $\gamma_{\text{Urbana}} = -0.164804$, $\gamma_{\text{Rural}} = -1.138390$.
* **Resultado del cuadre:** **Discrepancia del 0.000000%** frente a los agregados directos de la ENEMDU 2025:
  * **Empleo Adecuado Cantonal 2025:** **174,054.20 personas** (Urbana: 127,582.56 | Rural: 46,471.64).
  * **PEA Total Cantonal 2025:** **338,020.11 personas** (Urbana: 219,332.80 | Rural: 118,687.30).
  * **Tasa Directa de Empleo Adecuado Cuenca:** **51.49%** (Urbana: 58.17% | Rural: 39.15%).

---

### 5. EVALUACIÓN DE INCERTIDUMBRE Y CALIDAD ESTADÍSTICA (DISEÑO COMPLEJO)

* **Método de Estimación de Varianza:** Bootstrap Paramétrico Conjunto por Conglomerados ($B = 100$ réplicas), donde se perturba simultáneamente el vector de coeficientes $\boldsymbol{\beta}^{(b)} \sim \mathcal{N}(\hat{\boldsymbol{\beta}}, V_{\text{cluster}})$ y las metas directas considerando la matriz de varianza-covarianza muestral de la encuesta ENEMDU (Urbano: $CV_{\text{EA}}=7.95\%$, $CV_{\text{PEA}}=10.22\%$, $\rho=0.9552$; Rural: $CV_{\text{EA}}=25.32\%$, $CV_{\text{PEA}}=24.48\%$, $\rho=0.9417$).
* **Distinción Teórica de Doble Precisión (Tasa vs. Total de Personas):**
  En Small Area Estimation, la tasa porcentual $\hat{p}_d = \hat{Y}_d / \hat{N}_d$ es un estimador de razón estabilizado por la fuerte covarianza positiva entre el numerador modelado y el denominador expandido. Por el contrario, el total absoluto de personas $\hat{Y}_d$ acumula la varianza de la proyección demográfica intercensal. Por ello, el sistema reporta de forma independiente la calidad de la tasa y la calidad del recuento.

#### 5.1. Precisión de la TASA de Empleo Adecuado (%)
* **CV% Promedio Cantonal:** **7.42%** | **Mediana:** **5.79%**
* **Clasificación según Estándares Internacionales (CEPAL / INEC):**
  * **Confiable ($CV < 15\%$):** **2,021 sectores** (**94.7%** de los sectores censales).
  * **Referencial ($15\% \le CV \le 25\%$):** **104 sectores** (**4.9%** de los sectores censales).
  * **Experimental / Cautela ($CV > 25\%$):** **9 sectores** (**0.4%** de los sectores censales).

#### 5.2. Precisión del TOTAL DE PERSONAS en Empleo Adecuado
* **CV% Promedio Cantonal:** **16.79%** | **Mediana:** **14.86%**
* **Clasificación según Estándares Internacionales (CEPAL / INEC):**
  * **Confiable ($CV < 15\%$):** **1,075 sectores** (**50.4%** de los sectores censales).
  * **Referencial ($15\% \le CV \le 25\%$):** **162 sectores** (**7.6%** de los sectores censales).
  * **Experimental / Cautela ($CV > 25\%$):** **897 sectores** (**42.0%** de los sectores censales).

---

### 6. ESTRUCTURA DE LA BASE MULTIDIMENSIONAL UNIFICADA

La base consolidada posee **36,295 registros** ($2,135 \text{ sectores} \times 17 \text{ categorías}$) en formato *tidy long*, desambiguando con rigurosidad las fuentes y universos:

| Dimensión Analítica | Código | Categoría / Indicador Oficial | Universo Denominador | Naturaleza del Dato |
| :--- | :--- | :--- | :--- | :--- |
| **Mercado Laboral** | `1` | Empleo Adecuado/Pleno | PEA del sector | Modelo SAE Calibrado (Incertidumbre dual evaluada) |
| **Mercado Laboral** | `2-6` | Otros Ocupados No Plenos y Subempleo (Residual PEA - EA - Desempleo) | PEA del sector | Residual Censal Calibrado |
| **Mercado Laboral** | `7-8` | Desocupación | PEA del sector | Recuento Censal Calibrado |
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

*Notas Metodológicas:*
1. **Definición de Desocupación en el Visualizador:** Corresponde a la población en condición de desocupación censal (abierta y oculta) identificada en el Censo de Población y Vivienda 2022 (`CONDACT in [7, 8]`), expandida y actualizada al marco demográfico de 2025. Se presenta con la etiqueta ejecutiva *"Desocupación"* para optimizar la legibilidad visual. No debe confundirse con la tasa de desempleo coyuntural de la encuesta muestral continua ENEMDU, pues refleja la inactividad laboral temporal registrada durante la semana de empadronamiento censal.
2. **Universos de Referencia:** Cada fila de la base incluye la columna explícita `universo_denominador` para clarificar si la tasa se calcula sobre la **PEA** (en Mercado Laboral y Educación) o sobre la **Población Total** (en Grupos de Edad). Asimismo, en los archivos tabulares se preserva la columna `personas_censo_2022` rotulada conceptualmente como *"Línea Base Censal Estimada 2022"*.

---

### 7. LIMITACIONES Y RECOMENDACIONES DE USO

1. **Interpretación de Incertidumbre:** La calidad de la tasa ($CV_{\text{tasa}}$) es el indicador primario para la formulación de políticas y comparaciones espaciales relativas. Cuando se utilicen presupuestos o metas cuantitativas basadas en el recuento absoluto de personas, se debe consultar prioritariamente la columna de calidad de personas ($CV_{\text{personas}}$).
2. **Sectores Especiales sin Geometría Cartográfica (16 sectores):** Existen 16 sectores en la base de datos sin polígono cartográfico en el shapefile (15 colectivos/flotantes `*888` y 1 de dispersión territorial). Todos se incluyen en las tablas analíticas y sumatorias globales, pero no se representan en el visor de mapas.
3. **Reproducibilidad y Trazabilidad:** Todo el procedimiento es 100% reproducible y se ejecuta secuencialmente mediante los scripts modularizados en `SAE_Empleo_Cuenca/scripts/`.
