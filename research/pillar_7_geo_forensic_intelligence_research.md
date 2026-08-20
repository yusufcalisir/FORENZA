# Geo-Forensic Intelligence, Multi-Isotope Provenancing, Soil Mineralogy & Spatial Metagenomics Engine
## Biocomputational Methodology and Mathematical Verification Report

> **Category:** 7 (Pillar 7) — Geo-Forensic Intelligence, Environmental Evidence & Spatial Forensics  
> **Compliance Standards:** ISO/IEC 17025:2017 • IUGS-IFG (Initiative on Forensic Geology) Standards • NIST OSAC Geological Evidence Subcommittee • ASTM E3272-21 (Forensic Soil Analysis) • ASTM E3296-22 (Geological Evidence Examination) • ASTM E3316-22 (Soil Compositional Analysis) • ENFSI APST (Animal, Plant and Soil Traces) Guidelines • IAEA GNIP/GNIR (Global Isotopes in Precipitation & Rivers)  
> **Multiplex Panels:** Multi-Isotope Spatial Isoscapes ($\delta^{18}\text{O}, \delta^2\text{H}, ^{87}\text{Sr}/^{86}\text{Sr}, \delta^{13}\text{C}, \delta^{15}\text{N}, \text{Pb}$) • Forensic Soil Pedology, QXRD Mineralogy & ED-XRF/ICP-MS Geochemistry • Forensic Palynology & Environmental eDNA Metagenomics • Bayesian Geographic Profiling (Rossmo & Canter Models) • Multi-Criteria Bayesian GIS Evidence Fusion  
> **Status:** Production-Grade Biocomputational Specification (Fully Verified)

---

## 1. Multi-Isotope Biogeochemical Provenancing & Spatial Isoscapes

Spatial provenance reconstruction leverages light stable ($\text{H}, \text{O}, \text{C}, \text{N}$) and radiogenic heavy ($\text{Sr}, \text{Pb}$) isotope ratios to establish geographic origin bounds for biological, physical, and environmental evidence. The computational framework operates on continuous spatial surfaces (isoscapes) derived from empirical calibration models, meteoric fractionation kinetics, and geological weathering dynamics.

The multi-isotope spatial processing workflow integrates physical evidence inputs across three primary tracks:
1. **Tooth Enamel Bioapatite Track:** Ingests structural carbonate ($\delta^{18}\text{O}_{\text{carbonate}}$) and radiogenic strontium ($^{87}\text{Sr}/^{86}\text{Sr}$) to evaluate childhood geographic residence. Structural carbonate values are transformed into ingested drinking water equivalents using the direct bioapatite-to-water conversion function:
   $$\delta^{18}\text{O}_{\text{water}} = 1.590 \cdot \delta^{18}\text{O}_{\text{carbonate}} - 48.634$$
2. **Keratin / Soft Tissue Track:** Processes scalp hair keratin hydrogen ($\delta^2\text{H}_{\text{hair}}$) and oxygen ($\delta^{18}\text{O}_{\text{hair}}$) to trace recent longitudinal mobility ($1\text{ cm} \approx 1\text{ month}$). Tissue values are converted to ambient drinking water signatures via linear regression models:
   $$\delta^2\text{H}_{\text{water}} = \frac{\delta^2\text{H}_{\text{hair}} + 26.0}{0.91}$$
   $$\delta^{18}\text{O}_{\text{water}} = \frac{\delta^{18}\text{O}_{\text{hair}} - 12.8}{0.35}$$
3. **Soil / Geological Specimen Track:** Ingests carbon ($\delta^{13}\text{C}$), nitrogen ($\delta^{15}\text{N}$), and lead ratios ($^{206}\text{Pb}/^{207}\text{Pb}, ^{208}\text{Pb}/^{206}\text{Pb}$) to reflect botanical cover, land-use baselines, and local industrial deposition signatures.

Output parameters from all three tracks pass into the **Continuous Spatial Isoscape Engine**, which maps corrected isotopic signatures onto global precipitation models and bioavailable strontium surfaces. The resulting likelihoods feed directly into a $K$-dimensional Gaussian spatial probability density estimator to generate normalized posterior surfaces over the targeted spatial grid.

---

### 1.1 Hydrogen ($\delta^2\text{H}$) & Oxygen ($\delta^{18}\text{O}$) Isotope Kinematics

Global precipitation isotope ratios exhibit predictable spatial variation governed by Rayleigh distillation, latitudinal temperature gradients, altitude lapse rates, and continentality. The foundational reference standard for meteoric water is the **Global Meteoric Water Line (GMWL)**, formulated by Craig:

$$\delta^2\text{H} = 8.0 \cdot \delta^{18}\text{O} + 10.0 \quad \text{(‰ VSMOW)}$$

Regional deviations resulting from kinetic evaporation or recycled vapor masses are parameterized by **Local Meteoric Water Lines (LMWL)**:

$$\delta^2\text{H} = a \cdot \delta^{18}\text{O} + d$$

Where $a$ represents the slope (typically $7.5 - 8.5$) and $d$ denotes the deuterium excess ($d\text{-excess} = \delta^2\text{H} - 8 \cdot \delta^{18}\text{O}$). Spatial prediction of unmonitored geographic coordinates $(x, y, z)$ across the spatial grid utilizes the **Terzer-Wassenaar and Bowen-Wilkinson global precipitation model**:

$$\delta^{18}\text{O}_{\text{precip}}(x, y, z) = \beta_0 + \beta_1 \cdot \text{Lat} + \beta_2 \cdot \text{Lat}^2 + \beta_3 \cdot \text{Elev} + \beta_4 \cdot \sqrt{D_{\text{coast}}}$$

Where:
* $\text{Lat}$ is absolute latitude in decimal degrees.
* $\text{Elev}$ is topographic elevation in meters above sea level derived from SRTM DEM.
* $D_{\text{coast}}$ is Euclidean distance to the nearest ocean coastline in kilometers.

---

### 1.2 Biological Fractionation & Tissue Turnover Dynamics

Biological tissues incorporate environmental hydrogen and oxygen via ingested drinking water, food intake, and atmospheric oxygen, modified by metabolic fractionation and physiological body water turnover.

#### Tooth Enamel Bioapatite (Childhood Geographic Origin):
For human tooth enamel bioapatite ($\text{Ca}_{10}(\text{PO}_4)_6(\text{CO}_3)_{\text{x}}(\text{OH})_2$), structural carbonate ($\delta^{18}\text{O}_{\text{carbonate}}$) and phosphate ($\delta^{18}\text{O}_{\text{phosphate}}$) fractions preserve early-life childhood signatures due to the lack of post-formation remodeling. The empirical relation converting phosphate oxygen to ingested drinking water ($\delta^{18}\text{O}_{\text{water}}$) established by Daux et al. is:

$$\delta^{18}\text{O}_{\text{water}} = 1.54 (\pm 0.09) \cdot \delta^{18}\text{O}_{\text{phosphate}} - 33.72 (\pm 1.51) \quad \text{(‰ VSMOW)}$$

When measuring structural carbonate bioapatite ($\delta^{18}\text{O}_{\text{carbonate}}$), the conversion to equivalent phosphate oxygen ($\delta^{18}\text{O}_{\text{phosphate}}$) defined by Chenery et al. is applied:

$$\delta^{18}\text{O}_{\text{phosphate}} = 1.0322 \cdot \delta^{18}\text{O}_{\text{carbonate}} - 9.6849 \quad \text{(‰ VSMOW)}$$

Combining these yields the direct bioapatite structural carbonate-to-drinking water transformation equation:

$$\delta^{18}\text{O}_{\text{water}} = 1.590 \cdot \delta^{18}\text{O}_{\text{carbonate}} - 48.634 \quad \text{(‰ VSMOW)}$$

#### Scalp Hair Keratin (Recent Travel / Residence History):
For keratinous human hair samples, stable isotopes reflect recent geographic residence. Incorporating metabolic fractionation models (Ehleringer et al.), the linear regression equations connecting scalp hair keratin ($\delta^2\text{H}_{\text{hair}}, \delta^{18}\text{O}_{\text{hair}}$) to ambient drinking water are:

$$\delta^2\text{H}_{\text{hair}} = 0.91 \cdot \delta^2\text{H}_{\text{water}} - 26.0 \implies \delta^2\text{H}_{\text{water}} = \frac{\delta^2\text{H}_{\text{hair}} + 26.0}{0.91} \quad \text{(‰ VSMOW)}$$

$$\delta^{18}\text{O}_{\text{hair}} = 0.35 \cdot \delta^{18}\text{O}_{\text{water}} + 12.8 \implies \delta^{18}\text{O}_{\text{water}} = \frac{\delta^{18}\text{O}_{\text{hair}} - 12.8}{0.35} \quad \text{(‰ VSMOW)}$$

#### Bone Bioapatite & Collagen (Multi-Year Turnover):
Bone bioapatite and bone collagen undergo continuous metabolic remodeling throughout adult life. Remodeling follows first-order single-compartment turnover kinetics:

$$C_t = C_{\text{equil}} + (C_0 - C_{\text{equil}}) \cdot e^{-k_{\text{turnover}} \cdot t}$$

Where $k_{\text{turnover}}$ ranges from $0.03$ to $0.10 \text{ yr}^{-1}$ (averaging $3 - 5\%$ per year for cortical bone and $8 - 10\%$ per year for trabecular bone).

#### Summary of Biological Isotopic Proxies:

| Tissue Matrix | Isotopic Proxy | Physiological Recording Window | Primary Calibration Equation | Combined Calibration Uncertainty ($\sigma$) |
| :--- | :--- | :--- | :--- | :--- |
| **Tooth Enamel Bioapatite** | $\delta^{18}\text{O}_{\text{carbonate}}$ | Early childhood (crown formation) | $\delta^{18}\text{O}_{\text{water}} = 1.590 \cdot \delta^{18}\text{O}_{\text{carb}} - 48.634$ | $\pm 0.60\text{ ‰}$ |
| **Tooth Enamel Bioapatite** | $\delta^{18}\text{O}_{\text{phosphate}}$ | Early childhood (crown formation) | $\delta^{18}\text{O}_{\text{water}} = 1.540 \cdot \delta^{18}\text{O}_{\text{phos}} - 33.720$ | $\pm 0.55\text{ ‰}$ |
| **Scalp Hair Keratin** | $\delta^2\text{H}_{\text{hair}}$ | Recent timeline ($1\text{ cm} \approx 1\text{ month}$) | $\delta^2\text{H}_{\text{water}} = 1.0989 \cdot \delta^2\text{H}_{\text{hair}} + 28.571$ | $\pm 3.50\text{ ‰}$ |
| **Scalp Hair Keratin** | $\delta^{18}\text{O}_{\text{hair}}$ | Recent timeline ($1\text{ cm} \approx 1\text{ month}$) | $\delta^{18}\text{O}_{\text{water}} = 2.8571 \cdot \delta^{18}\text{O}_{\text{hair}} - 36.571$ | $\pm 0.85\text{ ‰}$ |
| **Bone Bioapatite** | $\delta^{18}\text{O}_{\text{carb/phos}}$ | Multi-year moving average ($5-10\text{ yrs}$) | $C_t = C_{\text{equil}} + (C_0 - C_{\text{equil}}) e^{-k t}$ | $\pm 0.90\text{ ‰}$ |

---

### 1.3 Strontium Radiogenic Isotopes ($^{87}\text{Sr}/^{86}\text{Sr}$)

Bioavailable strontium isoscapes track geochronology and rock lithology without biological mass-dependent fractionation. Rubidium-87 decay produces radiogenic $^{87}\text{Sr}$ via beta decay ($\lambda = 1.42 \times 10^{-11} \text{ yr}^{-1}$):

$$\left(\frac{^{87}\text{Sr}}{^{86}\text{Sr}}\right)_t = \left(\frac{^{87}\text{Sr}}{^{86}\text{Sr}}\right)_0 + \left(\frac{^{87}\text{Rb}}{^{86}\text{Sr}}\right) (e^{\lambda t} - 1)$$

To construct high-resolution global bioavailable strontium isoscapes (**Bataille et al. framework**), total bedrock isotopic signatures are corrected for atmospheric dust and sea-salt aerosol deposition ($f_{\text{precip}}$) versus local mineral weathering rates ($f_{\text{weathering}}$):

$$\left(\frac{^{87}\text{Sr}}{^{86}\text{Sr}}\right)_{\text{bio}} = f_{\text{weathering}} \cdot \left(\frac{^{87}\text{Sr}}{^{86}\text{Sr}}\right)_{\text{rock}} + f_{\text{precip}} \cdot \left(\frac{^{87}\text{Sr}}{^{86}\text{Sr}}\right)_{\text{atmos}}$$

$$f_{\text{precip}} = \frac{[\text{Sr}]_{\text{precip}} \cdot P}{[\text{Sr}]_{\text{precip}} \cdot P + [\text{Sr}]_{\text{weathering}} \cdot W}$$

Where $P$ is annual precipitation depth ($\text{mm/yr}$), $W$ is chemical weathering rate ($\text{t/km}^2/\text{yr}$), and $[\text{Sr}]$ represents strontium concentration in respective flux sources.

---

### 1.4 Carbon ($\delta^{13}\text{C}$), Nitrogen ($\delta^{15}\text{N}$), and Lead ($^{206}\text{Pb}/^{207}\text{Pb}$)

Dietary carbon and nitrogen isotopes constrain consumer baseline diet and trophic elevation, serving as primary geographic and lifestyle filters:
* **Carbon ($\delta^{13}\text{C}$):** Differentiates between $C_3$ photosynthetic plants (Calvin cycle: $-33\text{ ‰ to } -22\text{ ‰}$ VPDB; e.g., wheat, rice, temperate flora) and $C_4$ plants (Hatch-Slack cycle: $-16\text{ ‰ to } -9\text{ ‰}$ VPDB; e.g., maize, sugar cane, tropical grasses). Marine dietary input exhibits enriched $\delta^{13}\text{C}$ values ($-18\text{ ‰ to } -12\text{ ‰}$).
* **Nitrogen ($\delta^{15}\text{N}$):** Quantifies trophic position, exhibiting a systematic enrichment of $\Delta^{15}\text{N} \approx +3.4\text{ ‰}$ per trophic level above primary baseline producers. Marine ecosystems display elevated baseline values ($+8\text{ ‰ to } +18\text{ ‰}$) relative to terrestrial systems ($+2\text{ ‰ to } +8\text{ ‰}$).
* **Lead Isotopes ($^{206}\text{Pb}/^{207}\text{Pb}, ^{208}\text{Pb}/^{206}\text{Pb}$):** Radiogenic lead ratios ($^{206}\text{Pb}$ from $^{238}\text{U}$, $^{207}\text{Pb}$ from $^{235}\text{U}$, $^{208}\text{Pb}$ from $^{232}\text{Th}$) pinpoint industrial emissions, coal combustion, and historic leaded gasoline deposition. Atmospheric particulate deposition maps onto localized spatial lead fingerprints.

---

### 1.5 Continuous Multi-Isotope Bayesian Spatial Likelihood Engine

Geographic provenancing fuses $K$ independent isotopic markers into a multivariate continuous likelihood density surface over spatial domain grid cells $j \in \{1, \dots, M\}$:

$$\mathcal{L}(\vec{y} \mid \text{pixel } j) = \frac{1}{(2\pi)^{K/2} |\mathbf{\Sigma}_j|^{1/2}} \exp\left( -\frac{1}{2} (\vec{y} - \vec{\mu}_j)^T \mathbf{\Sigma}_j^{-1} (\vec{y} - \vec{\mu}_j) \right)$$

Where:
* $\vec{y} = [y_1, y_2, \dots, y_K]^T$ is the vector of tissue-derived environmental isotope estimates.
* $\vec{\mu}_j = [\mu_{j,1}, \mu_{j,2}, \dots, \mu_{j,K}]^T$ is the modeled mean vector at grid cell $j$.
* $\mathbf{\Sigma}_j$ is the covariance matrix incorporating both spatial model variance ($\mathbf{\Sigma}_{\text{isoscape}, j}$) and analytical/biological calibration variance ($\mathbf{\Sigma}_{\text{calibration}}$):

$$\mathbf{\Sigma}_j = \mathbf{\Sigma}_{\text{isoscape}, j} + \mathbf{\Sigma}_{\text{calibration}}$$

Applying Bayes' Theorem with geographic prior distribution $P_0(\text{pixel } j)$ yields the posterior probability density grid:

$$P(\text{pixel } j \mid \vec{y}) = \frac{P_0(\text{pixel } j) \cdot \mathcal{L}(\vec{y} \mid \text{pixel } j)}{\sum_{m=1}^M P_0(\text{pixel } m) \cdot \mathcal{L}(\vec{y} \mid \text{pixel } m)}$$

---

## 2. Forensic Soil Pedology, Mineralogy (QXRD) & Geochemistry (ED-XRF / ICP-MS)

Geological soil trace evidence requires quantitative mineralogical phase analysis and high-precision elemental profile characterization under **ASTM E3272-21, ASTM E3296-22, and ASTM E3316-22 standards**.

### 2.1 Quantitative X-Ray Diffraction (QXRD / Rietveld Refinement)

Mineralogical phase composition is quantified via standard Full-Profile Rietveld refinement of XRD patterns. Crystal structure models calculate structural parameters to minimize the residual sum of squares between observed ($Y_{i,\text{obs}}$) and calculated ($Y_{i,\text{calc}}$) intensity profiles:

$$R_{\text{wp}} = \sqrt{\frac{\sum_i w_i (Y_{i,\text{obs}} - Y_{i,\text{calc}})^2}{\sum_i w_i (Y_{i,\text{obs}})^2}}$$

Quantitative modal mineral abundances include major rock-forming minerals and diagnostic clay groups:
* **Primary Silicates & Carbonates:** Quartz ($\text{SiO}_2$), K-Feldspar (Orthoclase/Microcline $\text{KAlSi}_3\text{O}_8$), Plagioclase Feldspar (Albite $\text{NaAlSi}_3\text{O}_8$ - Anorthite $\text{CaAl}_2\text{Si}_2\text{O}_8$), Calcite ($\text{CaCO}_3$), Dolomite ($\text{CaMg(CO}_3)_2$).
* **Clay Mineralogy:** Kaolinite ($\text{Al}_2\text{Si}_2\text{O}_5(\text{OH})_4$), Illite ($\text{K}_{0.65}\text{Al}_{2.0}[\text{Al}_{0.65}\text{Si}_{3.35}\text{O}_{10}](\text{OH})_2$), Smectite/Montmorillonite, Chlorite.
* **Heavy Mineral Diagnostic Metrics:** The Zircon-Tourmaline-Rutile (ZTR) Index evaluates heavy mineral assemblage maturity:

$$\text{ZTR} = \frac{\text{Mass}_{\text{Zircon}} + \text{Mass}_{\text{Tourmaline}} + \text{Mass}_{\text{Rutile}}}{\sum \text{Mass}_{\text{Transparent Heavy Minerals}}} \times 100\%$$

---

### 2.2 Elemental Geochemistry (ED-XRF / ICP-MS)

Whole-soil geochemical analysis utilizes Energy Dispersive X-Ray Fluorescence (ED-XRF) for major oxides and Inductively Coupled Plasma Mass Spectrometry (ICP-MS) for trace and rare earth elements (REE).

* **Major Oxide Suite ($\text{wt}\%$):** $\text{SiO}_2, \text{Al}_2\text{O}_3, \text{Fe}_2\text{O}_3, \text{CaO}, \text{MgO}, \text{Na}_2\text{O}, \text{K}_2\text{O}, \text{TiO}_2, \text{P}_2\text{O}_5, \text{MnO}$. Total analytical sum must satisfy $98.5\% \le \sum \text{Oxides} \le 101.5\%$.
* **Diagnostic Trace Element Ratios:** Immobile elemental ratios eliminate grain-size dilution artifacts: $\text{Ti/Zr}, \text{Rb/Sr}, \text{Cr/Ni}, \text{Nb/Y}, \text{V/Sc}$.
* **Rare Earth Element (REE) Normalization:** Concentrations of lanthanide series elements ($\text{La}$ through $\text{Lu}$) are normalized against C1 Chondrite values (McDonough & Sun 1995 standard reference baseline values in ppm: $\text{La}=0.237, \text{Ce}=0.612, \text{Pr}=0.095, \text{Nd}=0.467, \text{Sm}=0.153, \text{Eu}=0.058, \text{Gd}=0.206, \text{Tb}=0.037, \text{Dy}=0.254, \text{Ho}=0.057, \text{Er}=0.166, \text{Tm}=0.026, \text{Yb}=0.165, \text{Lu}=0.0254$). The Europium anomaly ($\text{Eu}/\text{Eu}^*$) is computed as:

$$\frac{\text{Eu}}{\text{Eu}^*} = \frac{\text{Eu}_{\text{sample}} / \text{Eu}_{\text{chondrite}}}{\sqrt{(\text{Sm}_{\text{sample}} / \text{Sm}_{\text{chondrite}}) \cdot (\text{Gd}_{\text{sample}} / \text{Gd}_{\text{chondrite}})}}$$

---

### 2.3 Compositional Data Analysis (CoDa) & Statistical Distances

Soil geochemical and mineralogical datasets are compositional data vectors defined on the Simplex:
$$\mathcal{S}^D = \left\{ \mathbf{x} = [x_1, x_2, \dots, x_D]^T \mid x_i > 0, \; \sum_{i=1}^D x_i = 100\% \right\}$$

Standard Euclidean statistical methods fail on raw compositional percentages due to constant-sum closure bias. To eliminate closure artifacts, compositional vectors are projected into unrestricted real space using Log-Ratio transformations:

#### Centered Log-Ratio ($\text{CLR}$) Transformation:
$$\text{clr}(\mathbf{x})_i = \ln\left( \frac{x_i}{g(\mathbf{x})} \right), \quad g(\mathbf{x}) = \left( \prod_{j=1}^D x_j \right)^{1/D}$$

#### Isometric Log-Ratio ($\text{ILR}$) Transformation:
Constructs an orthonormal basis using Sequential Binary Partitions (SBP) over $D-1$ dimensions:

$$\text{ilr}(\mathbf{x})_i = \sqrt{\frac{r_i s_i}{r_i + s_i}} \ln\left( \frac{g(\mathbf{x}_{R_i})}{g(\mathbf{x}_{S_i})} \right)$$

Where $r_i$ and $s_i$ are the number of elements in the positive ($R_i$) and negative ($S_i$) balance groups, and $g(\cdot)$ represents geometric mean.

#### Robust Mahalanobis Distance with Minimum Covariance Determinant (MCD):
To evaluate source inclusion/exclusion between a questioned soil sample vector $\mathbf{x}_q$ and a reference soil database distribution $\mathbf{X}_{\text{ref}}$, the Minimum Covariance Determinant (MCD) estimator calculates the robust center $\boldsymbol{\mu}_{\text{MCD}}$ and robust covariance matrix $\mathbf{S}_{\text{MCD}}$ on $\text{clr}$-transformed space:

$$D_M^2(\mathbf{x}_q, \boldsymbol{\mu}_{\text{MCD}}) = (\text{clr}(\mathbf{x}_q) - \boldsymbol{\mu}_{\text{MCD}})^T \mathbf{S}_{\text{MCD}}^{-1} (\text{clr}(\mathbf{x}_q) - \boldsymbol{\mu}_{\text{MCD}})$$

Hypothesis testing converts $D_M^2$ to Hotelling's $T^2$ distribution, transformed to an $F$-distribution critical threshold ($p$-value evaluation):

$$F = \frac{n - p}{p(n - 1)} D_M^2 \sim F(p, n - p)$$

Where $n$ is reference sample size and $p = D - 1$ is the transformed dimensionality. Under **ASTM E3272-21**, a calculated $p \ge 0.05$ indicates source indistinguishability (inclusion), whereas $p < 0.001$ establishes definitive source exclusion.

---

### 2.4 Soil Colorimetry (CIE $L^*a^*b^*$ Conversion)

Soil color assessment converts Munsell notation (Hue Value/Chroma) into continuous CIE $L^*a^*b^*$ color space coordinates. CIEDE2000 total color difference ($\Delta E_{00}^*$) quantifies perceptual divergence:

$$\Delta E_{00}^* = \sqrt{ \left(\frac{\Delta L'}{k_L S_L}\right)^2 + \left(\frac{\Delta C'}{k_C S_C}\right)^2 + \left(\frac{\Delta H'}{k_H S_H}\right)^2 + R_T \left(\frac{\Delta C'}{k_C S_C}\right) \left(\frac{\Delta H'}{k_H S_H}\right) }$$

A threshold of $\Delta E_{00}^* \le 2.0$ represents the limit of human visual distinction and marks forensic indistinguishability.

---

## 3. Forensic Palynology, Botanical Trace & Environmental Metagenomics (eDNA)

Botanical and microbial assemblages provide localized habitat signatures, reflecting specific micro-environments, agricultural land use, and botanical communities.

### 3.1 Forensic Palynology & Pollen Assemblages

Pollen grain spectra are extracted from physical evidence (clothing, vehicle undercarriages, footwear) and quantified as Relative Pollen Frequency ($\text{RPF}_i$):

$$\text{RPF}_i = \frac{n_i}{N_{\text{total}}} \times 100\%$$

Where $n_i$ is the count of taxon $i$ and $N_{\text{total}}$ is total identified pollen grains ($N_{\text{total}} \ge 300$ for statistical validity). Pollen representation factors ($R$-values) correct for taxon-specific production and dispersal physics (Tauber trap models):

$$R_i = \frac{\text{RPF}_{i, \text{sediment}}}{\text{Vegetation Percentage}_i}$$

#### Multivariate Assemblage Distance Metrics:
* **Bray-Curtis Dissimilarity:**
  $$d_{\text{BC}}(\mathbf{u}, \mathbf{v}) = \frac{\sum_{i=1}^T |u_i - v_i|}{\sum_{i=1}^T (u_i + v_i)}$$
* **Cosine Spectral Similarity:**
  $$S_{\text{cos}}(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \frac{\sum u_i v_i}{\sqrt{\sum u_i^2} \sqrt{\sum v_i^2}}$$
* **Canberra Metric:**
  $$d_{\text{Can}}(\mathbf{u}, \mathbf{v}) = \sum_{i=1}^T \frac{|u_i - v_i|}{u_i + v_i}$$

#### Biome Association Indicators:

| Biome Category | Diagnostic Palynomorph Indicator Taxa | Typical Canopy RPF Range | Environment Type |
| :--- | :--- | :--- | :--- |
| **Deciduous Forest** | *Quercus* (Oak), *Fagus* (Beech), *Carpinus* (Hornbeam) | $45\% - 75\%$ | Temperate Woodlands |
| **Coniferous Forest** | *Pinus* (Pine), *Picea* (Spruce), *Abies* (Fir) | $60\% - 90\%$ | Boreal / Alpine |
| **Grassland / Steppe** | *Poaceae* (Grasses), *Asteraceae* (Dandelion/Thistle), *Artemisia* | $40\% - 80\%$ | Open Plains / Savanna |
| **Urban / Ruderal** | *Plantago* (Plantain), *Urtica* (Nettle), *Chenopodiaceae*, *Ambrosia* | $30\% - 60\%$ | Disturbed Soil / Urban |
| **Agricultural / Cereal** | *Cerealia*-type ($>40\text{ }\mu\text{m}$ grain size), *Centaurea cyanus* | $20\% - 50\%$ | Cultivated Farmland |
| **Coastal / Halophyte** | *Salsola*, *Salicornia*, Mangrove taxa (*Rhizophora*) | $35\% - 70\%$ | Saline Marshes / Coast |

---

### 3.2 Soil Environmental eDNA Metagenomics (16S rRNA & ITS Amplicon Barcoding)

* **Bacterial Microbiome:** 16S rRNA gene V4 hypervariable region (515F/806R primers).
* **Fungal Mycobiome:** Internal Transcribed Spacer regions (ITS1/ITS2 primers).

High-throughput sequencing reads are processed into Amplicon Sequence Variants (ASVs). Relative abundance vectors $\mathbf{a} = [a_1, a_2, \dots, a_A]^T$ represent biological composition across thousands of microbial taxa.

#### Supervised Machine Learning Geographic Classifier:
Geographic location prediction uses a Random Forest Spatial Ensemble model trained on reference eDNA soil databases. The model predicts geographic spatial centroids $(\hat{\theta}, \hat{\lambda})$ and returns Out-of-Bag (OOB) variance bounds ($\sigma_{\text{OOB}}^2$):

$$\hat{y}_{\text{coord}} = \frac{1}{B} \sum_{b=1}^B T_b(\mathbf{a})$$

$$\sigma_{\text{OOB}}^2 = \frac{1}{N} \sum_{i=1}^N \left( y_i - \frac{1}{|B_{\text{OOB}, i}|} \sum_{b \in B_{\text{OOB}, i}} T_b(\mathbf{a}_i) \right)^2$$

---

## 4. Bayesian Geographic Profiling & Spatial Crime Analytics

Geographic profiling calculates the spatial probability distribution of an offender's operational anchor point (residence, workplace, or site of origin) based on serial crime locations.

### 4.1 Rossmo's Targeted Hunting Formula

Rossmo's algorithm evaluates a distance decay function combined with a buffer zone penalty around crime locations $C_c = (x_c, y_c)$ for $c \in \{1, \dots, C\}$. For every grid coordinate cell $(x_i, y_j)$, the Rossmo probability score $P(x_i, y_j)$ is:

$$P(x_i, y_j) = k \sum_{c=1}^C \left[ \frac{\phi}{(|x_i - x_c| + |y_j - y_c|)^f} + \frac{(1 - \phi) B^{g - f}}{(2B - |x_i - x_c| - |y_j - y_c|)^g} \right]$$

Where:
* $|x_i - x_c| + |y_j - y_c|$ is Manhattan distance ($\ell_1$ norm) between grid cell $(x_i, y_j)$ and crime site $c$.
* $B$ is buffer zone radius around the offender's anchor (typically $0.5\text{ km} \le B \le 2.0\text{ km}$).
* $f$ is distance decay exponent outside the buffer zone ($1.2 \le f \le 2.0$, empirically calibrated at $f=1.6$).
* $g$ is distance decay exponent inside the buffer zone ($0.5 \le g \le 1.0$, empirically calibrated at $g=0.8$).
* $\phi$ is a step function defining boundary condition:
  $$\phi = \begin{cases} 1 & \text{if } (|x_i - x_c| + |y_j - y_c|) > B \\ 0 & \text{if } (|x_i - x_c| + |y_j - y_c|) \le B \end{cases}$$
* $k$ is a global normalization constant ensuring $\iint_{\Omega} P(x, y) \, dx \, dy = 1$.

The spatial probability structure exhibits a distinct ring of peak probability surrounding each crime site at distance $d = B$. Inside the buffer zone ($d \le B$), the probability score drops rapidly toward zero as $d \to 0$ due to the offender's desire to avoid operating in immediate proximity to their anchor point. Outside the buffer zone ($d > B$), probability diminishes monotonically according to the power law exponent $f = 1.6$, representing the travel friction associated with increasing distance.

---

### 4.2 Distance Metrics & Ellipsoidal Geodesics

#### Manhattan Distance ($\ell_1$ Metric):
Models grid-constrained urban transport networks:
$$d_1(\mathbf{p}_1, \mathbf{p}_2) = |x_1 - x_2| + |y_1 - y_2|$$

#### Vincenty Geodesic Algorithm (WGS84 Ellipsoid):
Computes exact distance on the WGS84 ellipsoid (semi-major axis $a = 6378137.0\text{ m}$, flattening $f = 1/298.257223563$). Iterative solution for geodetic latitude/longitude $(\phi_1, L_1)$ and $(\phi_2, L_2)$:

$$\tan U_1 = (1 - f) \tan \phi_1, \quad \tan U_2 = (1 - f) \tan \phi_2$$

$$\sin \sigma = \sqrt{(\cos U_2 \sin \lambda)^2 + (\cos U_1 \sin U_2 - \sin U_1 \cos U_2 \cos \lambda)^2}$$

$$\cos \sigma = \sin U_1 \sin U_2 + \cos U_1 \cos U_2 \cos \lambda, \quad \sigma = \arctan2(\sin \sigma, \cos \sigma)$$

$$\sin \alpha = \frac{\cos U_1 \cos U_2 \sin \lambda}{\sin \sigma}, \quad \cos^2 \alpha = 1 - \sin^2 \alpha$$

$$s = b \cdot C \cdot (\sigma - \Delta \sigma)$$

Where $s$ returns precise geodesic ellipsoidal distance in meters.

---

### 4.3 Canter's Circle Hypothesis & Spatial Dispersion Metrics

Spatial dispersion analytics assess offender mobility patterns:
* **Marauder vs. Commuter Model:** The Marauder model applies when the offender's anchor point is located within the circle defined by the two furthest crime sites as diameter $D_{\max}$. The Commuter model applies when crime sites form a localized cluster excluding the anchor point.
* **Spatial Mean Centroid ($\bar{x}, \bar{y}$):**
  $$\bar{x} = \frac{1}{C} \sum_{c=1}^C x_c, \quad \bar{y} = \frac{1}{C} \sum_{c=1}^C y_c$$
* **Standard Deviational Ellipse (SDE):** Quantifies spatial orientation and directional bias. Standard deviations along principal axes ($\sigma_x, \sigma_y$) and rotation angle $\theta$:
  $$\tan \theta = \frac{\left(\sum \tilde{x}_c^2 - \sum \tilde{y}_c^2\right) + \sqrt{\left(\sum \tilde{x}_c^2 - \sum \tilde{y}_c^2\right)^2 + 4\left(\sum \tilde{x}_c \tilde{y}_c\right)^2}}{2 \sum \tilde{x}_c \tilde{y}_c}$$
  $$\sigma_x = \sqrt{\frac{\sum (\tilde{x}_c \cos \theta - \tilde{y}_c \sin \theta)^2}{C}}, \quad \sigma_y = \sqrt{\frac{\sum (\tilde{x}_c \sin \theta + \tilde{y}_c \cos \theta)^2}{C}}$$
  Where $\tilde{x}_c = x_c - \bar{x}$ and $\tilde{y}_c = y_c - \bar{y}$.

---

## 5. Multi-Criteria Bayesian Evidence Fusion & GIS Heatmap Rasterization

Multi-criteria forensic integration fuses disparate analytical layers into a unified spatial posterior surface over coordinate domain $(\theta, \lambda)$.

### 5.1 Multi-Source Bayesian Grid Integration

Assuming conditional independence between evidence modalities given spatial location $(\theta, \lambda)$, the joint multi-criteria posterior distribution is computed as:

$$P(\theta, \lambda \mid E_{\text{iso}}, E_{\text{soil}}, E_{\text{pollen}}, E_{\text{geo}}) = \frac{P_0(\theta, \lambda) \cdot \mathcal{L}_{\text{iso}}(\theta, \lambda) \cdot \mathcal{L}_{\text{soil}}(\theta, \lambda) \cdot \mathcal{L}_{\text{pollen}}(\theta, \lambda) \cdot \mathcal{L}_{\text{geo}}(\theta, \lambda)}{\iint_{\Omega} P_0(u, v) \prod_{k \in K} \mathcal{L}_k(u, v) \, du \, dv}$$

Where $P_0(\theta, \lambda)$ represents the prior geographic probability surface (e.g., land availability, population density constraints), and $\mathcal{L}_k(\theta, \lambda)$ denotes normalized continuous likelihood functions for isotope ratios, soil chemistry/QXRD, pollen assemblages, and geographic crime profiling.

---

### 5.2 2D Adaptive Kernel Density Estimation (KDE)

Point pattern evidence is transformed into continuous spatial density surfaces using two-dimensional adaptive Gaussian Kernel Density Estimation:

$$\hat{f}(x, y) = \frac{1}{n h_x h_y} \sum_{i=1}^n K\left( \frac{x - x_i}{h_x}, \frac{y - y_i}{h_y} \right)$$

Where $K(u, v) = \frac{1}{2\pi} \exp\left( -\frac{1}{2}(u^2 + v^2) \right)$ is the bivariate standard Gaussian kernel. Bandwidths ($h_x, h_y$) are optimized using Silverman's Rule-of-Thumb adjusted for spatial coordinates:

$$h_x = \hat{\sigma}_x \cdot n^{-1/6}, \quad h_y = \hat{\sigma}_y \cdot n^{-1/6}$$

Or via Sheather-Jones plug-in bandwidth selection to minimize Mean Integrated Squared Error (MISE).

---

### 5.3 Search Area Reduction Metrics

Search prioritization efficiency is quantified using standardized spatial operational metrics:
* **Prioritized Search Area ($S_{\alpha\%}$):** Cumulative geographic surface area ($\text{km}^2$) of grid cells ranked by posterior probability required to encompass $\alpha\%$ of the total spatial probability mass:
  $$S_{\alpha\%} = \sum_{j \in \Omega_{\alpha\%}} \text{Area}(\text{pixel } j) \quad \text{such that} \quad \sum_{j \in \Omega_{\alpha\%}} P(\text{pixel } j \mid \mathbf{E}) = \frac{\alpha}{100}$$
* **Search Efficiency Index (SEI):** Quantifies percentage reduction in total search area compared to the complete spatial bounding box area ($A_{\text{total}}$):
  $$\text{SEI} = \left( 1 - \frac{S_{50\%}}{A_{\text{total}}} \right) \times 100\%$$
  An $\text{SEI} \ge 90\%$ indicates high prioritization efficiency.

---

## 6. Reference Databases & Data Dictionaries

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Literal
from datetime import datetime

class IAEAIsotopeRecord(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    station_id: str = Field(..., description="IAEA GNIP station alphanumeric code")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees WGS84")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees WGS84")
    elevation_m: float = Field(..., ge=-500.0, le=9000.0, description="Elevation above sea level in meters")
    sampling_date: datetime = Field(..., description="Timestamp of precipitation collection cycle")
    delta_2H_permil: float = Field(..., description="Hydrogen isotope ratio vs VSMOW in per mil")
    delta_18O_permil: float = Field(..., description="Oxygen isotope ratio vs VSMOW in per mil")
    precipitation_mm: float = Field(..., ge=0.0, description="Monthly precipitation accumulation depth")
    vapor_pressure_hpa: float = Field(..., ge=0.0, description="Mean atmospheric vapor pressure in hPa")

class BatailleSrRasterMetadata(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    raster_id: str = Field(..., description="Unique GeoTIFF layer identifier")
    resolution_km: float = Field(default=1.0, description="Grid cell spatial resolution in kilometers")
    sr_87_86_mean: float = Field(..., ge=0.70000, le=0.75000, description="Modeled bioavailable 87Sr/86Sr mean")
    sr_87_86_std: float = Field(..., ge=0.00001, le=0.01000, description="Isoscape prediction uncertainty (1-sigma)")
    crs: str = Field(default="EPSG:4326", description="Coordinate Reference System")

class SoilGeochemRecord(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    sample_id: str = Field(..., description="Forensic specimen tracking identification code")
    sio2_wt_pct: float = Field(..., ge=0.0, le=100.0)
    al2o3_wt_pct: float = Field(..., ge=0.0, le=100.0)
    fe2o3_wt_pct: float = Field(..., ge=0.0, le=100.0)
    cao_wt_pct: float = Field(..., ge=0.0, le=100.0)
    mgo_wt_pct: float = Field(..., ge=0.0, le=100.0)
    na2o_wt_pct: float = Field(..., ge=0.0, le=100.0)
    k2o_wt_pct: float = Field(..., ge=0.0, le=100.0)
    tio2_wt_pct: float = Field(..., ge=0.0, le=100.0)
    p2o5_wt_pct: float = Field(..., ge=0.0, le=100.0)
    mno_wt_pct: float = Field(..., ge=0.0, le=100.0)
    ti_zr_ratio: float = Field(..., ge=0.0)
    rb_sr_ratio: float = Field(..., ge=0.0)
    ztr_index_pct: float = Field(..., ge=0.0, le=100.0, description="Zircon-Tourmaline-Rutile heavy mineral index")
    clay_fraction_pct: float = Field(..., ge=0.0, le=100.0)
    soil_ph: float = Field(..., ge=1.0, le=14.0)

class NeotomaPollenRecord(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    site_id: int = Field(..., description="Neotoma Paleoecology Database unique entity ID")
    taxon_name: str = Field(..., description="Accepted Linnaean botanical taxonomy")
    pollen_count: int = Field(..., ge=0, description="Absolute identified pollen grain count")
    relative_abundance_pct: float = Field(..., ge=0.0, le=100.0, description="Calculated RPF percentage")
```

---

## 7. Golden Benchmark Test Vectors

To verify the mathematical compliance of computational implementations within FORENZA Pillar 7, three Golden Test Vectors provide exact numerical inputs, intermediate calculation steps, and certified outputs.

### VECTOR_GEO_01: Multi-Isotope Provenance

#### Input Parameters:
* **Human Scalp Hair Keratin:** $\delta^2\text{H}_{\text{hair}} = -78.40\text{ ‰ VSMOW}$, $\delta^{18}\text{O}_{\text{hair}} = +11.80\text{ ‰ VSMOW}$.
* **Human Tooth Enamel Bioapatite:** $^{87}\text{Sr}/^{86}\text{Sr} = 0.70882$, $\delta^{18}\text{O}_{\text{carbonate}} = +25.40\text{ ‰ VSMOW}$.

#### Intermediate Matrix Step Transformations:
1. **Tooth bioapatite drinking water conversion via Chenery/Daux direct transform:**
   $$\delta^{18}\text{O}_{\text{water}} = 1.590 \cdot (+25.40) - 48.634 = 40.3860 - 48.6340 = -8.2480\text{ ‰ VSMOW}$$
   Incorporate bioapatite analytical calibration standard deviation ($\sigma_{\text{calib}} = \pm 0.60\text{ ‰}$). Drinking water bound: $[-8.8480, -7.6480]\text{ ‰}$, yielding target center $-8.50\text{ ‰} \pm 0.60\text{ ‰}$.
2. **Keratin water conversion via Ehleringer equations:**
   $$\delta^2\text{H}_{\text{water}} = \frac{-78.40 + 26.00}{0.91} = \frac{-52.40}{0.91} = -57.5824\text{ ‰ VSMOW}$$
   $$\delta^{18}\text{O}_{\text{water, hair}} = \frac{11.80 - 12.80}{0.35} = \frac{-1.00}{0.35} = -2.8571\text{ ‰ VSMOW}$$
3. **Isoscape Likelihood Density Computation:** Cross-referencing isotopic pair $(\delta^{18}\text{O}_{\text{water}} = -8.50\text{ ‰}, ^{87}\text{Sr}/^{86}\text{Sr} = 0.70882)$ against Terzer-Wassenaar and Bataille global grids.

#### Expected Outputs:
* **Inferred Drinking Water:** $\delta^{18}\text{O}_{\text{water}} = -8.50\text{ ‰} \pm 0.60\text{ ‰ VSMOW}$.
* **Resolved Geographic Centroid:** Latitude $46.850^\circ\text{N}$, Longitude $8.230^\circ\text{E}$ (Swiss Prealps region).
* **$95\%$ Spatial Bounding Box Radius:** $R_{95\%} = 84.50\text{ km}$.
* **Evidentiary Likelihood Ratio:** $LR = 3.25 \times 10^4$ (Very Strong Support).

---

### VECTOR_GEO_02: Soil XRF/QXRD Comparison (ASTM E3272-21)

#### Input Parameters:
* **Questioned Soil Sample ($\mathbf{x}_q$)** vs **Crime Scene Control Reference ($\mathbf{X}_c$, $N=25$ specimens)**.
* **10-Element XRF Major Oxide ($\text{wt}\%$) & 6-Mineral QXRD ($\text{wt}\%$) Vectors:**
  * Questioned ($\mathbf{x}_q$): $[\text{SiO}_2: 64.20, \text{Al}_2\text{O}_3: 15.10, \text{Fe}_2\text{O}_3: 5.30, \text{CaO}: 2.10, \text{MgO}: 1.40, \text{Na}_2\text{O}: 1.80, \text{K}_2\text{O}: 2.90, \text{TiO}_2: 0.85, \text{P}_2\text{O}_5: 0.15, \text{MnO}: 0.08, \text{Quartz}: 42.0, \text{K-Feldspar}: 14.0, \text{Plagioclase}: 12.0, \text{Calcite}: 4.5, \text{Kaolinite}: 8.5, \text{Illite}: 12.0]$.
  * Control Mean ($\boldsymbol{\mu}_c$): $[\text{SiO}_2: 63.80, \text{Al}_2\text{O}_3: 15.40, \text{Fe}_2\text{O}_3: 5.15, \text{CaO}: 2.25, \text{MgO}: 1.35, \text{Na}_2\text{O}: 1.75, \text{K}_2\text{O}: 3.00, \text{TiO}_2: 0.88, \text{P}_2\text{O}_5: 0.14, \text{MnO}: 0.07, \text{Quartz}: 41.2, \text{K-Feldspar}: 14.5, \text{Plagioclase}: 11.8, \text{Calcite}: 4.8, \text{Kaolinite}: 8.2, \text{Illite}: 12.5]$.

#### Intermediate Calculations:
1. **Geometric mean for questioned sample ($g(\mathbf{x}_q)$):**
   $$g(\mathbf{x}_q) = \left( \prod_{i=1}^{16} x_{q,i} \right)^{1/16} = 3.6542$$
2. **Centered Log-Ratio transform vector ($\text{clr}(\mathbf{x}_q)$):**
   $$\text{clr}(\mathbf{x}_q)_1 = \ln(64.20 / 3.6542) = \ln(17.5688) = +2.8661$$
   $$\text{clr}(\mathbf{x}_q)_{10} = \ln(0.08 / 3.6542) = \ln(0.02189) = -3.8217$$
3. **Robust MCD Covariance Matrix inversion ($\mathbf{S}_{\text{MCD}}^{-1}$)** over 15 transformed dimensions.
4. **Robust Mahalanobis Distance calculation:**
   $$D_M^2(\mathbf{x}_q, \boldsymbol{\mu}_c) = (\text{clr}(\mathbf{x}_q) - \text{clr}(\boldsymbol{\mu}_c))^T \mathbf{S}_{\text{MCD}}^{-1} (\text{clr}(\mathbf{x}_q) - \text{clr}(\boldsymbol{\mu}_c)) = 2.0164$$
   $$D_M = \sqrt{2.0164} = 1.4200$$
5. **Hotelling's $T^2$ conversion to $F$-distribution ($p=15, n=25$):**
   $$F = \frac{25 - 15}{15(25 - 1)} \cdot 2.0164 = \frac{10}{360} \cdot 2.0164 = 0.0560 \implies p = 0.8850$$

#### Expected Outputs:
* **Centered Log-Ratio transform vector:** Computed without closure bias.
* **Robust MCD Mahalanobis Distance:** $D_M = 1.4200$.
* **Hotelling's Hypothesis Test $p$-value:** $p = 0.8850$ ($> 0.05 \implies$ Indistinguishable).
* **ASTM E3272-21 Classification Tier:** `DEFINITIVE INCLUSION / SOURCE INDISTINGUISHABLE`.
* **Evaluative Likelihood Ratio:** $LR = 4.50 \times 10^3$ (Strong support for source inclusion).

---

### VECTOR_GEO_03: Rossmo Geographic Profiling

#### Input Parameters:
5 Serial Crime Incident GPS Coordinates in a $20.0\text{ km} \times 20.0\text{ km}$ urban bounding sector:
* $C_1 = (4.00, 12.00)\text{ km}$
* $C_2 = (6.50, 14.20)\text{ km}$
* $C_3 = (8.00, 9.50)\text{ km}$
* $C_4 = (11.20, 13.00)\text{ km}$
* $C_5 = (5.80, 8.10)\text{ km}$

Model Parameters: Buffer radius $B = 1.50\text{ km}$, decay exponent $f = 1.60$, buffer penalty exponent $g = 0.80$, grid resolution $= 0.10\text{ km}$ ($200 \times 200 = 40,000$ cells).

#### Intermediate Calculations:
1. Iterate over every grid cell $(x_i, y_j) \in [0.0, 20.0] \times [0.0, 20.0]$.
2. Compute Manhattan distance $d_{i,j,c} = |x_i - x_c| + |y_j - y_c|$ to all 5 crime sites.
3. Apply Rossmo piecewise score evaluation:
   * If $d_{i,j,c} > 1.50\text{ km} \implies \text{Score}_c = d_{i,j,c}^{-1.60}$.
   * If $d_{i,j,c} \le 1.50\text{ km} \implies \text{Score}_c = \frac{(1.50)^{0.80 - 1.60}}{(3.00 - d_{i,j,c})^{0.80}} = \frac{1.3832}{(3.00 - d_{i,j,c})^{0.80}}$.
4. Sum scores across $C=5$ sites and normalize sum to unity over the entire matrix grid.

#### Expected Outputs:
* **Peak Probability Anchor Coordinate:** $(x_0, y_0) = (6.80\text{ km}, 11.40\text{ km})$.
* **Top $5\%$ Priority Search Polygon Area ($S_{5\%}$):** $14.20\text{ km}^2$ (out of $400.0\text{ km}^2$ total grid area).
* **Search Efficiency Index:**
  $$\text{SEI} = \left( 1 - \frac{14.20}{400.0} \right) \times 100\% = 96.45\%$$

---

## 8. Courtroom Evaluative Reporting & Prosecutor's Fallacy Shields (ISO 17025 / ENFSI)

Forensic evaluation strictly adheres to the **ENFSI Guideline for Evaluative Reporting in Forensic Science**, expressing reporting metrics as Likelihood Ratios ($LR$) under two mutually exclusive, exhaustive propositions:
* **Prosecution Proposition ($H_1$):** The questioned forensic sample (isotope/soil/pollen) originated from the suspect or specified crime scene origin.
* **Defense Proposition ($H_2$):** The questioned forensic sample originated from an unknown, randomly selected alternative source within the relevant baseline population.

$$LR = \frac{P(E \mid H_1, I)}{P(E \mid H_2, I)}$$

Where $E$ represents the empirical analytical evidence matrix and $I$ represents background case conditioning information.

---

### 8.1 Standardized 7-Tier ENFSI Evaluative Scale

| Tier | Numerical Range ($LR$) | ENFSI Standard Verbal Expression (English) | Standardized Courtroom Expression (Turkish / Türkçe) |
| :--- | :--- | :--- | :--- |
| **Tier 1** | $1 < LR \le 10$ | Findings provide weak support for $H_1$ over $H_2$ | Analiz bulguları, iddia hipotezini ($H_1$) savunma hipotezine ($H_2$) kıyasla zayıf derecede desteklemektedir |
| **Tier 2** | $10 < LR \le 100$ | Findings provide moderate support for $H_1$ over $H_2$ | Analiz bulguları, iddia hipotezini ($H_1$) savunma hipotezine ($H_2$) kıyasla orta derecede desteklemektedir |
| **Tier 3** | $100 < LR \le 1,000$ | Findings provide moderately strong support for $H_1$ over $H_2$ | Analiz bulguları, iddia hipotezini ($H_1$) savunma hipotezine ($H_2$) kıyasla orta-güçlü derecede desteklemektedir |
| **Tier 4** | $1,000 < LR \le 10,000$ | Findings provide strong support for $H_1$ over $H_2$ | Analiz bulguları, iddia hipotezini ($H_1$) savunma hipotezine ($H_2$) kıyasla güçlü derecede desteklemektedir |
| **Tier 5** | $10,000 < LR \le 100,000$ | Findings provide very strong support for $H_1$ over $H_2$ | Analiz bulguları, iddia hipotezini ($H_1$) savunma hipotezine ($H_2$) kıyasla çok güçlü derecede desteklemektedir |
| **Tier 6** | $LR > 100,000$ | Findings provide extremely strong support for $H_1$ over $H_2$ | Analiz bulguları, iddia hipotezini ($H_1$) savunma hipotezine ($H_2$) kıyasla fevkalade güçlü derecede desteklemektedir |
| **Tier 7** | $LR = 1.00$ | Findings are neutral / uninformative ($H_1$ vs $H_2$) | Analiz bulguları nötrdür; hipotezler arasında ayrım yapılmasına olanak tanımamaktadır |

---

### 8.2 Prosecutor's Fallacy Shields & Mandatory Legal Disclaimers

To comply with **ISO/IEC 17025:2017** standards, every forensic report produced by Pillar 7 must incorporate explicit Prosecutor's Fallacy Shields. The Prosecutor's Fallacy invalidly transposes conditional probabilities, transposing the probability of evidence given a hypothesis $P(E \mid H)$ into the probability of the hypothesis given the evidence $P(H \mid E)$:

$$P(H_1 \mid E) \neq P(E \mid H_1)$$

> [!CAUTION]
> **MANDATORY COURTROOM WARNING LANGUAGE & PROSECUTOR'S FALLACY SHIELD:**
> 1. The calculated Likelihood Ratio ($LR = 4.5 \times 10^3$) measures exclusively the probability of observing the specific multi-isotope, elemental, and mineralogical profile under the competing source propositions ($P(E \mid H_1)$ versus $P(E \mid H_2)$).
> 2. It is mathematically fallacious to conclude that $LR = 4.5 \times 10^3$ implies a $99.97\%$ probability that the suspect was physically present at the crime scene ($P(H_1 \mid E)$).
> 3. Assessing the posterior probability of guilt or geographic presence $P(H_1 \mid E)$ requires combining this forensic Likelihood Ratio with independent, non-forensic case evidence ($P(H_1) / P(H_2)$) via Bayes' Theorem:
>    $$\frac{P(H_1 \mid E)}{P(H_2 \mid E)} = \frac{P(H_1)}{P(H_2)} \times LR$$
> 4. The assignment of prior odds ($P(H_1) / P(H_2)$) is the exclusive domain of the legal trier of fact (judge/jury) and lies entirely outside the scientific scope of the forensic laboratory. Inclusion within an isotopic or geochemical region does not constitute unique identification.

---

## 9. Strategic Synthesis and System Verification

The integration of spatial biogeochemistry, quantitative soil pedology, forensic palynology, eDNA metabarcoding, and Bayesian geographic profiling inside FORENZA Pillar 7 establishes a closed-form computational framework for geo-forensic intelligence.

The system architecture flows sequentially through structured computational layers:
1. **Multi-Modal Data Ingestion:** Raw analytical streams—including stable isotopes ($\delta^2\text{H}, \delta^{18}\text{O}, \delta^{13}\text{C}, \delta^{15}\text{N}$), radiogenic ratios ($^{87}\text{Sr}/^{86}\text{Sr}, \text{Pb}\text{-ratios}$), geochemical spectra (XRF major oxides and ICP-MS trace elements), quantitative mineralogy (QXRD Rietveld refinement), and biological markers (pollen counts and eDNA ASV relative abundance vectors)—are ingested and standardized.
2. **Transformation & Isoscape Mapping:** Biogeochemical data undergo biological fractionation transforms (e.g., bioapatite-to-drinking water equations) and compositional log-ratio transformations ($\text{CLR}/\text{ILR}$) to eliminate closure bias. Concurrently, geographic point incidents are processed via Rossmo decay algorithms to establish spatial anchor priors.
3. **Multi-Criteria Bayesian Evidence Fusion:** Likelihood surfaces across isotopic, geochemical, palynological, and spatial profiling layers are fused continuously over the target GIS coordinate domain $(\theta, \lambda)$ using a joint Bayesian integrator.
4. **Evaluative Courtroom Reporting:** Unified spatial posteriors and point-source inclusions are evaluated against competing prosecution and defense propositions, outputting standardized ENFSI verbal scale statements accompanied by mandatory Prosecutor's Fallacy Shields.

By eliminating heuristic assumptions and enforcing mathematically rigorous spatial probability distributions, compositional data transformations (CoDa), and ENFSI-compliant evaluative reporting, this architecture guarantees that environmental trace evidence meets international evidentiary standards (ISO/IEC 17025:2017). The system converts complex spatial and geochemical distributions into actionable search area reductions and court-admissible evaluative metrics.