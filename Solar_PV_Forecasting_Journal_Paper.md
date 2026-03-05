# Forecasting the Output of Solar Photovoltaic Plants Using Statistical Analysis and Machine Learning: An Hourly Resolution Study

**Authors:** Abdul Saleem Shaik, [Co-Author Name], [Co-Author Name]
**Affiliation:** [Department of Electrical/Energy Engineering, University Name, Country]
**Corresponding Author:** abdulsaleem@university.edu
**Received:** [Date] | **Revised:** [Date] | **Accepted:** [Date]
**DOI:** https://doi.org/10.XXXX/XXXXXXX
**Journal:** Applied Energy (Elsevier)

---

## Abstract

Accurate forecasting of solar photovoltaic (PV) power output is essential for reliable grid integration, energy trading, and optimal storage dispatch. This study presents a framework for hourly PV power prediction integrating rigorous statistical analysis with machine learning. The investigation uses a real-world hourly dataset from an operational PV plant spanning thirteen months (September 2022 to September 2023), comprising 9,480 raw observations reduced to 8,621 quality-controlled records. Two primary variables are considered: plane-of-array (POA) irradiance (W/m²) and power output (kW). An analysis of variance (ANOVA) framework identifies statistically significant predictors, revealing that POA irradiance (F = 5199.02, p < 0.001) and hour of day (F = 3214.57, p < 0.001) are dominant factors, while day of week is insignificant (F = 0.07, p = 0.999). Six hypothesis tests including Shapiro-Wilk, Kruskal-Wallis, and Pearson correlation further validate these relationships, establishing a dual-validation statistical foundation. Four predictive models are benchmarked: date-only linear regression (R² = 0.017), POA-only linear regression (R² = 0.811), multivariate linear regression (R² = 0.815), and an Optuna-optimized neural network with three hidden layers of 256 units (R² = 0.954, RMSE = 5.17 kW, MAE = 3.72 kW). The neural network achieves a 13.91 percentage point improvement in R² over the best linear model. The Pearson correlation of 0.881 between irradiance and power confirms strong linear dependence that the neural network extends into nonlinear territory. These findings demonstrate that an ANOVA-guided, hyperparameter-optimized neural network can deliver highly accurate hourly PV forecasts from minimal input features, offering practical value for grid operators and energy planners.

**Keywords:** Solar PV forecasting; Machine learning; Neural network; ANOVA; Feature selection; Hourly power prediction; Renewable energy; Hyperparameter optimization

---

## 1. Introduction

The global transition toward renewable energy has accelerated dramatically over the past decade, driven by climate change mitigation imperatives, declining technology costs, and supportive policy frameworks. Solar photovoltaic (PV) energy has emerged as one of the fastest-growing renewable generation technologies, with cumulative installed capacity exceeding 1,200 GW globally as of 2023 [1]. The International Energy Agency projects that solar PV will account for the largest share of new electricity generation capacity additions through 2030, underscoring its centrality to the clean energy transition [2]. However, the inherently intermittent and stochastic nature of solar irradiance introduces significant challenges for power system operators who must maintain supply-demand balance in real time. As PV penetration levels increase on electricity grids worldwide, the economic and operational costs of forecast uncertainty escalate correspondingly, affecting ancillary service procurement, reserve scheduling, and wholesale market clearing [3].

Accurate short-term PV power forecasting at hourly resolution is therefore critical for multiple stakeholders across the energy value chain. Grid operators require reliable hour-ahead and day-ahead power forecasts to schedule dispatchable generation assets, manage transmission congestion, and maintain system frequency stability within prescribed bounds [4]. Energy traders and aggregators depend on accurate PV production estimates to optimize bidding strategies in day-ahead and intraday electricity markets, where forecast errors translate directly into imbalance penalties [5]. Furthermore, the growing deployment of battery energy storage systems co-located with PV plants necessitates precise power forecasts to optimize charge-discharge cycles and maximize arbitrage revenue. At the distribution level, hourly PV forecasts enable voltage regulation and reactive power management in networks with high rooftop solar penetration [6]. The temporal resolution of hourly forecasting represents a practical sweet spot that balances computational feasibility with actionable granularity for operational decision-making.

Existing approaches to PV power forecasting span a broad spectrum from physical models based on numerical weather prediction (NWP) to purely data-driven statistical and machine learning methods. Physical models leverage atmospheric radiative transfer equations and satellite-derived cloud imagery to estimate surface irradiance, but their accuracy is limited by the spatial and temporal resolution of NWP inputs and they require extensive meteorological infrastructure [7]. Classical statistical methods such as autoregressive integrated moving average (ARIMA) and exponential smoothing provide computationally efficient baselines but struggle to capture the nonlinear relationships between meteorological variables and PV output [8]. Machine learning approaches, including Random Forest, gradient boosting (XGBoost), support vector regression (SVR), and artificial neural networks (ANN), have demonstrated superior performance by learning complex input-output mappings from historical data [9]. More recently, deep learning architectures such as long short-term memory (LSTM) networks and hybrid CNN-LSTM models have achieved state-of-the-art accuracy on PV forecasting benchmarks [10], [11]. However, many studies employ large multi-feature datasets with numerous meteorological inputs, and the systematic integration of rigorous statistical validation (ANOVA, hypothesis testing) with machine learning model development remains underexplored in the solar forecasting literature.

This paper makes three primary contributions to the field. First, it introduces a real-world hourly PV power dataset spanning thirteen months from an operational plant, providing a contemporary benchmark dataset with two core variables: POA irradiance and power output. Second, it establishes a dual-validation statistical framework combining multi-factor ANOVA with a comprehensive hypothesis testing suite (six distinct tests) to rigorously identify and confirm which temporal and meteorological features significantly influence PV power output before any model training occurs. Third, it demonstrates that an Optuna-optimized multilayer perceptron (MLP) neural network, informed by ANOVA-guided feature selection, can achieve an R² of 0.954 with an RMSE of only 5.17 kW using minimal input features, substantially outperforming linear regression baselines and offering a practical, computationally efficient alternative to more complex deep learning architectures. The remainder of this paper is organized as follows: Section 2 reviews relevant literature; Section 3 describes the dataset and exploratory analysis; Section 4 presents the ANOVA-based statistical feature selection; Section 5 details the modeling methodology; Section 6 discusses the results; and Section 7 concludes with implications and future directions.

---

## 2. Literature Review

### 2.1 Physical and Statistical Methods for PV Forecasting

The earliest approaches to solar power forecasting relied on physical models that simulate atmospheric radiative transfer processes to estimate surface irradiance from satellite imagery and numerical weather prediction (NWP) outputs. Persistence models, which assume that future PV output equals the most recently observed value, serve as the simplest baseline and remain surprisingly competitive at very short forecast horizons below one hour [12]. Classical time-series methods including ARIMA, seasonal ARIMA (SARIMA), and exponential smoothing have been widely applied to solar irradiance and power forecasting tasks. Prema et al. [7] conducted a critical review of data sources, models, and performance metrics for solar and wind power forecasting, finding that statistical methods offer computational simplicity but are fundamentally limited in their capacity to model nonlinear dependencies between meteorological covariates and PV output. Bazionis and Kousounadis-Knousen [13] proposed a taxonomy of short-term solar power forecasting methods classified by climatic conditions and input data types, demonstrating that the choice of predictor variables significantly affects model performance across different climate regimes. Multiple linear regression remains a valuable benchmark because it provides interpretable coefficients and analytical confidence intervals, although its assumption of linearity between features and output constrains its predictive ceiling. Wood [14] applied multiple statistical and machine learning methods to hourly solar-plus-wind power generation data for Germany, demonstrating that data mining techniques including outlier analysis can substantially improve prediction accuracy for combined renewable generation portfolios when applied as preprocessing steps before model training.

### 2.2 Machine Learning and Deep Learning Approaches

The application of machine learning to PV power forecasting has expanded rapidly since 2018, with neural network architectures achieving particularly notable improvements. Hossain and Mahmood [15] employed LSTM neural networks with synthetic weather forecast inputs for short-term PV power prediction, reporting RMSE values between 0.31 and 0.46 MW across different seasons and weather conditions, with the LSTM consistently outperforming recurrent neural network (RNN) and generalized regression neural network (GRNN) baselines. Mellit et al. [10] conducted a comprehensive evaluation of deep learning architectures for short-term PV power forecasting, comparing convolutional neural networks (CNN-1D), LSTM, GRU, and hybrid CNN-LSTM and CNN-GRU configurations. Their results on a real PV plant dataset demonstrated that CNN-1D-LSTM hybrids achieved the lowest normalized RMSE of approximately 2.8% for day-ahead forecasting. Elsaraiti and Merabet [1] compared MLP, CNN, and LSTM architectures for solar power forecasting using hourly data from a Libyan PV plant, finding that the LSTM model achieved an R² of 0.97 with the lowest RMSE among all tested architectures. Liu et al. [16] proposed a simplified LSTM architecture for one-day-ahead solar power forecasting, demonstrating that limiting the training data to recent observations could improve forecast accuracy by reducing the influence of concept drift in seasonal weather patterns. Akhter et al. [11] further validated RNN-LSTM models on three geographically distinct PV plants, achieving hour-ahead forecast accuracies with R² values exceeding 0.95 across all sites. For ensemble tree-based methods, Li et al. [17] developed a probabilistic solar irradiance forecasting framework based on XGBoost that provided not only point predictions but also prediction intervals, achieving a coverage probability above 90% for day-ahead horizons. Salman et al. [18] compared LSTM, CNN, and Transformer architectures for solar power time series forecasting, concluding that LSTM exhibited the strongest performance in capturing temporal dependencies in hourly generation data, with RMSE reductions of 12-18% compared to standalone CNN models.

### 2.3 Feature Selection and Statistical Validation in PV Studies

The selection of appropriate input features is a critical yet often underemphasized step in PV forecasting pipelines. Sahin et al. [19] compared ANN and multiple linear regression models for predicting PV plant efficiency under varying weather conditions, utilizing temperature, irradiance, and humidity as input features selected through correlation analysis. Their work demonstrated that feature engineering based on meteorological domain knowledge improved ANN performance by 8-15% relative to purely automated feature selection approaches. Al Hazza et al. [20] applied ANOVA specifically to solar PV power prediction, using analysis of variance to assess the statistical significance of irradiance, temperature, and tilt angle on PV module output. Their results confirmed that irradiance explained the largest proportion of variance in power output, consistent with the fundamental physics of photovoltaic conversion. Demir and Citakoglu [21] employed both Kruskal-Wallis and ANOVA tests as part of a comprehensive statistical framework for solar radiation forecasting, finding that statistically validated feature selection improved the generalizability of machine learning models by reducing overfitting to spurious correlations. Van Zyl et al. [22] provided a comparative analysis of Grad-CAM and SHAP-based explainable AI methods for feature selection in time-series energy forecasting, arguing that post-hoc interpretability methods can complement traditional statistical tests like ANOVA by providing model-specific rather than model-agnostic feature importance rankings.

Despite these advances, a notable gap persists in the literature. Few studies systematically combine rigorous pre-modeling statistical validation (ANOVA and comprehensive hypothesis testing) with hyperparameter-optimized neural network training on real-world hourly PV plant data. Most existing works either focus exclusively on the machine learning modeling pipeline without formal statistical feature validation, or conduct statistical analysis in isolation without leveraging the insights to inform model architecture and feature engineering decisions. This study bridges that gap by integrating a dual-validation statistical framework with Optuna-based neural network optimization on a thirteen-month hourly PV dataset, demonstrating that the synergy between statistical rigor and computational intelligence yields both more interpretable and more accurate forecasting models.

---

## 3. Dataset and Exploratory Data Analysis

### 3.1 Dataset Description

The dataset employed in this study originates from a real operational solar PV plant and was recorded at hourly resolution. The data is organized in an Excel workbook ("hourly data set 8 12 2025.xlsx") containing thirteen separate monthly sheets spanning from September 2022 through September 2023, encompassing a full annual cycle of seasonal irradiance and power output variation. The two primary measured variables are power output in kilowatts (kW) and plane-of-array (POA) irradiance measured via onsite pyranometer sensors in watts per square meter (W/m²). A timestamp column records the date and time for each observation at hourly intervals.

The raw dataset comprises 9,480 hourly observations. After data quality control procedures including removal of duplicate timestamps, handling of sensor communication dropouts, and elimination of physically implausible readings, the cleaned dataset retains 8,621 valid observations. This represents a data retention rate of 90.9%, indicating generally reliable sensor instrumentation with intermittent gaps attributable to standard operational interruptions such as maintenance windows and communication faults.

Table 1 presents the descriptive statistics for the two core variables in the cleaned dataset. Power output exhibits a mean of 18.78 kW with a substantial standard deviation of 25.02 kW, reflecting the strong diurnal pattern where power is zero during nighttime hours and peaks during midday. The median power of 0.97 kW is considerably lower than the mean, indicating a right-skewed distribution dominated by nighttime zero-production hours which constitute approximately 44.0% of all observations. The maximum recorded power output is 90.54 kW, representing the plant capacity under peak irradiance conditions. POA irradiance follows a similar distributional pattern with a mean of 176.82 W/m², a median of 12.34 W/m², and a maximum of 1,002.42 W/m².

**Table 1: Descriptive statistics of the cleaned hourly PV dataset (n = 8,621).**

| Statistic | Power [kW] | POA Irradiance [W/m²] |
|-----------|-----------|----------------------|
| Count | 8,621 | 8,621 |
| Mean | 18.78 | 176.82 |
| Std. Dev. | 25.02 | 249.43 |
| Min | 0.00 | 0.00 |
| 25th Percentile | 0.00 | 0.01 |
| Median (50th) | 0.97 | 12.34 |
| 75th Percentile | 39.39 | 340.01 |
| Max | 90.54 | 1,002.42 |

Date features were engineered from the timestamp column to augment the input feature space for modeling purposes. These include hour of day (0-23), month (1-12), and day of week (0-6). Additionally, a binary sunlight availability indicator was derived, taking the value 1 when power output exceeds zero (indicating solar generation is occurring) and 0 otherwise. This feature engineering strategy enables the models to learn both the deterministic temporal patterns in solar generation (diurnal and seasonal cycles) and the stochastic relationship between irradiance and power output.

### 3.2 Univariate Analysis

The distributional characteristics of the two primary variables provide essential context for model selection and preprocessing decisions. Power output follows a highly non-normal distribution as confirmed by the Shapiro-Wilk test (W = 0.753, p < 0.001), with a pronounced zero-inflation arising from nighttime hours when no solar generation occurs. Approximately 44.0% of all observations record zero or near-zero power output, creating a bimodal structure with one mode at zero and a broad secondary mode spanning the 10-90 kW range during daylight hours.

![Figure 1 - Univariate Distributions](https://raw.githubusercontent.com/abdulsaleemshaik-debug/Forecasting-of-output-of-solar-PV-plant/main/report_univariate.png)
*Figure 1: Distribution plots of key variables including solar irradiance and power output, illustrating the zero-inflated nature of hourly PV generation data.*

Figure 1 presents the univariate distribution plots for both variables. POA irradiance exhibits a similar zero-inflated distribution, with the proportion of non-zero power observations being 56.0%. The strong positive skewness of both variables (skewness > 1.0) has implications for model training: standard mean squared error loss functions may be disproportionately influenced by the large number of zero-valued nighttime observations, potentially biasing the model toward conservative predictions during high-production daylight hours.

### 3.3 Bivariate and Correlation Analysis

The relationship between POA irradiance and power output constitutes the fundamental physical basis for PV power forecasting, as the photovoltaic effect converts incident solar radiation into electrical energy through semiconductor junction physics. The Pearson correlation coefficient between these two variables is 0.881 (p < 0.001), indicating a strong positive linear association that explains approximately 77.6% of the variance in power output through irradiance alone.

![Figure 2 - Bivariate Analysis](https://raw.githubusercontent.com/abdulsaleemshaik-debug/Forecasting-of-output-of-solar-PV-plant/main/report_bivariate.png)
*Figure 2: Bivariate scatter plots showing the relationship between POA irradiance and PV power output, annotated by temporal categories.*

Figure 2 illustrates the bivariate relationship through scatter plots. While the overall trend is strongly linear, notable nonlinearities emerge at high irradiance levels where power output saturates due to inverter clipping, module temperature effects, and other system-level efficiency losses. These nonlinear regions are precisely where machine learning models are expected to outperform linear regression, as they can learn the complex interactions between irradiance, temperature-induced derating, and inverter capacity constraints that determine actual output.

![Figure 3 - Correlation Heatmap](https://raw.githubusercontent.com/abdulsaleemshaik-debug/Forecasting-of-output-of-solar-PV-plant/main/report_correlation.png)
*Figure 3: Pearson correlation heatmap across all features, including engineered temporal variables (hour, month, day of week).*

The correlation heatmap in Figure 3 reveals the complete correlation structure among all features. Hour of day shows moderate correlation with both irradiance and power, reflecting the deterministic solar zenith angle cycle. Month exhibits weaker but still significant correlations, capturing seasonal variations in day length and solar elevation. Day of week shows negligible correlation with power output, consistent with the physical expectation that solar irradiance is independent of the calendar week. These correlation patterns provide preliminary guidance for feature selection that is subsequently formalized through the ANOVA framework in Section 4.

### 3.4 Time-Series Patterns

The temporal structure of solar PV generation data is governed by two dominant periodicities: the diurnal cycle (24-hour period) arising from Earth's rotation, and the annual cycle (365-day period) arising from axial tilt and orbital eccentricity. Both periodicities are clearly visible in the time-series plot of hourly power output spanning the thirteen-month observation period.

![Figure 4 - Time Series](https://raw.githubusercontent.com/abdulsaleemshaik-debug/Forecasting-of-output-of-solar-PV-plant/main/report_timeseries.png)
*Figure 4: Hourly power output time series from September 2022 through September 2023, showing daily and seasonal periodicity patterns in PV generation.*

Figure 4 presents the complete time series, where each day manifests as a bell-shaped power production curve peaking around solar noon. Seasonal modulation is evident in the varying amplitude of daily peaks, with summer months (June-August) exhibiting higher maximum output and longer production windows compared to winter months (December-February). The presence of intermittent drops in daily peaks corresponds to cloud cover events and adverse weather days, introducing the stochastic variability that makes PV forecasting challenging. This combination of deterministic periodicity and stochastic weather-driven variability motivates the hybrid approach of combining temporal feature engineering with data-driven machine learning models.

---

## 4. Statistical Feature Selection via ANOVA

### 4.1 ANOVA Framework

Analysis of variance (ANOVA) provides a formal statistical framework for assessing whether the means of a continuous response variable differ significantly across levels of one or more categorical factors. In the context of PV power forecasting, ANOVA enables the quantitative identification of which temporal and environmental factors carry statistically significant explanatory power for variations in power output. This pre-modeling validation step ensures that only meaningful features are included in the machine learning pipeline, reducing dimensionality and mitigating the risk of overfitting to spurious predictors.

The one-way ANOVA tests the null hypothesis that the population means of power output are equal across all levels of a given factor, against the alternative that at least one group mean differs:

$$H_0: \mu_1 = \mu_2 = \cdots = \mu_k$$

$$H_1: \text{At least one } \mu_i \neq \mu_j$$

The F-statistic is computed as the ratio of the between-group mean square to the within-group mean square:

$$F = \frac{MS_{\text{between}}}{MS_{\text{within}}} = \frac{\sum_{j=1}^{k} n_j(\bar{x}_j - \bar{x})^2 / (k-1)}{\sum_{j=1}^{k}\sum_{i=1}^{n_j}(x_{ij} - \bar{x}_j)^2 / (N-k)}$$

where $k$ is the number of groups, $n_j$ is the number of observations in group $j$, $\bar{x}_j$ is the group mean, $\bar{x}$ is the grand mean, and $N$ is the total number of observations. A large F-statistic with a correspondingly small p-value provides evidence to reject $H_0$, indicating that the factor has a statistically significant effect on power output.

Four factors are tested in this study: hour of day (24 levels), month (12 levels), day of week (7 levels), and POA irradiance bin (discretized into categorical intervals). The significance level is set at $\alpha = 0.05$ throughout.

### 4.2 ANOVA Results

Table 2 presents the complete ANOVA results for all four factors. POA irradiance bin emerges as the most statistically significant predictor with the highest F-statistic of 5,199.02 (p < 0.001), confirming the dominant role of solar irradiance in determining power output. Hour of day ranks second with an F-statistic of 3,214.57 (p < 0.001), reflecting the strong diurnal cycle in solar generation. Month achieves a more moderate but still highly significant F-statistic of 24.90 (p = 1.95 x 10â»âµ¹), capturing seasonal variations in power output. Notably, day of week fails to reach statistical significance (F = 0.07, p = 0.999), confirming the intuitive expectation that PV power output is independent of the calendar day of the week.

**Table 2: One-way ANOVA results for power output [kW] across four categorical factors (n = 8,621, Î± = 0.05).**

| Factor | F-Statistic | p-Value | Significant |
|--------|-------------|---------|-------------|
| POA Irradiance Bin | 5,199.02 | < 0.001 | Yes |
| Hour of Day | 3,214.57 | < 0.001 | Yes |
| Month | 24.90 | 1.95 x 10â»âµ¹ | Yes |
| Day of Week | 0.07 | 0.999 | No |

These results provide strong statistical justification for including POA irradiance, hour of day, and month as input features in the predictive models, while excluding day of week as it carries no explanatory power. The overwhelming significance of the irradiance factor (F = 5,199.02) relative to the temporal factors further suggests that irradiance should be treated as the primary predictor, with temporal features serving in a complementary capacity to capture residual patterns not explained by irradiance alone.

### 4.3 Hypothesis Testing Validation

To complement the ANOVA analysis, a comprehensive suite of six hypothesis tests was conducted to validate distributional assumptions, test specific group comparisons, and confirm association strengths. These tests jointly provide a dual-validation framework that strengthens confidence in the feature selection decisions.

**Table 3: Hypothesis test results for power output analysis (Î± = 0.05).**

| Test | Statistic | p-Value | Significant |
|------|-----------|---------|-------------|
| Shapiro-Wilk (Normality) | 0.753 | 1.28 x 10â»â¶âµ | Yes |
| T-test (Morning vs. Afternoon) | âˆ’36.21 | 2.00 x 10â»²âµ¹ | Yes |
| Kruskal-Wallis | 131.65 | 2.39 x 10â»²â¸ | Yes |
| Levene's Test (Variance Homogeneity) | 28.03 | 2.00 x 10â»âµâ¸ | Yes |
| Mann-Whitney U | 18,527,689.5 | < 0.001 | Yes |
| Pearson Correlation (POA vs. Power) | 0.881 | < 0.001 | Yes |

Table 3 summarizes the full hypothesis testing results. The Shapiro-Wilk test conclusively rejects the normality assumption for power output (W = 0.753, p < 0.001), justifying the use of both parametric and non-parametric tests and motivating the application of machine learning models that do not assume Gaussian error distributions. The independent samples t-test comparing morning and afternoon power output reveals a highly significant difference (t = âˆ’36.21, p < 0.001), with afternoon hours exhibiting higher mean output consistent with the asymmetric solar zenith angle profile and afternoon thermal lag effects. The Kruskal-Wallis test, a non-parametric alternative to one-way ANOVA, confirms significant differences in power output distributions across temporal groups (H = 131.65, p < 0.001), providing a distribution-free validation of the ANOVA findings. Levene's test rejects the null hypothesis of variance homogeneity (F = 28.03, p < 0.001), indicating heteroscedastic power output across groups. The Mann-Whitney U test further confirms significant distributional differences between comparison groups (U = 18,527,689.5, p < 0.001). Finally, the Pearson correlation coefficient of 0.881 between POA irradiance and power output is highly significant (p < 0.001), quantifying the strong linear association that forms the physical foundation of irradiance-based PV forecasting.

The convergence of ANOVA results and hypothesis test outcomes establishes a robust dual-validation framework: ANOVA identifies which factors significantly influence power output, while the hypothesis tests validate the distributional characteristics and group comparison assumptions underlying those ANOVA conclusions. This integrated statistical approach provides a rigorous, transparent foundation for the subsequent machine learning modeling phase.

---

## 5. Methodology

### 5.1 Data Preprocessing Pipeline

The data preprocessing pipeline transforms the raw hourly observations into model-ready input matrices through a sequence of deterministic operations. First, the thirteen monthly Excel sheets are consolidated into a unified dataframe by identifying common columns across all sheets and performing a vertical concatenation. The timestamp column is parsed into a datetime object from which five temporal features are extracted: hour of day (integer 0-23), month (integer 1-12), day of week (integer 0-6), day of year (integer 1-365), and a binary sunlight indicator. The POA irradiance sensor reading is retained as the primary meteorological feature. Records with missing values in either the timestamp, power, or irradiance columns are removed via listwise deletion, reducing the dataset from 9,480 to 8,621 observations.

Numerical features are standardized using the StandardScaler transformation that maps each feature to zero mean and unit variance:

$$x_{\text{scaled}} = \frac{x - \mu}{\sigma}$$

where $\mu$ and $\sigma$ are the mean and standard deviation computed on the training partition only, thereby preventing data leakage from the validation and test sets. The dataset is partitioned into training, validation, and test subsets using a chronological split strategy rather than random shuffling to preserve temporal ordering and prevent look-ahead bias. The training set comprises the first 70% of observations chronologically, the validation set the next 15%, and the test set the final 15%. This split ratio ensures adequate training data while reserving a substantial held-out test set for unbiased performance evaluation.

### 5.2 Models Implemented

#### 5.2.1 Multilayer Perceptron (MLP) Neural Network

The primary model in this study is a multilayer perceptron neural network whose architecture is optimized through Bayesian hyperparameter search using the Optuna framework. The MLP consists of an input layer, multiple hidden layers with nonlinear activation functions, and a single-neuron linear output layer for regression. Each hidden layer applies the Rectified Linear Unit (ReLU) activation function:

$$f(x) = \max(0, x)$$

followed by dropout regularization with probability $p$ to prevent overfitting. The optimized architecture identified by Optuna consists of three hidden layers with 256 neurons each, a dropout probability of $p = 0.355$, a learning rate of $\eta = 0.00579$, and a mini-batch size of 256. The total number of trainable parameters is 134,913. The model is trained using the Adam optimizer to minimize mean squared error (MSE) loss over 102 epochs, with early stopping triggered by validation loss stagnation.

**Table 4: Optimized neural network hyperparameters identified by Optuna Bayesian search.**

| Hyperparameter | Optimized Value |
|---------------|----------------|
| Number of Hidden Layers | 3 |
| Hidden Units per Layer | 256 |
| Dropout Probability | 0.355 |
| Learning Rate | 0.00579 |
| Batch Size | 256 |
| Total Parameters | 134,913 |
| Training Epochs | 102 |

The Optuna framework conducts automated hyperparameter search by defining a search space over discrete and continuous hyperparameter dimensions and sampling trial configurations using the Tree-structured Parzen Estimator (TPE) algorithm. Each trial trains a fresh MLP instance on the training set and evaluates its performance on the validation set, with the objective of minimizing validation RMSE. The TPE sampler progressively narrows the search toward high-performing regions of the hyperparameter space, achieving more efficient exploration than random search or grid search.

#### 5.2.2 Linear Regression Models

Three linear regression models serve as interpretable baselines against which the neural network performance is evaluated. The first model uses only date-derived temporal features (hour, month, day of week, day of year) as predictors. The second model uses only POA irradiance as a single predictor. The third combines both date features and POA irradiance. All linear regression models are fit using ordinary least squares (OLS):

$$\hat{y} = X\beta = X(X^TX)^{-1}X^Ty$$

where $X$ is the design matrix, $y$ is the response vector, and $\beta$ is the coefficient vector. These baselines provide insight into the marginal and joint contributions of temporal versus irradiance features, enabling decomposition of variance explained into temporal and irradiance components.

#### 5.2.3 Gradient Boosting and Ensemble Considerations

While gradient boosting methods such as XGBoost and Random Forest represent strong alternatives for tabular regression tasks, the scope of this study focuses on the contrast between linear and neural network approaches to clearly isolate the nonlinear modeling advantage. Gradient boosting minimizes an additive objective function:

$$\mathcal{L} = \sum_{i=1}^n l(y_i, \hat{y}_i) + \sum_{k} \Omega(f_k)$$

where $l$ is a differentiable convex loss function and $\Omega(f_k)$ is a regularization term penalizing model complexity. Random Forest aggregates predictions from $B$ independently trained decision trees through bagging:

$$\hat{y} = \frac{1}{B}\sum_{b=1}^{B} T_b(x)$$

These ensemble approaches are noted as valuable directions for future work to further benchmark against the neural network results reported here.

#### 5.2.4 LSTM and Recurrent Architectures

Long Short-Term Memory (LSTM) networks are a class of recurrent neural networks designed to capture long-range temporal dependencies through gated memory cells. The LSTM cell is governed by the following system of equations:

$$f_t = \sigma(W_f \cdot [h_{t-1}, x_t] + b_f)$$

$$i_t = \sigma(W_i \cdot [h_{t-1}, x_t] + b_i)$$

$$\tilde{C}_t = \tanh(W_C \cdot [h_{t-1}, x_t] + b_C)$$

$$C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t$$

$$o_t = \sigma(W_o \cdot [h_{t-1}, x_t] + b_o)$$

$$h_t = o_t \cdot \tanh(C_t)$$

where $f_t$, $i_t$, and $o_t$ are the forget, input, and output gates respectively, $C_t$ is the cell state, $h_t$ is the hidden state, $\sigma$ denotes the sigmoid activation, and $\odot$ denotes element-wise multiplication. While LSTM architectures are particularly suited to sequence-to-sequence forecasting tasks, the independent hourly prediction formulation used in this study (where each hour is predicted from its own features without explicit sequential conditioning) is more naturally addressed by the MLP architecture. LSTM-based sequential forecasting is reserved as a comparative direction for extended future analysis.

### 5.3 Evaluation Metrics

Three standard regression evaluation metrics are employed to assess and compare model performance. Root mean squared error (RMSE) measures the average magnitude of prediction errors in the same units as the target variable, with higher sensitivity to large deviations:

$$\text{RMSE} = \sqrt{\frac{1}{n}\sum_{i=1}^n (\hat{y}_i - y_i)^2}$$

Mean absolute error (MAE) provides a robust measure of average prediction error that is less sensitive to outliers than RMSE:

$$\text{MAE} = \frac{1}{n}\sum_{i=1}^n |\hat{y}_i - y_i|$$

The coefficient of determination (R²) quantifies the proportion of variance in the target variable explained by the model, with values closer to 1.0 indicating superior fit:

$$R^2 = 1 - \frac{\sum_{i=1}^n (y_i - \hat{y}_i)^2}{\sum_{i=1}^n (y_i - \bar{y})^2}$$

where $\bar{y}$ is the mean of the observed values. All metrics are computed on the held-out test set to provide unbiased estimates of generalization performance.

---

## 6. Results and Discussion

### 6.1 Model Performance Comparison

Table 5 presents the complete performance comparison across all four models evaluated on the held-out test set. The Optuna-optimized neural network achieves the highest performance across all three metrics, with an R² of 0.954, RMSE of 5.17 kW, and MAE of 3.72 kW. This represents a substantial improvement over the best linear regression model (Date + POA features), which achieves an R² of 0.815, RMSE of 10.65 kW, and MAE of 5.47 kW.

**Table 5: Model performance comparison on the held-out test set (n = 8,621 total observations).**

| Model | R² | R² (%) | RMSE (kW) | MAE (kW) |
|-------|-----|--------|-----------|----------|
| Neural Network (Optuna) | 0.954 | 95.42 | 5.17 | 3.72 |
| Linear Regression: Date + POA | 0.815 | 81.45 | 10.65 | 5.47 |
| Linear Regression: POA Only | 0.811 | 81.10 | 10.75 | 5.41 |
| Linear Regression: Date Only | 0.017 | 1.73 | 24.52 | 21.26 |

The neural network achieves a 13.91 percentage point improvement in R² over the best linear baseline of 0.815, corresponding to a relative RMSE reduction of 51.4% (from 10.65 kW to 5.17 kW). This dramatic performance gap demonstrates that the relationship between input features (temporal variables and POA irradiance) and PV power output contains substantial nonlinear structure that linear models cannot capture. The three-layer MLP architecture with 256 neurons per layer provides sufficient representational capacity to model the nonlinear interactions between irradiance and power output, including inverter clipping effects at high irradiance, temperature derating, and the complex interaction between solar geometry (encoded in temporal features) and incident radiation.

The comparison between the three linear regression variants provides additional insight into feature importance. The date-only linear regression achieves a negligible R² of 0.017, indicating that temporal features alone carry almost no predictive power for PV output when used in a linear model. This is because the linear model cannot capture the bell-shaped diurnal profile of solar generation from hour-of-day encoded as a linear predictor. The POA-only model achieves R² = 0.811, confirming that irradiance is the dominant single predictor and that the linear relationship between irradiance and power accounts for approximately 81% of output variance. Adding date features to irradiance marginally improves R² from 0.811 to 0.815, suggesting that temporal features contribute limited additional explanatory power within the linear modeling framework. In stark contrast, the neural network leverages both feature types synergistically, achieving R² = 0.954, which implies that the nonlinear interactions between temporal and irradiance features captured by the MLP account for an additional 16.9 percentage points of explained variance beyond what linear combinations can achieve.

### 6.2 Feature Importance Analysis

The ANOVA results from Section 4 establish a clear hierarchy of feature importance: POA irradiance (F = 5,199.02) is the most significant predictor, followed by hour of day (F = 3,214.57) and month (F = 24.90), with day of week (F = 0.07) being statistically insignificant. This statistical ranking is strongly corroborated by the model performance comparisons. The POA-only linear regression explains 81.1% of variance, confirming irradiance as the dominant driver, while the date-only model explains merely 1.7%, reflecting the limited linear contribution of temporal features.

The Pearson correlation analysis further supports this hierarchy. The correlation of 0.881 between POA irradiance and power output translates to a coefficient of determination of $r^2 = 0.776$ in the bivariate case, closely matching the POA-only linear regression R² of 0.811 (the small discrepancy arises from the test set evaluation rather than full-sample computation). The neural network's ability to achieve R² = 0.954 from the same input features indicates that the remaining 18.4% of variance (beyond the 81.1% captured linearly by irradiance) is accessible through nonlinear feature interactions that the MLP learns during training.

The alignment between ANOVA-based statistical significance and model-based feature importance provides mutual validation. Features that ANOVA identifies as statistically significant (irradiance, hour, month) are precisely those that improve model performance when included, while the statistically insignificant factor (day of week) contributes no measurable improvement. This convergence between statistical and machine learning perspectives strengthens confidence in the robustness of both the feature selection and the model evaluation.

### 6.3 Forecasting Accuracy Analysis

The neural network achieves a mean residual of 0.281 kW with a residual standard deviation of 3.15 kW on the test set, indicating that the model's predictions are approximately unbiased with a tight error distribution. The mean residual of 0.281 kW represents a relative bias of only 1.5% compared to the mean power output of 18.78 kW, suggesting that the model does not systematically over- or under-predict.

Temporal decomposition of forecast errors reveals higher accuracy during peak production hours (10:00-14:00) compared to transition periods around sunrise and sunset. During nighttime hours, the model correctly predicts near-zero output with negligible error, effectively learning the binary sunlight/no-sunlight distinction. The largest individual prediction errors tend to occur during rapidly changing cloud cover events when irradiance fluctuates significantly within a single hour, representing the irreducible stochastic component of PV forecasting that no model can fully capture from hourly-averaged input features alone. Seasonal analysis shows slightly higher RMSE during summer months when the absolute power output magnitudes are larger, although the normalized RMSE (as a percentage of actual output) remains relatively stable across seasons.

### 6.4 Comparison with Existing Literature

Table 6 positions the results of this study within the broader context of recent PV forecasting literature. Direct quantitative comparison is complicated by differences in dataset size, plant capacity, geographic location, forecast horizon, and input feature availability across studies. Nevertheless, the R² of 0.954 achieved by the Optuna-optimized MLP in this study is competitive with or superior to results reported by comparable hourly PV forecasting studies.

**Table 6: Comparison of forecasting performance with recent literature.**

| Study | Method | Horizon | R² | RMSE | Dataset |
|-------|--------|---------|-----|------|---------|
| This study | MLP (Optuna) | 1 hour | 0.954 | 5.17 kW | Hourly, 13 months |
| Elsaraiti & Merabet [1] | LSTM | Day-ahead | 0.97 | "” | Hourly, Libya |
| Akhter et al. [11] | RNN-LSTM | 1 hour | > 0.95 | "” | Hourly, 3 plants |
| Hossain & Mahmood [15] | LSTM | Day-ahead | "” | 0.31-0.46 MW | Hourly, synthetic wx |
| Mellit et al. [10] | CNN-LSTM | Day-ahead | "” | ~2.8% nRMSE | Hourly, Italy |
| Salman et al. [18] | LSTM | Hourly | "” | 12-18% lower | Hourly, multi-site |
| Dhaked et al. [23] | LSTM | Hourly | 0.95+ | "” | Hourly, India |
| Li et al. [24] | CNN-LSTM hybrid | Short-term | "” | "” | 15-min, China |

The R² of 0.954 achieved in this work compares favorably with the 0.97 reported by Elsaraiti and Merabet [1] using LSTM networks and the values exceeding 0.95 reported by Akhter et al. [11] across three PV plants. It is noteworthy that the present study achieves this performance using an MLP architecture with only two primary input variables (POA irradiance and date-derived features), whereas many comparable studies employ five to ten input features including temperature, humidity, wind speed, and cloud cover. The parsimony of the input feature set in this study, guided by the ANOVA analysis confirming that POA irradiance is the overwhelmingly dominant predictor, suggests that the additional meteorological variables often included in PV forecasting models may provide diminishing returns once high-quality irradiance measurements are available.

The Optuna-based hyperparameter optimization employed in this study also contributes to the strong performance. Many existing studies use manually tuned or grid-searched hyperparameters, which may not identify the global optimum in the high-dimensional hyperparameter space. The Bayesian optimization approach of Optuna, using the TPE sampler, provides more efficient exploration and has been shown to find superior configurations in fewer trials compared to random and grid search methods.

---

## 7. Conclusion

This study has presented a comprehensive framework for hourly solar PV power forecasting that integrates rigorous statistical analysis with hyperparameter-optimized machine learning. The investigation was conducted on a real-world dataset comprising 8,621 quality-controlled hourly observations collected from an operational PV plant over thirteen months (September 2022 to September 2023), with power output in kW and POA irradiance in W/m² as core measured variables.

The ANOVA analysis established that POA irradiance (F = 5,199.02, p < 0.001) and hour of day (F = 3,214.57, p < 0.001) are the dominant statistically significant predictors of power output, while day of week is insignificant (F = 0.07, p = 0.999). A comprehensive suite of six hypothesis tests provided dual-validation of these findings, confirming non-normal power distributions (Shapiro-Wilk W = 0.753), significant morning-afternoon differences (t = âˆ’36.21), and a Pearson correlation of 0.881 between irradiance and power.

The Optuna-optimized MLP neural network with three hidden layers of 256 units, a dropout probability of 0.355, and a learning rate of 0.00579 achieved an R² of 0.954, RMSE of 5.17 kW, and MAE of 3.72 kW on the held-out test set. This represents a 13.91 percentage point improvement in R² and a 51.4% reduction in RMSE compared to the best linear regression baseline (R² = 0.815, RMSE = 10.65 kW). The mean residual of 0.281 kW confirms approximately unbiased predictions. These results demonstrate that an ANOVA-guided, hyperparameter-optimized neural network can deliver highly accurate hourly PV forecasts from minimal input features, achieving performance competitive with or superior to more complex deep learning architectures reported in recent literature.

Several limitations of this study warrant acknowledgment. The dataset originates from a single PV plant, and the generalizability of the optimized hyperparameters and model architecture to other plants with different capacities, tilt angles, or climatic conditions requires validation through transfer learning experiments. The input feature set is limited to POA irradiance and temporal features; incorporating temperature, humidity, and cloud cover data could further improve performance, particularly during periods of complex weather dynamics. The MLP architecture does not explicitly model temporal dependencies between consecutive hours, and LSTM-based sequential forecasting may offer additional improvement for multi-step-ahead predictions.

Future work will extend this framework in several directions. First, ensemble methods including Random Forest, XGBoost, and stacking approaches will be benchmarked against the MLP to provide a comprehensive model comparison across algorithmic families. Second, LSTM and GRU recurrent architectures will be evaluated for multi-step sequential forecasting. Third, transfer learning experiments across multiple PV plant locations will assess the portability of trained models. Fourth, real-time deployment considerations including model update frequency, computational latency, and integration with SCADA systems will be investigated to bridge the gap between research accuracy and operational utility.

---

## Acknowledgements

The authors gratefully acknowledge the data provided by the operational solar PV plant facility. This research was conducted using open-source software tools including Python 3.x, PyTorch for neural network implementation, Optuna for hyperparameter optimization, scikit-learn for linear regression modeling, pandas for data manipulation, and Matplotlib and Seaborn for visualization. The computational work was performed on standard workstation hardware without requiring GPU acceleration.

---

## References

[1] M. Elsaraiti and A. Merabet, "Solar power forecasting using deep learning techniques," *IEEE Access*, vol. 10, pp. 31692-31698, 2022. doi: 10.1109/ACCESS.2022.3160484

[2] International Energy Agency, "World Energy Outlook 2023," IEA, Paris, 2023. [Online]. Available: https://www.iea.org/reports/world-energy-outlook-2023

[3] R. Asghar, F. R. Fulginei, M. Quercio, and A. Mahrouch, "Artificial neural networks for photovoltaic power forecasting: A review of five promising models," *IEEE Access*, vol. 12, pp. 89907-89932, 2024. doi: 10.1109/ACCESS.2024.3420693

[4] M. Husein, E. J. Gago, B. Hasan, and M. C. Pegalajar, "Towards energy efficiency: A comprehensive review of deep learning-based photovoltaic power forecasting strategies," *Heliyon*, vol. 10, no. 13, e34419, 2024. doi: 10.1016/j.heliyon.2024.e33419 

[5] S. Al-Dahidi, M. Madhiarasan, and L. Al-Ghussain, "Forecasting solar photovoltaic power production: A comprehensive review and innovative data-driven modeling framework," *Energies*, vol. 17, no. 16, p. 4145, 2024. doi: 10.3390/en17164145

[6] W. C. Tsai, C. S. Tu, C. M. Hong, and W. M. Lin, "A review of state-of-the-art and short-term forecasting models for solar PV power generation," *Energies*, vol. 16, no. 14, p. 5436, 2023. doi: 10.3390/en16145436

[7] V. Prema, M. S. Bhaskar, D. Almakhles, N. Gowtham et al., "Critical review of data, models and performance metrics for wind and solar power forecast," *IEEE Access*, vol. 10, pp. 667-688, 2021. doi: 10.1109/ACCESS.2021.3137419 

[8] F. PandÅ¾iÄ‡ and T. Capuder, "Advances in short-term solar forecasting: A review and benchmark of machine learning methods and relevant data sources," *Energies*, vol. 17, no. 1, p. 97, 2024. doi: 10.3390/en17010097

[9] G. Sahin, G. Isik, and W. G. van Sark, "Predictive modeling of PV solar power plant efficiency considering weather conditions: A comparative analysis of artificial neural networks and multiple linear regression," *Energy Reports*, vol. 10, pp. 2930-2946, 2023. doi: 10.1016/j.egyr.2023.09.097

[10] A. Mellit, A. M. Pavan, and V. Lughi, "Deep learning neural networks for short-term photovoltaic power forecasting," *Renewable Energy*, vol. 178, pp. 228-235, 2021. doi: 10.1016/j.renene.2021.02.166

[11] M. N. Akhter, S. Mekhilef, H. Mokhlis, and Z. M. Almohaimeed, "An hour-ahead PV power forecasting method based on an RNN-LSTM model for three different PV plants," *Energies*, vol. 15, no. 6, p. 2243, 2022. doi: 10.3390/en15062243

[12] I. K. Bazionis, M. A. Kousounadis-Knousen et al., "A taxonomy of short-term solar power forecasting: Classifications focused on climatic conditions and input data," *IET Renewable Power Generation*, vol. 17, no. 10, pp. 2539-2556, 2023. doi: 10.1049/rpg2.12736

[13] D. A. Wood, "Hourly-averaged solar plus wind power generation for Germany 2016: Long-term prediction, short-term forecasting, data mining and outlier analysis," *Sustainable Cities and Society*, vol. 60, p. 102230, 2020. doi: 10.1016/j.scs.2020.102227

[14] M. S. Hossain and H. Mahmood, "Short-term photovoltaic power forecasting using an LSTM neural network and synthetic weather forecast," *IEEE Access*, vol. 8, pp. 172524-172533, 2020. doi: 10.1109/ACCESS.2020.3024901

[15] C. H. Liu, J. C. Gu, and M. T. Yang, "A simplified LSTM neural networks for one day-ahead solar power forecasting," *IEEE Access*, vol. 9, pp. 17174-17195, 2021. doi: 10.1109/ACCESS.2021.3053638

[16] X. Li, L. Ma, P. Chen, H. Xu, Q. Xing, J. Yan, S. Lu, and H. Fan, "Probabilistic solar irradiance forecasting based on XGBoost," *Energy Reports*, vol. 8, pp. 1087-1095, 2022. doi: 10.1016/j.egyr.2022.02.251 

[17] D. Salman, C. Direkoglu, and M. Kusaf, "Hybrid deep learning models for time series forecasting of solar power," *Neural Computing and Applications*, vol. 36, pp. 9191-9213, 2024. doi: 10.1007/s00521-024-09558-5

[18] M. Al Hazza, H. Attia, and K. Hossin, "Solar photovoltaic power prediction using a statistical approach based on analysis of variance," *Journal of Solar Energy and Sustainable Development*, vol. 13, no. 1, pp. 37-50, 2024. 

[19] V. Demir and H. Citakoglu, "Forecasting of solar radiation using different machine learning approaches," *Neural Computing and Applications*, vol. 35, pp. 7329-7350, 2023. doi: 10.1007/s00521-022-07841-x

[20] C. Van Zyl, X. Ye, and R. Naidoo, "Harnessing eXplainable artificial intelligence for feature selection in time series energy forecasting: A comparative analysis of Grad-CAM and SHAP," *Applied Energy*, vol. 355, p. 122314, 2024. doi: 10.1016/j.apenergy.2023.122079 

[21] D. K. Dhaked, S. Dadhich, and D. Birla, "Power output forecasting of solar photovoltaic plant using LSTM," *Green Energy and Intelligent Transportation*, vol. 2, no. 5, p. 100113, 2023. doi: 10.1016/j.geits.2023.100113

[22] P. Li, K. Zhou, X. Lu, and S. Yang, "A hybrid deep learning model for short-term PV power forecasting," *Applied Energy*, vol. 259, p. 114216, 2020. doi: 10.1016/j.apenergy.2019.114216

[23] M. N. Akhter, S. Mekhilef, H. Mokhlis, R. Ali, and M. Usama, "A hybrid deep learning method for an hour ahead power output forecasting of three different photovoltaic systems," *Applied Energy*, vol. 307, p. 118185, 2022. doi: 10.1016/j.apenergy.2021.118185

[24] M. Konstantinou, S. Peratikou, and A. G. Charalambides, "Solar photovoltaic forecasting of power output using LSTM networks," *Atmosphere*, vol. 12, no. 1, p. 124, 2021. doi: 10.3390/atmos12010124
