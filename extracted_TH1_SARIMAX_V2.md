Energy Consumption Forecasting through Seasonal Autoregressive Integrated Moving Average with Exogenous Regressors (SARIMAX)- Based Monitoring System for Household Appliances

A Research Presented to the Faculty of the Technological Institute of the Philippines College of Computer Studies 1338 Arlegui St., Quiapo, Manila

In Partial Fulfillment of the Requirements for the Degree of Bachelor of Science in Computer Science

By Suaverdez, Jhona Lyn P. Laxa, John Raphael G. Portodo, Geovanny V.

Adviser

Dr. Melvin Ballera

November 2025

| CHAPTER 1.......................................................................................................................................5                                                                                                |                                                                                                                                  |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| 1.1 Introduction Of The Problem..................................................................................................5                                                                                                               |                                                                                                                                  |
| 1.2.1 Research Questions.....................................................................................................9                                                                                                                   |                                                                                                                                  |
| 1.3 Research Objectives..............................................................................................................9                                                                                                           |                                                                                                                                  |
| 1.4 Significance Of The Study...................................................................................................                                                                                                                 | 10                                                                                                                               |
| 1.5 Scope And Delimitations......................................................................................................11                                                                                                              |                                                                                                                                  |
| 1.5.1 Scope of the Study..................................................................................................................                                                                                                       | 11                                                                                                                               |
| 1.5.2 Delimitations of the Study........................................................................................................12                                                                                                       |                                                                                                                                  |
| 1.6 Definition of Terms.............................................................................................................................13                                                                                           |                                                                                                                                  |
| CHAPTER 2.....................................................................................................................................17                                                                                                 |                                                                                                                                  |
| 2.1 Consolidated Summary of Reviewed Studies....................................................................................17                                                                                                               |                                                                                                                                  |
| 2.1 Integrating IoT for Appliance-Level Energy Monitoring and Forecasting.............................28                                                                                                                                         |                                                                                                                                  |
| 2.1.1 Smart Plug Technology and Measurement Accuracy................................................                                                                                                                                             | 28                                                                                                                               |
| 2.1.3 Optimal Sampling Frequency for Energy Data...........................................................30                                                                                                                                    |                                                                                                                                  |
| 2.1.4 Integrating Exogenous Variables and Local Context..................................................31                                                                                                                                      |                                                                                                                                  |
| 2.2. Enhancing Appliance-Level Energy Forecasting through Data Integrity, Cleaning, and Feature                                                                                                                                                  | Engineering.................................................................................................................. 32 |
| 2.2.1 Data Integrity Verification and Standardization for Appliance-Level Forecasting.......32                                                                                                                                                   |                                                                                                                                  |
| 2.2.2 Advanced Data Cleaning and Energy Derivation Techniques....................................33                                                                                                                                              |                                                                                                                                  |
| 2.2.3 Hourly Aggregation and Feature Engineering for Enhanced Forecasting..................35                                                                                                                                                    |                                                                                                                                  |
| 2.2.4 Final Dataset Assembly and Weather Data Integration.............................................                                                                                                                                           | 36                                                                                                                               |
| 2.3 Synthetic Data Generation Using GANs and Time-Series Generators.............................................                                                                                                                                 | 37                                                                                                                               |
| 2.3.1 Synthetic Data Generation Using GANs..................................................................................37                                                                                                                   |                                                                                                                                  |
| 2.3.2 GANs in Energy Data Reconstruction and Their Limitations...................................................39                                                                                                                              |                                                                                                                                  |
| 2.4 Forecasting Model Design and Validation for Appliance-Level Energy Consumption.......................42                                                                                                                                      |                                                                                                                                  |
| 2.4.1 Pre-Modeling Checks & Stationarity..........................................................................                                                                                                                               | 42                                                                                                                               |
| 2.4.2 SARIMAX Model Fitting with Exogenous Features and Rolling Forecasting.............43                                                                                                                                                       |                                                                                                                                  |
| 2.4.3 Forecast Accuracy, Diagnostic Validation, and User-Interpretable Insight.................44                                                                                                                                                |                                                                                                                                  |
| 2.5 System Implementation and Validation for Appliance-Level Energy Forecasting and Cost Estimation..................................................................................................................................45          |                                                                                                                                  |
| 2.5.1 Cost Estimation Methodology....................................................................................                                                                                                                            | 46                                                                                                                               |
| 2.5.2 Budget Threshold and Alert Engine..........................................................................                                                                                                                                | 47                                                                                                                               |
| 2.5.3 System Artifacts and Validation.................................................................................48                                                                                                                         |                                                                                                                                  |
| 2.6 Synthesis.............................................................................................................................                                                                                                       | 50                                                                                                                               |
| 2.7 Theoretical Framework........................................................................................................54                                                                                                              |                                                                                                                                  |
| 2.8 Conceptual Framework........................................................................................................56                                                                                                               |                                                                                                                                  |
| CHAPTER 3.....................................................................................................................................60                                                                                                 | 60                                                                                                                               |
| 3.1 Research Design................................................................................................................. Approach................................................................................................... | 60                                                                                                                               |
| 3.1.1 Research                                                                                                                                                                                                                                   |                                                                                                                                  |

| 3.1.2 Research Respondents..............................................................................................61            |    |
|---------------------------------------------------------------------------------------------------------------------------------------|----|
| A. Sampling Technique..............................................................................................................61 |    |
| B. Research Population & Sample Size....................................................................................62            |    |
| C. Methodological Rationale.....................................................................................................      | 63 |
| 3.1.3 Research Appliance Selection...................................................................................                 | 64 |
| 3.2 Data Collection Procedures.................................................................................................64     |    |
| 3.2.1 Hardware and Instrumentation...................................................................................65               |    |
| 3.2.2 Data Logging Setup...................................................................................................           | 67 |
| 3.2.3 Collected Variables.....................................................................................................68      |    |
| A. Appliance Metadata.................................................................................................                | 68 |
| B. Smart Plug Variables................................................................................................70             |    |
| C. Weather Variables....................................................................................................73            |    |
| C.1 Primary Data Source.......................................................................................73                      |    |
| C.2 Supplementary Data Source...........................................................................                              | 74 |
| D. Meralco Tariff Variables............................................................................................74             |    |
| E. Big Data Characteristics (4 V's)............................................................................................75     |    |
| 3.3 Data Preprocessing and Preparation...................................................................................81           |    |
| 3.3.0 Tuya API Log Restructuring and Variable Reconstruction.......................................................81                 |    |
| 0. Daily Energy Log Consolidation.................................................................82                                  |    |
| A. Long-to-Wide Restructuring of Tuya Datapoints...................................................................83                 |    |
| B. Selection and Mapping of Energy-Relevant Tuya Datapoints..............................................                             | 84 |
| C. Unit Scaling and Conversion to Engineering Quantities............................85                                                |    |
| D. Derivation and Initialization of Power Factor.............................................                                         | 86 |
| E. Appliance-Specific Dataset Segmentation.................................................87                                         |    |
| 3.3.1 Data Integrity Verification and Standardization..........................................................                       | 88 |
| A. Schema Alignment and Unit Validation....................................................................88                         |    |
| B. Time Standardization and Ordering.........................................................................                         | 89 |
| C. Physics Consistency and Scaling Verification..........................................................89                           |    |
| C.1 Recomputation of Power.................................................................................90                         |    |
| C.2 Recomputation of Cumulative Energy.............................................................90                                 |    |
| C.3 Comparison and Tolerance Rule.....................................................................91                              |    |
| C.4 Validation Ranges and Plausibility Screening.................................................                                     | 91 |
| C.5 Power Factor Consistency Check...................................................................                                 | 92 |
| 3.3.2 Data Cleaning and Energy Derivation........................................................................92                   |    |
| A. Interval Energy Computation....................................................................................92                  |    |
| B. Handling Gaps, Resets, and Outliers........................................................                                        | 94 |
| C Daily Consistency Check..........................................................................................                   | 96 |
| 3.3.3 Data Aggregation and Feature Construction..............................................................97                       |    |
| A. Hourly Resampling...................................................................................................97             |    |

| B. Validation of Weather Data.......................................................................................98                   |                                                                                    |
|------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| C. Derived Time and Historical Features......................................................................99                          |                                                                                    |
| 3.3.4 Final Data Transformation........................................................................................100               |                                                                                    |
| A. Weather Synchronization.......................................................................................100                     |                                                                                    |
| B. Final Variable Structure for Modeling.....................................................................101                         |                                                                                    |
| 3.4 Synthetic Data Generation Using TimeGAN....................................................................................102       |                                                                                    |
| 3.4.1 Preprocessing for Training the Improved TimeGAN+............................................................103                    |                                                                                    |
| A. Outlier Removal..................................................................................................................103  |                                                                                    |
| B. Min-Max Normalization......................................................................................................           | 106                                                                                |
| C. Daily Segmentation.............................................................................................................107    |                                                                                    |
| 3.4.2 Improved TimeGAN Architecture...........................................................................................109        |                                                                                    |
| A. Components of the Improved TimeGAN.............................................................................110                    |                                                                                    |
| B. Multi-Head Self-Attention in the Recovery Module..............................................................111                     |                                                                                    |
| C. Loss Functions....................................................................................................................112 |                                                                                    |
| D. Training Hyperparameters..................................................................................................            | 112                                                                                |
| 3.4.3 Generating Synthetic Days....................................................................................................113   |                                                                                    |
| A. Number of Synthetic Days Generated................................................................................                    | 116                                                                                |
| B. Characteristics of Raw Synthetic Output.............................................................................116               |                                                                                    |
| 3.4.4 Monthly Energy Scaling Using Meralco Bills.........................................................................                | 117                                                                                |
| A. Compute Synthetic Monthly Energy....................................................................................118               |                                                                                    |
| B. Compute the Scaling Factor...............................................................................................             | 121                                                                                |
| C. Apply Scaling to the Synthetic Month.................................................................................123              |                                                                                    |
| D. Scaling Applied to 10-Minute Interval Values.....................................................................                     | 124                                                                                |
| E. Preservation of 10-Minute Structure After Scaling..............................................................126                    |                                                                                    |
| 3.4.5 Appliance-Level Reconstruction............................................................................................126      |                                                                                    |
| A. Computing Real Appliance Energy                                                                                                       | Shares.........................................................................126 |
| B. Allocating the Synthetic Aggregated Load to Appliances...................................................                             | 127                                                                                |
| C. Aggregating the Appliance-Level Synthetic kWh to Hourly Resolution..............................                                      | 129                                                                                |
| 3.4.6 Post-Generation Validation....................................................................................................129  |                                                                                    |
| A. Denormalization of Synthetic Data......................................................................................130            |                                                                                    |
| B. Statistical Comparison........................................................................................................130     |                                                                                    |
| C. PCA Visualization...............................................................................................................      | 131                                                                                |
| D. t-SNE Visualization.............................................................................................................132   |                                                                                    |
| E. Synchronization of Real, Synthetic, and Weather Datasets...............................................                               | 133                                                                                |
| 3.5 Modeling Approach............................................................................................................135     |                                                                                    |
| 3.5.1 Pre-Modeling Checks...............................................................................................136              |                                                                                    |
| A. Stationarity Assessment.........................................................................................136                   |                                                                                    |
| 3.5.2 Model Estimation and Fitting....................................................................................138                |                                                                                    |
| A. SARIMAX Model Structure.....................................................................................138                       |                                                                                    |
| B. Model Identification and Parameter Selection........................................................140                               |                                                                                    |

| C. Exogenous Variables and Feature Vector..............................................................143                                                   |     |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------|-----|
| D. Forecast Horizon and Rolling-Origin Strategy.......................................................                                                       | 143 |
| E. Data Splitting and Evaluation Window...................................................................                                                   | 144 |
| 3.5.3 Model Evaluation and Error Analysis.......................................................................                                             | 145 |
| A. Evaluation Design and Performance Metrics.........................................................145                                                     |     |
| B. Residual Diagnostics and Model Validation...........................................................                                                      | 146 |
| C. Visualization of Error Patterns................................................................................148                                        |     |
| 3.6 System Implementation.....................................................................................................                               | 148 |
| 3.6.1 Cost Estimation Methodology..................................................................................                                          | 148 |
| A. Inputs and Time Base............................................................................................                                          | 148 |
| B. Hourly Cost Translation..........................................................................................148                                      |     |
| C. Top-Consuming Appliances (Forecast Perspective)..............................................149                                                          |     |
| D. System Artifacts.....................................................................................................149                                  |     |
| 3.6.2 Budget Threshold and Alert Engine.........................................................................                                             | 150 |
| A. Budget Constructs..................................................................................................150                                    |     |
| B. Status Logic...........................................................................................................                                   | 151 |
| C. Alert Policies..........................................................................................................                                  | 152 |
| D. Execution Schedule...............................................................................................                                         | 152 |
| 3.6.3 System Validation.....................................................................................................153                              |     |
| 3.6.4 Prototype...............................................................................................................................154            |     |
| References.................................................................................................................................................. | 158 |

## 1.1 Introduction Of The Problem

Energy consumption is one of the leading contributors to global environmental degradation and climate change, affecting  millions  of  lives,  especially  in  underserved  regions.  The proposed energy  monitoring  and  forecasting  system  has  a  significant  social  impact  in  addressing  the financial  burden  of  electricity  costs  for  Filipino  households,  particularly  low-  to  middle-income families. According to the Philippine Statistics Authority (2023), electricity expenses represent one of  the  largest  monthly  expenditures  for  households,  with  rates  among  the  highest  in  Southeast Asia,  averaging ₱ 11.743  per  kilowatt-hour  in  2025  (GlobalPetrolPrices.com,  2025).  The  lack  of real-time  visibility  into  appliance-level  consumption  leaves  consumers  unable  to  identify  which devices  contribute  most  to  their  energy  bills,  leading to inefficient consumption, unexpected high bills, and wasted energy. As Respicio &amp; Co. (2024) noted, these unresolved issues underscore the need for  more  transparent  energy management practices, particularly in residential areas. These challenges directly relate to SDG 7 (Affordable and Clean Energy), which emphasizes the need to ensure access to affordable, reliable, sustainable, and modern energy for all, and SDG 13 (Climate Action),  which  calls  for  efforts  to mitigate the effects of climate change through more sustainable energy practices (Bertheau, 2024).

In  the  Philippines,  where  energy  consumption  patterns  are  often  misjudged,  particularly among households in underserved regions, the introduction of real-time, appliance-level monitoring systems  becomes  crucial.  Research  has  shown  that  households  significantly  misestimate  their energy usage, especially with  regard to lighting and cooling devices (Baidoo et al., 2021). These gaps  in  perception  demonstrate  the  need  for  a  granular  energy  monitoring  system  that  allows consumers to visualize and control their consumption more effectively.

Despite  the  growing  energy  demand  driven  by  modern  appliances,  remote  work,  and increasingly  digital  lifestyles,  traditional electric meters still only provide a single monthly reading, with  no  breakdown  by  appliance  or  usage  behavior.  The  shift  toward  smart  grids  and  more sustainable  energy  practices  presents  an  opportunity  to address the growing demand for energy

## CHAPTER I INTRODUCTION

while reducing its  environmental  impact.  However,  residential  energy  management  remains underdeveloped,  particularly in developing  countries like the Philippines.  Real-time  energy consumption  forecasting  and  cost  estimation  are  essential  for  efficient  resource  allocation  and cost-saving strategies, yet the technology remains underutilized.

In tackling this issue, forecasting models such as ARIMA have long been used for energy consumption  prediction.  In  the  Philippines,  studies  by  Caw-it  and  Talirongan  (2025)  and  Uayan (2024)  have  demonstrated  the  effectiveness  of  ARIMA-based  models  in  predicting  short-term energy  consumption.  ARIMA  models are particularly  useful  for  capturing  seasonal  consumption patterns, making them beneficial for residential energy planning. However, ARIMA has limitations, particularly  its  inability  to  account  for  dynamic  seasonality  and  external  factors  such  as ambient temperature,  time  of  day,  and holidays, which are critical variables that significantly affect energy consumption patterns. This limitation makes ARIMA inadequate for long-term energy forecasting, where seasonal variations play a significant role.

Building  upon ARIMA's shortcomings, SARIMAX (Seasonal ARIMAX) addresses some of these  limitations  by  integrating  seasonal  adjustments  and  external  variables,  making  it  a  more robust  tool for energy forecasting. Studies by Cecílio, Rodrigues, Barros, and de Sá (2025) show that  SARIMAX  can improve forecasting accuracy by considering factors like weather conditions and  tariff rates,  which  are  essential  for  forecasting  energy  consumption  costs.  Despite  its improvements,  SARIMAX  still  faces  challenges  in  handling  dynamic  seasonality  adjustments, which are necessary for addressing fluctuations  caused  by  seasonal  weather changes or varied appliance usage during peak periods.

To  address the challenge of having only two months of high-frequency household energy data,  this  study  integrates  an  Improved  TimeGAN  architecture  to  reconstruct  the missing twelve months of 10-minute interval consumption. Recent advancements in time-series data augmentation highlight  the  capability  of  GAN-based  models  to  generate  realistic  synthetic  sequences  that preserve temporal structure,  particularly  under  limited-data conditions. For example, Zhang et al. (2025)  demonstrate  that  TimeGAN-based augmentation can effectively mitigate imbalanced and small-sample distributions in building electricity datasets by generating high-quality virtual samples

that align closely with real consumption patterns. Building on this direction, the enhanced model of Tang  et  al.  (2025)  incorporates  a  multi-head  self-attention  mechanism  in  the  recovery  network, enabling more accurate extraction of long-range consumption dependencies even under small-sample constraints. This approach is further supported by the findings of Chen et al. (2024), who  show  that  deep  generative  models  can  significantly  improve  data  representativeness  and stability  when  real-world  time-series  samples  are  limited,  noisy,  or  incomplete.  By  generating realistic  daily  household  load  profiles  and  later  aligning  them  with  actual  Meralco  monthly  kWh values,  the  Improved  TimeGAN  provides  the  complete  year-long  dataset  required  for  accurate appliance-level forecasting and cost estimation using SARIMAX.

This  gap  in  existing  research  presents  an  opportunity  for  innovation.  While  several international and local studies (Caw-it and Talirongan, 2025; Khan and Ahmad, 2023; Jamil et al., 2024; Nguyen and Lee, 2023; Zhang et al., 2022) have demonstrated the technical feasibility of energy forecasting systems, many of these models remain either too complex, internet-dependent, or  inaccessible  for  ordinary  households.  These  limitations  make  them  less  suitable  for  Filipino families,  sectors  that  are  currently  underserved  by  existing  energy  technologies.  By  integrating appliance-level  forecasting  and  applying  SARIMAX  on  high-frequency  10-minute  data  collected through  commercially  available  Wi-Fi-enabled  devices  with  built-in  energy  monitoring,  we  bridge the  gap  between  complex  industrial  solutions  and  limited  household  tools.  Additionally,  we introduce  a  budget  alert  system  to  notify  users  when  their  energy  consumption  exceeds  preset limits,  providing  real-time  cost  management  and  control  over  electricity  bills.  By  integrating appliance-level  forecasting  and  applying  SARIMAX  on  high-frequency  10-minute  data  collected through  commercially  available  Wi-Fi-enabled  devices  with  built-in  energy  monitoring,  we  bridge the  gap  between  complex  industrial  solutions  and  limited  household  tools.  Additionally,  we introduce  a  budget  alert  system  to  notify  users  when  their  energy  consumption  exceeds  preset limits, providing real-time cost management and control over electricity bills.

## 1.2 Problem Statement

Many  Filipino households  continue  to  face  challenges  in  managing  their  electricity expenses  due  to  the  limited  availability  of  practical  tools  that  can  monitor,  analyze,  and  predict energy  consumption  at  the  appliance  level.  Conventional  electric  meters  provide  only  a  total

monthly figure, which leaves users unaware of how much electricity each appliance contributes to their  overall  consumption.  This  lack  of  visibility  hinders  their  ability  to  identify  high-consuming devices,  manage  their  budgets  effectively,  and  make  well-informed  decisions  that  could  help reduce energy costs.

Most  households  are  unable  to  monitor  the  timely  energy  consumption  of  individual appliances  with  granular  detail,  which  makes  it  difficult  to  determine  which  specific  devices  are responsible  for  driving  up  their  electricity  bills.  Families  often rely on assumptions or guesswork, such as believing that lighting contributes most to their expenses, when in reality large appliances like  refrigerators, air conditioning units, or computers may account for the majority of energy use. Without accurate, appliance-level monitoring from a high-frequency source, households are left in the  dark  about  their  true  consumption  patterns,  limiting  their  capacity  to  make  adjustments  that could lower their costs.

Another  pressing  problem  is  the  absence  of  budget  tracking  and  alert  systems  for household  energy use. Consumers generally have no mechanism that informs them when their electricity consumption is nearing or exceeding a self-imposed budget for the day, week, or month. As a result,  many  households  are  caught  off  guard  by  unexpectedly  high  bills  at  the end of the month.  This  not  only  disrupts  financial  planning  but  also  creates  stress  for  families,  particularly those from low-income to middle-income backgrounds who must manage tight budgets.

In  addition, households currently lack access to forecasting tools that could provide them with  a  reasonable  estimate  of  their  future  electricity  costs.  Without  the  ability  to  project  their upcoming bills  based  on  current  usage  trends  and  seasonal  patterns,  consumers  are  unable  to anticipate  expenses  or  adjust  their  energy  consumption  proactively.  This  challenge  is  further compounded  by  the  limited  availability  of  long-term  appliance-level  datasets,  which  this  study addresses by reconstructing additional months of historical data using a generative model.

## 1.2.1 Research Questions

This study is guided by the following specific research questions:

1. How  can  a  high-frequency  energy  monitoring  system  using  Tuya  smart  sockets  help Filipino households track and manage their appliance-level energy consumption?
2. How can Improved TimeGAN be used to reconstruct missing historical appliance-level data to support accurate SARIMAX forecasting?
3. How can the SARIMAX algorithm be applied to forecast hourly electricity consumption and estimate the associated costs for households?
4. How can a budget tracking and alert system be designed to notify users when they are projected to exceed cost limits?

## 1.3 Research Objectives

The  main  objective  of  this  study  is  to  implement  a  low-cost  home  energy  monitoring system  that  provides  high-frequency  appliance-level  data  forecasting,  budget  tracking,  and  cost estimation using Tuya smart sockets and the SARIMAX algorithm.

1. To  design  a  high-frequency  monitoring  system  using  Tuya  smart  sockets  that measures and  displays  the  energy  consumption  of  individual  appliances  through  an  interactive dashboard.
2. To  generate  a  complete  year-long  appliance-level  dataset  for  forecasting  model  training and  validation  by  reconstructing  missing  historical  data  using  an  Improved  TimeGAN architecture.
3. To implement a forecasting system for hourly energy consumption based on the SARIMAX algorithm, with cost estimation derived from the forecasted values.
4. To develop a budget tracking feature that allows users to set daily electricity consumption limits and integrates an alert system that notifies them when usage approaches or exceeds these thresholds.

This  study  proposes  the  Home  Energy  Consumption  Forecasting  with  High-Frequency Tuya  Smart  Socket  Integration  and  Enhanced  SARIMAX Forecasting Algorithm, a low-cost and accessible  platform  that integrates algorithmic intelligence into an energy monitoring system. The proposed system employs commercially available Tuya smart sockets with Wi-Fi connectivity to enable plug-and-play, appliance-level monitoring and cloud-assisted data acquisition. The forecasting  component  uses  the  SARIMAX  model  to  forecast  hourly  appliance-level  electricity

consumption and cost for the next twenty-four hours.This model is trained on a 14-month dataset consisting  of  two  months  of  real  appliance-level  readings  and  twelve  months  of  synthetically reconstructed  data.  The  system  features  a web dashboard with visualizations, detailed logs, and budgeting  tools,  complemented  by  a  mobile  interface  that  provides  simplified  notifications  on forecasted  electricity  costs  and  appliance-level  contributions.  Through  this integrated design, the system  delivers  a  scalable,  and  user-centered  approach  to  household  energy  visualization  and forecasting.

## 1.4 Significance Of The Study

Upon completion of this thesis,  homeowners are expected to benefit through visibility of their  future  appliance-level  electricity  consumption.  By  having  clearer insights into which devices contribute  most  to  their  energy  usage,  they  can  make  more  informed  decisions  in  scheduling appliance operations, preventing overconsumption, and ultimately lowering their monthly electricity expenses.

Researchers  will  be  able  to  apply  their  knowledge  in  computer  science,  particularly  in integrating  commercial  IoT  devices  such  as  Tuya  smart sockets, building web-based visualizers, and implementing forecasting algorithms such as SARIMAX and rule-based alerts.

Homeowners will have access to a user-friendly platform that displays forecasted data on energy consumption per appliance. This empowers users to track their electricity behavior and take immediate action to save costs.

Small  business  owners  will  gain  a  more  reliable  way  to  monitor  electricity  usage  per appliance  compared to relying  solely  on  a  sub-meter,  which  only  shows  total consumption. This feature  can  help  identify  which  equipment  consumes  the  most  power,  and  support  cost-saving decisions to improve small business operations.

Students and schools can use this research as a reference for developing similar projects in  electronics,  computer  science,  or  environmental  studies.  It  demonstrates  how  forecasting algorithms can be used to solve real-world problems and promote energy awareness.

Future  researchers  can  build  upon  this  project  as  a  foundation  for  more  advanced systems,  such  as  web-based  energy  dashboards,  predictions  for  cost  estimation,  or  integration with home automation platforms.

The  environment  will  benefit  from  the  system  by  encouraging  responsible  energy  use through increased awareness and reduced unnecessary electricity consumption.

## 1.5 Scope And Delimitations

This section outlines the boundaries, extent, and limitations of the system developed in this study.  It  clarifies  what the research includes, such as the design of an appliance-level monitoring and forecasting  system  using  Tuya  smart  sockets,  synthetic  data  reconstruction,  and  SARIMAX forecasting, and what falls outside its intended coverage.

## 1.5.1 Scope of the Study

This  study  focuses  on  the  design,  development,  and  evaluation  of  an  appliance-level Home Energy Consumption Forecasting and Cost Estimation System that integrates Tuya Wi-Fi Smart Sockets, a cloud-based data pipeline, and a SARIMAX forecasting algorithm. The system is specifically  designed  for  Filipino  households,  which  operate  under  the  Meralco  residential  tariff structure.  Its  purpose  is to provide monitoring, short-term cost forecasting, and budget alerts that can help users manage electricity consumption more efficiently and gain awareness of their energy usage patterns.

The  system  measures  appliance-level  electricity  usage  through  SMATRUL  Tuya  Smart Sockets, which transmit data to the Tuya Cloud API at ten-minute intervals. The recorded data are retrieved  by  a  Python-based  logger  hosted  on a Microsoft Azure Virtual Machine (VM) to ensure continuous  operation  even  without  local  computer  access.  The  system  also  integrates  hourly weather  data  from  OpenWeatherMap  and  Meteostat  APIs,  along  with  monthly  tariff  rates  from official Meralco advisories. In addition, because only two months of high-frequency measurements were available, the study integrates a synthetic data generation stage using Improved TimeGAN to reconstruct  the  remaining  historical  months needed for seasonal forecasting. These datasets are

combined  to  form  the  inputs  for  the  SARIMAX  (Seasonal  AutoRegressive  Integrated  Moving Average  with  eXogenous  Variables)  model,  which  forecasts  hourly  appliance-level  electricity consumption and cost for the next twenty-four hours. The resulting forecasts are visualized on a dashboard  that  presents  historical  and  projected  energy  data,  estimated  costs,  top-consuming appliances, and budget status alerts.

Model  performance  is  assessed  through  standard  quantitative  metrics,  including  Mean Absolute  Error  (MAE),  Root  Mean  Square  Error  (RMSE),  Mean  Absolute  Percentage  Error (MAPE),  and  Coefficient  of  Determination  (R²).  Diagnostic  tests  such  as  the  Autocorrelation Function (ACF), Partial Autocorrelation Function (PACF), and Ljung-Box Q-test are used to confirm that  model  residuals  behave  as  white  noise,  validating  model  adequacy.  Testing  is  limited  to selected  household  appliances  chosen  for  their  common  and  practical  relevance  in  everyday energy consumption. The forecasting horizon is short-term, focusing on hourly forecasts within a 24-hour window to support daily household energy management and budget planning.

The  study's  scope  is  methodological  rather  than  demographic.  It  does  not  seek  to generalize  findings  to  a  broader  population  of  households  or  regions.  Instead,  it  focuses  on demonstrating  a  replicable  methodological  framework  for  appliance-level  forecasting  and  cost estimation using real data from a single monitored household. The aim is to validate the system's capability  and  reliability,  which  can  later  be  adapted  and  scaled to other households with similar data availability. The system is evaluated using data collected from a single residential household to demonstrate feasibility, reliability, and methodological validity.

## 1.5.2 Delimitations of the Study

The study is limited to a single participating household, and the findings are not intended to represent electricity consumption behavior across all households in Parañaque, Metro Manila. The system is  also  limited  to  devices  compatible  with  Tuya  Smart  Sockets operating within standard single-phase 220-240 V AC electrical systems. It does not include automatic appliance control or remote shutdown features, as its purpose is limited to monitoring, forecasting, and notification. The synthetic dataset generated through TimeGAN  serves only as a reconstructed historical approximation  and  not  as  a  replacement  for  real  consumption  data.  Its  use  is  limited  to  model training  and  is  validated  statistically  to  ensure  realism.  The forecasting component employs only

the SARIMAX algorithm, excluding more complex deep learning methods such as LSTM or CNN to maintain interpretability and  computational  efficiency. The  implementation  is  geographically restricted to Metro Manila and nearby areas under Meralco's tariff structure; therefore, results may not directly apply to regions with different pricing schemes or energy policies.

Furthermore, the system cannot monitor appliances that are not individually connected to a Tuya  Smart  Socket,  nor  can  it  handle  high-voltage  or  industrial  environments.  Its  performance depends on the continuity of Wi-Fi connectivity and data logging; interruptions, power outages, or user-related  behavior  changes  may  introduce  gaps  in  data  collection.  Finally,  while  the  current version  focuses  on  data  visualization,  forecasting,  and  alerting, several features, such as mobile app integration, exportable consumption logs, and enhanced long-term analytics, are identified as potential future enhancements and fall outside the present scope of this prototype.

## 1.6 Definition of Terms

- 10-Minute Resolution The frequency of smart plug recording, yielding 144 data points per day.
- Appliance-Level Monitoring The measurement and tracking of energy consumption for each  individual  household  device  to  identify  which  appliances  contribute  most  to  total usage.
- Augmented Dickey-Fuller (ADF) Test A statistical method used to determine if a time series is stationary by testing for the presence of a unit root.
- Condition Vector (c) Optional input that encodes attributes such as weekday/weekend or season, guiding the Generator to produce context-specific sequences.
- Cumulative Energy Reset An anomaly where the smart plug resets its kWh counter to zero, requiring correction during preprocessing.
- Differencing  A  preprocessing  technique  that  makes  a  time  series  stationary  by subtracting previous values from current ones.
- Discriminator (D) A network that distinguishes real sequences from synthetic ones to guide adversarial learning in GANs.
- Dynamic  Seasonality  Adjustment  An  adaptive  method  that  modifies  seasonal parameters of a forecasting model in real-time based on changing consumption patterns.

- Embedding Network (E) - A module in TimeGAN that encodes real time-series data into compact latent representations.
- Energy Budget Threshold A user-defined consumption or cost limit that triggers alerts.
- Exogenous  Feature  Vector  (X )  A  set  of  external  variables  used  by  SARIMAX  to improve forecasting accuracy.
- Exogenous  Variables  (Exog)  External  factors  such  as  temperature,  humidity,  and rainfall that influence energy consumption but are not part of the main time series.
- Fallback  Energy Estimation A  physics-based  method  for  estimating  missing  interval energy using the average of adjacent power readings.
- Forecast Error Metrics Measures such as MAE, RMSE, and MAPE used to evaluate model performance.
- Forecast Horizon The future time span for which predictions are made, set to 24 hours in this study.
- Generator (G) A neural  network  component of  TimeGAN that creates synthetic latent sequences from random noise and optional condition vectors.
- Hourly Aggregation The conversion of 10-minute intervals into hourly energy totals for SARIMAX modeling.
- Hybrid  Validation  Rule  A  rule  combining  actual  cumulative  differences  and  fallback estimation to derive the most reliable interval energy value.
- Improved TimeGAN -  A  time-series  generative  adversarial  network used to reconstruct missing  historical  appliance-level  energy  data,  producing  synthetic  load  profiles  that preserve temporal structure and distributional characteristics of real measurements.
- Kurtosis A measure of the 'peakedness' or tail heaviness of a distribution.
- Latent Vector (z) - A random input fed into the Generator to produce synthetic sequences with varied patterns.
- Mean Absolute Percentage Error (MAPE) A metric that measures forecasting accuracy by calculating the average percentage difference between predicted and actual values.
- PCA  (Principal  Component  Analysis) A dimensionality  reduction  technique  used  to compare structural similarity between real and synthetic time-series data.
- Recovery Network (R) A module that reconstructs full time-series sequences from latent embeddings; the 'decoder' of TimeGAN.

- Rolling-Origin  Evaluation  A  model  validation  technique  that  retrains  and  tests  the forecasting model on updated datasets to simulate real-world forecasting conditions.
- Root Mean Square Error (RMSE) A measure of forecasting performance that calculates the square root of the average squared difference between predicted and observed values.
- SARIMAX  (Seasonal  AutoRegressive  Integrated  Moving  Average  with  eXogenous Variables)  A forecasting  model  that  extends ARIMA by including seasonal effects and external variables to predict energy consumption.
- Scaling Factor (α) A  multiplier  applied  to  synthetic  daily  sequences  to  align  the total monthly energy with real electricity bills.
- Seasonality A recurring and predictable pattern in time series data that repeats over a fixed period such as daily or weekly cycles.
- Seasonal Period (s) The number of time steps that complete one seasonal cycle; for daily cycles, s = 24 for hourly forecasting.
- Skewness A measure of asymmetry in the distribution of a time-series dataset.
- Stationarity  A property  of  a time series where its mean and variance remain constant over time, required for SARIMAX modeling.
- Supervisor Network (S) A network that enforces temporal consistency by predicting the next latent step, improving sequence realism.
- Synthetic Load Profile -A reconstructed  time-series  generated  using  Improved TimeGAN to extend real appliance-level measurements into a complete year-long dataset for forecasting.
- Synthetic Month Scaling The process of adjusting GAN-generated load profiles so that the monthly kWh totals match the actual Meralco billing values.
- Time-Series Generative Adversarial Network (TimeGAN) -A neural network architecture combining adversarial learning and supervised  sequence  modeling  to generate realistic time-series sequences.
- t-SNE (t-Distributed Stochastic Neighbor Embedding) A visualization technique that assesses whether real and synthetic sequences cluster similarly in non-linear space.
- Tuya Smart Socket -A Wi-Fi-enabled device that measures real-time power consumption and transmits energy data to the cloud for monitoring and forecasting.

## CHAPTER II REVIEW OF RELATED STUDIES

This chapter presents a review of existing studies and literature that form the foundation of the  research.  It  explores  prior  works  on  IoT-based  energy  monitoring,  cloud  data  management, optimal  sampling  frequency,  integration  of  exogenous  variables,  and  appliance-level  energy forecasting.  Each section highlights how previous studies have contributed to the development of energy  forecasting systems,  identifies existing gaps, and  explains how  the  present  study addresses  these  gaps  through  an  integrated,  appliance-level  forecasting  and  cost  estimation framework tailored to the Philippine residential context.

## 2.1 Consolidated Summary of Reviewed Studies

This section presents a consolidated summary of all studies reviewed across the previous subsections  on  IoT-based  appliance-level energy  monitoring, cloud data pipelines,  optimal sampling  frequency,  preprocessing  and  data  integrity,  feature  engineering,  SARIMAX-based forecasting, synthetic data generation using GANs and time-series generators, cost estimation, and system implementation. Integrated in Table 2.1 the core variables, methods, parameters, and key findings  of  each  referenced  work  into  a  unified  format.  This  summary  provides  a  concise comparative  view  of  the  diverse  methodologies  and  technological  approaches  that  inform  the design of this study's data collection pipeline, preprocessing framework, TimeGAN-based synthetic data reconstruction, forecasting model design, and appliance-level cost estimation components.

| Author & Year               | Variables Used                                                       | Parameters                                                      | Methods Applied                                                                | Key Findings                                                                                                                                           |
|-----------------------------|----------------------------------------------------------------------|-----------------------------------------------------------------|--------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| Condon et al. (2023)        | Real-time appliance-level voltage current power readings via AWS IoT | Smart plug deployment at 10-second sampling and cloud ingestion | Sonoff POW R2 installation AWS IoT Core integration continuous data monitoring | Demonstrated that low-cost smart plugs can reliably capture high-frequency appliance data and that cloud platforms support stable real-time ingestion. |
| Ahmed et al. (2022)         | Smart plug power current voltage telemetry across campus devices     | Campus-scale IoT deployment and multi-appliance monitoring      | Sonoff POW R2 deployment and cloud backend integration                         | Validated the practicality and scalability of commodity smart plugs for continuous multi-device campus-wide monitoring.                                |
| Santos et al. (2023)        | Appliance-level smart plug readings under dynamic load               | Measurement accuracy and error detection                        | Controlled experiments assessing smart plug precision                          | Identified measurement errors around ±3 percent showing the need for correction when loads fluctuate.                                                  |
| Athanasioulas et al. (2024) | High-resolution 10-second appliance-level energy data                | Ultra-high-frequency sampling for appliance pattern capture     | Analysis of the Plegma dataset                                                 | Showed that very high sampling resolution reveals micro-level load signatures that improve detection and forecasting.                                  |

| Aguirre-Fraire et al. (2024)   | One-minute appliance-level energy data with temperature humidity wind          | IoT and weather-integrated dataset design                  | Smart meter data combined with OpenWeatherMap weather API                        | Demonstrated that merging granular weather and energy data improves forecasting dataset quality.                                                                            |
|--------------------------------|--------------------------------------------------------------------------------|------------------------------------------------------------|----------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Hernandez et al. (2020)        | Household energy data at 5-20 minute intervals                                 | Impact of sampling frequency on accuracy                   | Comparative analysis of multiple sampling intervals                              | Found that sampling intervals longer than ten minutes cause significant information loss and recommended using five minutes or lower for accuracy.                          |
| Petralia et al. (2023)         | Smart meter load readings for NILM and appliance detection                     | Evaluation of optimal sampling intervals                   | Comparison of 10-minute versus higher-frequency readings                         | Concluded that a ten-minute interval is optimal for balancing resolution and data volume in NILM applications.                                                              |
| Chen et al. (2025)             | Temperature humidity electricity price aggregate load and appliance-level data | SARIMAX with exogenous inputs and structured preprocessing | Data normalization timestamp validation SARIMAX modeling and feature engineering | Found that weather-based exogenous variables and rigorous preprocessing significantly improve forecast accuracy although the approach lacks appliance-specific granularity. |

| Santos (2021)            | Philippine temperature electricity prices residential aggregate load   | Weather-driven residential forecasting                                                  | SARIMAX with temperature and price regressors                                                               | Weather integration enhances national-level demand forecasting but does not provide appliance-level detail.                                       |
|--------------------------|------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| Liu et al. (2023)        | Industrial and commercial load with temperature and humidity           | Effects of extreme weather on energy demand                                             | Statistical modeling of weather-load relationships                                                          | Showed that weather strongly influences energy usage but did not include residential or appliance-level patterns.                                 |
| Eirinaki et al. (2022)   | Smart meter interval data and appliance usage logs                     | Timestamp alignment and time-resolution validation as well as energy usage optimization | Schema and interval conformance and recommender system analysis                                             | Demonstrated that strict timestamp validation improves forecast reliability but the work did not integrate appliance-level data or budget alerts. |
| Dhaou (2023)             | RMS voltage current power factor and energy readings                   | Verification of physical consistency                                                    | Recalculation of power using V multiplied by I multiplied by power factor and comparison with device values | Ensured measurement reliability by correcting inconsistent electrical readings but did not include integration with external data sources.        |
| Mystakidis et al. (2024) | Smart meter load with temperature humidity wind                        | Weather-integrated preprocessing and normalization                                      | Standardization aggregation and environmental variable alignment                                            | Found that structured preprocessing and weather integration improve forecasting accuracy especially when                                          |

|                                |                                                   |                                                     |                                                                        | combining multiple data sources.                                                                                        |
|--------------------------------|---------------------------------------------------|-----------------------------------------------------|------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Neumann et al. (2023)          | Weather variables and energy load                 | Weather data synchronization for forecasting        | Cleaning timestamp alignment and preparation of environmental features | Demonstrated that proper synchronization of weather and load data significantly improves forecasting stability.         |
| Ünal et al. (2021)             | Interval-based smart meter load                   | Interval validation and outlier removal             | Time-interval conformance and outlier filtering                        | Improved forecasting by enforcing proper interval spacing and removing anomalous readings.                              |
| Arvanitidis & Bargiotas (2022) | Missing interval and cumulative meter readings    | Handling incomplete data and cumulative consistency | Interpolation normalization and cumulative checks                      | Showed that proper treatment of missing data stabilizes forecasting and improves compatibility with time-series models. |
| Weber et al. (2021)            | Smart meter data with missing blocks              | Reconstruction of missing intervals                 | Copy-Paste Imputation using similar historical segments                | Preserved total energy consumption while filling gaps which is ideal for energy time-series continuity.                 |
| Schaffer et al. (2022)         | Cumulative smart meter readings and hourly totals | Accurate cumulative-to-interval transformation      | Conversion of cumulative readings into interval and hourly data        | Produced consistent hourly series needed for forecasting by ensuring cumulative-to-interval accuracy.                   |

| Rubattua et al. (2023)   | Load time series weather-driven variables lagged and rolling features                                        | Temporal feature engineering for forecasting                                                                             | Creation of lag values rolling means and time-based indicators                                                                                                                                       | Demonstrated that engineered temporal features significantly enhance forecasting performance.                                                                                                                                                                                    |
|--------------------------|--------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Ibrahim et al. (2022)    | Smart grid load with seasonal and daily patterns                                                             | Short-term load forecasting using time-based features                                                                    | Extraction of seasonal cycles daily patterns and lag structures                                                                                                                                      | Found that time-driven features improve next-interval forecasting accuracy.                                                                                                                                                                                                      |
| Tang et al. (2025)       | Manufacturing energy consumption time-series with 15-minute intervals, outlier-filtered and normalized.      | Improving synthetic energy generation and forecasting accuracy using an enhanced TimeGAN with multi-head self-attention. | Improved TimeGAN with attention, preprocessing through outlier removal and normalization, statistical comparison of synthetic vs real data, PCA and t-SNE evaluation, and CNN-GRU forecasting tests. | Generated data closely matched real statistics with less than 0.5 percent mean and quartile deviation. Forecasting performance improved with lower RMSE and MAE and higher R². Synthetic curves were smooth and stable due to attention-enhanced long-range dependency modeling. |
| Kaselimi et al. (2022)   | Aggregated household load, high and low frequency NILM datasets, appliance signatures and contextual inputs. | Trustworthy and robust NILM including accuracy, generalization, fairness, privacy and scalability.                       | Survey of NILM approaches including CNN, RNN, LSTM, seq2seq, hybrid convolutional-recurrent models, GAN-based NILM, transformer models and                                                           | Identified major challenges including noisy data, imbalance, poor generalization across households and limited explainability. Highlighted GANs and transformer-based                                                                                                            |

|                      |                                                                                                          |                                                                                                                         | semi-supervised techniques.                                                                                                                       | models as promising but noted the need for interpretable and reliable NILM.                                                                                                                    |
|----------------------|----------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Zhang et al. (2025)  | Building electricity load with imbalanced workday and holiday samples.                                   | Improving prediction accuracy under highly imbalanced temporal patterns using local and global augmentation strategies. | TimeGAN-based local augmentation combined with K-means clustering, sliding window segmentation, GA optimization and a CNN-LSTM forecasting model. | Local augmentation improved holiday load prediction accuracy, increased R² and reduced NRMSE and NMAE by balancing sample distributions.                                                       |
| Chen et al. (2024)   | Speech time-series such as MFCCs, pitch and timbre features under limited sample conditions.             | Improving small-sample time-series augmentation through a Dual-Layer Transfer GAN.                                      | Coarse and fine transfer networks with a module transfer strategy to enhance feature reuse and reduce irrelevant noise.                           | DLT-GAN improved realism, convergence and feature consistency for small datasets and produced high-quality speech and timbre sequences.                                                        |
| Asre & Anwar. (2022) | Electricity consumption data from multiple Australian states at 30-minute intervals after normalization. | Developing Time-Variant GAN to preserve temporal behavior in multivariate energy data.                                  | Generator, discriminator, embedding and recovery networks with min-max normalization, PCA, t-SNE and TSTR evaluation.                             | Synthetic data matched real patterns in mean, standard deviation, interquartile range and temporal structure. Time-Variant GAN outperformed other variants and maintained predictive accuracy. |

| Yilmaz & Korn. (2022)   | Fifteen-minute residential electricity demand for three years with robust scaling and daily subsets.   | Comparing multiple GAN models for synthetic residential demand generation.               | Training RCGAN, TimeGAN, CWGAN and RCWGAN with distributional comparison of mean, skewness and kurtosis, autocorrelation checks, visual trajectory evaluation and generator-discriminator loss tracking.   | All GANs produced realistic load profiles. CWGAN best matched kurtosis, RCGAN was most stable and TimeGAN struggled with low-load periods. Training behaved smoothly across models.              |
|-------------------------|--------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Shadkam (2020)          | Building-level hourly energy load with temperature and humidity                                        | Stationarity testing seasonal structure SARIMAX order selection and residual diagnostics | Augmented Dickey-Fuller test SARIMAX modeling AIC-based model selection Ljung-Box Q-test ACF and PACF checks                                                                                               | Showed that enforcing stationarity and seasonal differencing significantly improves SARIMAX accuracy and confirmed that residual diagnostics are essential for capturing all temporal structure. |
| Muñoz et al. (2023)     | Intermittent appliance-level load signals                                                              | Stabilization prior to forecasting                                                       | Decomposition and differencing of burst-type appliance patterns                                                                                                                                            | Demonstrated that decomposition and differencing reduce noise and improve forecasting accuracy especially for highly variable appliances.                                                        |
| Ma et al. (2023)        | Residential load affected by behavioral routines and changing usage patterns                           | Adaptive modeling and interpretability                                                   | Analysis of daily and weekly usage drift and creation of diagnostic visualizations                                                                                                                         | Found that residential forecasting requires adaptive models that adjust to shifting behavior                                                                                                     |

|                        |                                                                                |                                                                         |                                                                                                  | and emphasized the need for interpretable diagnostics to reveal the sources of forecasting error.                                                                             |
|------------------------|--------------------------------------------------------------------------------|-------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Chen (2025)            | Hourly appliance-level consumption with engineered lagged and rolling features | Stationarity and seasonality at appliance level feature-enhanced SARIMA | SARIMA versus machine learning comparisons feature engineering differencing and model validation | Concluded that static SARIMA struggles with dynamic appliance loads and that ML models outperform unless SARIMA includes rich time-derived features and strong preprocessing. |
| Kienhuis (2023)        | Smart meter interval load data for residential baselines                       | Forecast evaluation strategies                                          | Traditional train-test splits and accuracy metrics including MAE and RMSE                        | Showed that conventional evaluation methods do not reflect real operational forecasting motivating the use of rolling-origin evaluation.                                      |
| Torculas et al. (2023) | Smart meter energy consumption with ML predictions                             | Forecasting without cost estimation or user interface                   | Machine learning forecasting models                                                              | Produced energy consumption predictions but lacked cost breakdown appliance-level cost insights dashboards or validation tools which limited interpretability.                |

| Caw-it et al. (2025)       | Monthly household electricity expenses and aggregate usage   | Statistical cost forecasting                       | ARIMA-based monthly electricity bill prediction           | Generated monthly cost forecasts but lacked appliance-level detail and a proper validation framework.                                                     |
|----------------------------|--------------------------------------------------------------|----------------------------------------------------|-----------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------|
| Magtibay et al. (2021)     | IoT telemetry of building-level load                         | Monitoring-only architecture                       | IoT monitoring system without dashboards or cost tools    | Provided building energy monitoring but lacked cost estimation appliance-level granularity and interactive visualization features.                        |
| Singh et al. (2021)        | IoT-measured household energy usage                          | Monitoring and visualization without cost modeling | IoT system with usage visualization and appliance control | Visualized consumption but did not provide cost allocation or appliance-specific cost analysis and had no formal validation of the forecasting component. |
| Shaban et al. (2025)       | Appliance energy use with tariff variations                  | Appliance scheduling under tariff fluctuations     | Optimization algorithms for shifting appliance operation  | Showed cost savings from schedule optimization but provided no real-time alerts or budget monitoring features.                                            |
| Assadian & Assadian (2023) | Appliance-level energy consumption                           | Predictive modeling of appliance usage             | Machine learning forecasting for appliance loads          | Delivered appliance-level predictions but did not include budget alerts or mechanisms for                                                                 |

Table 2.1 Summary of Studies

|                    |                                                              |                                       |                                      | detecting excessive consumption.                                                                   |
|--------------------|--------------------------------------------------------------|---------------------------------------|--------------------------------------|----------------------------------------------------------------------------------------------------|
| Zhao et al. (2025) | Residential energy profiles with electricity price forecasts | Scheduling and cost-aware forecasting | Forecasting and scheduling framework | Enabled price-aware scheduling but lacked real-time cost alerts and appliance-level notifications. |

## 2.1 Integrating IoT for Appliance-Level Energy Monitoring and Forecasting

This  review  synthesizes  the  work  of  various  studies  that  provide  a  basis  for  integrating Internet  of  Things  (IoT)  devices,  cloud-based  platforms,  and  external  data  sources  in  building datasets  for  energy  forecasting.  A  successful  system  must  strike  a  balance  between  sensor accuracy, data integrity, and contextual enrichment, as all these factors are critical for high-accuracy energy forecasting. Our study builds upon these approaches by integrating a more comprehensive  data  collection  framework  tailored  to  the  specific  needs  of  residential  energy forecasting and cost estimation in the Philippine context.

## 2.1.1 Smart Plug Technology and Measurement Accuracy

The  use  of  smart  plug  technology  is  at  the  core  of  appliance-level  energy  monitoring, enabling the collection of real-time power data for energy forecasting. The studies by Condon et al. (2023)  and Ahmed et al. (2022) demonstrate the practical deployment of commodity smart plugs, specifically  the  Sonoff  POW  R2,  for  continuous  monitoring  in  residential  and  campus  settings, respectively.  These  studies  highlight the viability of using affordable, widely available smart plugs as sensors for real-time data acquisition.

In  Condon  et  al.  (2023),  the  researchers  implemented  a  cloud-based  Home  Energy Management  System  (HEMS)  using  Sonoff  POW  R2  smart  plugs  connected  to  the  AWS  IoT platform,  sampling  data  at  10-second  intervals.  This  approach  successfully  demonstrates  the integration of  cloud  ingestion  and  analytics,  emphasizing  how  commodity  smart  plugs  can contribute  to  scalable  energy  management  systems.  Similarly,  Ahmed  et  al.  (2022)  explored  a campus-scale  system  using  the  same  Sonoff  plugs,  further  validating  their  feasibility  for  data collection.  Both  studies  confirm  that  smart  plugs  are  a  cost-effective  and  practical  solution  for appliance-level monitoring.

However, a critical gap emerges in these studies regarding measurement accuracy. Santos et al. (2023) identified that smart plugs, including the Sonoff POW R2, can introduce measurement errors  of  up  to  ±3%,  particularly  under  dynamic  loads.  This  error  can  result  in  incorrect  energy consumption  readings,  which  may  lead  to  misleading  conclusions  in  forecasting  models  if  not

properly  addressed.  Moreover,  these  studies  do not specifically address how such measurement inaccuracies are mitigated, making it an important consideration for future work.

In  response,  our study addresses these accuracy issues by selecting certified SMATRUL Tuya  Smart  Sockets.  These  plugs  are  specifically  chosen  for  their  known  performance  under varying  loads,  and  we  further  mitigate  inaccuracies  by  implementing  a Physics Consistency and Scaling  Verification  process.  By  recomputing  power  consumption  from  raw  voltage  and  current readings  and  validating  the  results  against  expected  standards,  we  ensure  data  integrity  and correct for potential device-specific errors before the data is used in forecasting models.

## 2.1.2 Cloud-Based Architectures and Data Pipelines

A robust cloud infrastructure plays a critical role in managing the high volume of real-time data  generated  by IoT devices. Several studies, including Condon et al. (2023) and Ahmed et al. (2022),  highlight  the  importance  of  cloud  integration  in  facilitating  data  ingestion  and  storage, crucial  for  large-scale  energy  management  systems.  Both studies utilize cloud platforms for data storage  and  real-time  data  flow,  yet  they  overlook  some  important  issues  related  to  service interruptions, data storage format, and scalability.

In  Condon  et  al.  (2023),  a  real-home  Home  Energy  Management  System  (HEMS)  is implemented  using  Sonoff  POW  R2  smart  plugs  with  AWS  IoT,  capturing  data  at  a  10-second interval for appliance-level energy  consumption.  Similarly, Ahmed  et  al. (2022) explore  a campus-scale  system  with  the  same  type  of  smart  plugs,  validating  the  feasibility  of  using commodity  devices  for  continuous  data  collection.  These  studies  prove  that  smart  plug-based systems are viable for cloud data ingestion and analysis, but both systems lack a clearly defined and lightweight storage mechanism for organizing data.

To  address  this  gap,  our  study adopts a Python-based logger that operates continuously on a Microsoft  Azure  Virtual  Machine  (VM).  This system retrieves data from the Tuya Cloud API and stores it in CSV files, ensuring that the data is easily accessible for time-series modeling and further analysis. Additionally, our system  includes  a  fallback  estimation  mechanism,  which

interpolates missing data points during brief network  or API  interruptions, thus ensuring uninterrupted data flow despite potential service disruptions.

## 2.1.3 Optimal Sampling Frequency for Energy Data

The  frequency  at  which  energy  consumption  data  is  sampled  is  pivotal  in  capturing accurate  appliance-level  energy  usage  patterns,  which  are  essential  for  both  forecasting  and detecting  appliance  behavior.  The  Plegma  dataset  (Athanasoulias  et  al.,  2024),  which  records appliance-level  energy  usage  at  10-second  intervals, represents the highest resolution of data in appliance  monitoring.  This  fine  granularity  enables  a  detailed  analysis  of  energy  consumption fluctuations,  making  it  highly  relevant  to  studies  focusing  on  energy  demand  forecasting  and appliance  detection.  However,  for practical applications, particularly those limited by data storage and transmission constraints, higher frequency sampling may not always be feasible.

In  contrast,  studies  like  Hernandez  et  al.  (2020)  and  Petralia  et  al.  (2023)  explore  the impact of different sampling rates on energy consumption accuracy. Hernandez et al. (2020) found that sampling intervals greater than 10 minutes can lead to significant data loss, particularly during peak  load  periods.  Their  study  suggests  that  5-minute  sampling  intervals  offer  a  good  balance between capturing household load features and minimizing the computational overhead. Meanwhile,  Petralia  et  al.  (2023)  support  the  adoption  of  10-minute  intervals  for  detecting appliances  effectively,  especially  in  non-intrusive  load  monitoring  (NILM)  applications,  where resolution  beyond  10  minutes  might  not  yield  substantial  improvements  in  accuracy  but  could increase data volume unnecessarily.

To reconcile the ideal sampling frequency with the practical constraints of IoT devices, we adopt a 10-minute sampling cadence, aligning with the capabilities of the Tuya Cloud API while still maintaining  an  appropriate  resolution  for  appliance  detection  and  time-series  forecasting.  This approach ensures that we capture the necessary energy usage patterns without overloading the system  with  excessive  data,  which  could  compromise  long-term  sustainability.  The  10-minute cadence  has  been  validated  by  Petralia  et  al.  (2023)  and  demonstrates  an  effective  balance between capturing essential energy consumption behaviors and ensuring scalability, as evidenced

by  Hernandez  et  al.  (2020),  who  also  advocate  for  such  a  cadence  in  residential  energy consumption studies.

## 2.1.4 Integrating Exogenous Variables and Local Context

Forecasting  accuracy  in  energy  consumption  modeling  can  be significantly enhanced by integrating  exogenous  variables  such  as weather data and electricity tariff rates. Studies in sales forecasting (Chen et al., 2025) and energy forecasting (Santos, 2021) highlight the effectiveness of SARIMAX  models  in  leveraging  external  factors  to  improve  forecasting  accuracy.  Ampountolas (2021)  and  Santos  (2021)  specifically  demonstrate  the  benefits  of  integrating  weather-related variables,  such  as  temperature,  and  electricity  prices,  for  improving  the  precision  of  energy demand forecasts. Additionally, Liu et al. (2023) examined the impact of weather on industrial and commercial energy consumption, offering valuable insights into  how  extreme  weather conditions can  influence  energy  demand.  This  aligns  with  our  approach  of  integrating  weather  data  into energy forecasting, particularly during extreme weather events, which can help guide the inclusion of such  data  in residential  energy  consumption  models.  Furthermore,  a  recent  study  by Aguirre-Fraire et al. (2024) offers an  extensive dataset that  integrates  household  energy consumption with weather data collected, which includes one-minute interval data for household energy consumption and weather metrics from the OpenWeatherMap API.

However,  these  studies  tend  to  focus  on  aggregate-level  forecasting,  leaving  a  gap  in understanding how appliance-specific data can enhance forecasting accuracy. For example, while Santos (2021) focuses on aggregate demand in the Philippines, it does not account for how data at the appliance level can significantly improve predictions. Moreover, many international datasets do not  consider  crucial  local  weather  factors,  such  as  rainfall,  which  has  a  pronounced  effect  on energy  consumption,  especially  in  tropical  climates  like  the  Philippines.  Furthermore,  Liu  et  al's study focuses on industrial/commercial datasets with 15-minute intervals and it lacks the residential appliance-level granularity and the tariff/cost data integration we include.

To  bridge  these  gaps,  our  study  brings  the  industrial/commercial  scale  weather  impacts down  to  the  residential  appliance  level.  It  will  also  extend  the  focus  from  aggregate-level  to appliance-level  forecasting  by  incorporating  real-time  weather  data  from  the  OpenWeatherMap

API,  which  includes  temperature,  humidity,  and  rainfall.  Additionally,  we  integrate  Meralco  Tariff Data,  which  enables  accurate  cost  estimation  based  on  local  electricity  rates.  The  inclusion  of these local tariff and weather variables not only improves the forecasting accuracy but also allows for  precise  cost  estimations  for  individual  appliances.  This  approach  addresses  shortcomings  in previous studies, which often overlook these key factors.

## 2.2.  Enhancing Appliance-Level Energy Forecasting through Data Integrity, Cleaning, and Feature Engineering

This review synthesizes  key  studies focused  on  the preprocessing,  cleaning,  and standardization  of  energy  data  collected  from  smart  plugs  and  weather  sources,  which form the foundation  for  accurate  appliance-level  energy  forecasting.  Accurate  preprocessing  ensures that raw  data  is  physically  consistent,  temporally  continuous,  and  synchronized  with  environmental conditions, which is important for downstream forecasting and cost estimation tasks. The following sections discuss how previous works have addressed various stages of data preparation and how our  study  builds  upon  them,  extending  their  methods  to  achieve  higher  levels  of  granularity, accuracy, and applicability in the Philippine context.

## 2.2.1 Data Integrity Verification and Standardization for Appliance-Level Forecasting

Ensuring the accuracy, consistency, and synchronization of energy data from smart plugs and  weather  sensors  is  important  for  high-accuracy  appliance-level  energy  forecasting.  Several studies  emphasize  the  importance  of  data  integrity in energy forecasting, highlighting techniques for  validating  unit  consistency,  timestamps,  and  physical  parameters.  Chen  et  al.  (2025)  and Eirinaki  et  al.  (2022)  demonstrate  that  structured data preprocessing improves the robustness of forecasting  models  like  SARIMAX  and  LSTM,  which  is  particularly  essential  for  appliance-level data that can involve complex and heterogeneous data sources. Dhaou (2023) discusses the need for physical consistency in smart plug measurements, focusing on RMS values, power factor, and voltage/current  scaling,  which  is  crucial  for  eliminating  measurement  errors  in  the  forecasting pipeline. Similarly, Mystakidis et al. (2024) discuss the role of statistical normalization and interval aggregation  in  energy  forecasting  accuracy.  Neumann  et  al.  (2023)  delve  into  weather  data preprocessing,  which  also  plays  a  significant  role  in  improving  forecasting  performance  when combined with appliance-specific data.

However,  these  studies  often  focus  on  aggregate-level  or  broader  system-level  data, leaving  gaps  in  appliance-level  forecasting,  where  multiple  devices  and  external factors such as weather  data  must  be  harmonized  with  appliance-specific  energy  consumption  readings.  For instance,  while  Chen  et  al.  (2025)  focus  on  electricity sales forecasting, their approach does not consider  appliance-level  granularity  or  the  integration  of  weather  data  with  smart  plug  readings. Dhaou  (2023)  addresses  physical  consistency  but  does  not  extend  this  approach  to  include integration  with  external  data  sources  like  weather or the finer granularity required for residential appliance-level forecasting. Additionally, Eirinaki et al. (2022) focus on time-resolution conformance but  do  not  implement  the  rigorous  validation  and  schema  checks  necessary  for  appliance-level granularity.

To address these gaps, our study applies unit standardization, gap handling, and tolerance rules at a 10-minute interval for appliance-level data, extending the methods proposed by Chen et al.  (2025)  and  Eirinaki  et  al.  (2022)  to  the  appliance-specific  level.  We enhance Dhaou's (2023) physical  consistency  approach  by  incorporating  power  factor  recalculations  and  applying a ±5% tolerance rule, ensuring that each  appliance's data is physically consistent  before  model integration. Furthermore, we integrate external data sources  like weather  data  from  the OpenWeatherMap  API,  ensuring  synchronization  of  both  energy  and  environmental  data.  Our approach  improves  data  integrity  through  cross-source  validation,  physical  consistency  checks, and  rigorous  schema  enforcement,  addressing  the  limitations  observed  in  previous  studies, especially with respect to appliance-specific data.

## 2.2.2 Advanced Data Cleaning and Energy Derivation Techniques

Data cleaning and energy derivation are critical in transforming raw energy consumption data into reliable datasets suitable for forecasting models. Several studies have explored different methods for handling missing data, outliers,  and  cumulative data, each contributing to improving forecasting accuracy. Ünal et al. (2021) formalized methods for time-interval validation and outlier removal, demonstrating how these techniques improve load forecasting accuracy when applied to smart meter data. Their approach emphasizes the importance of interval validation and handling outliers, which is a foundational step in preparing data for forecasting models. Similarly, Arvanitidis

&amp;  Bargiotas  (2022)  introduced  normalization  and  interpolation  techniques,  showing  that  these methods improve the accuracy of forecasting models by ensuring the data is in a consistent format for machine learning algorithms.

Weber  et  al.  (2021)  proposed  the  Copy-Paste  Imputation  (CPI)  method,  specifically designed  for  energy  time  series  data.  This  method  addresses  the  problem  of  missing  data  by copying and pasting similar data blocks, preserving the total energy of the missing segments. Their method is highly effective for maintaining the continuity and accuracy of the data by ensuring that the  total  energy  consumed during the missing periods remains unchanged. Schaffer et al. (2022) introduced  a  method  for  converting  cumulative  energy  data  into  interval-based  energy  values, a necessary  step  for  many  forecasting  models.  This  conversion  process  ensures  that  cumulative data, often recorded by smart meters, is appropriately transformed into interval  energy consumption values, facilitating more accurate forecasting.

However, despite  these  advancements,  a  gap  remains  in  addressing  the  specific challenges  posed  by  missing  data  over  extended  periods  and  handling  cumulative  resets  or outages that often distort the energy consumption readings.

Our study addresses these gaps by adopting a hybrid decision rule for validating interval energy, which combines direct energy measurements and fallback energy estimates. We introduce a tolerance-based comparison (±10%) for validating missing data, which ensures that any missing data  does  not  lead  to  significant  inaccuracies  in  energy  predictions.  Furthermore,  we  apply  a reprocessing mechanism for cumulative resets, which effectively handles energy data that may be interrupted  or  reset  during  data  collection.  By  incorporating  physical  verification  such  as  power factor  recalculations  and scaling validation for each appliance, we ensure that the data maintains its physical integrity, addressing the shortcomings observed in Weber et al. (2021) and Schaffer et al.  (2022).  This  method  not  only  corrects for errors in energy data but also helps to fill gaps in a way  that  preserves  both  energy  consistency  and  forecasting  accuracy,  which  is  critical  when dealing with residential appliance-level data.

## 2.2.3 Hourly Aggregation and Feature Engineering for Enhanced Forecasting

Effective aggregation of energy data from high-resolution intervals, 10-minute intervals, to hourly  totals,  along  with  the  creation  of  additional  temporal  features,  plays  a  critical  role  in enhancing  forecasting  models.  Schaffer  et  al.  (2022)  demonstrated  how  cumulative-to-interval energy  derivation  is  crucial  for  transforming  energy  data  into  usable  time-series  for  forecasting. Their  study,  which  focused  on  hourly  data  from  smart  heat  meters,  laid  the  groundwork  for understanding  the  need  for  accurate  aggregation  in  energy  demand  forecasting.  Additionally, Rubattua et al.  (2023)  explored  feature  engineering  techniques,  particularly  for  load forecasting, emphasizing  the  importance  of  lagged  variables  and  rolling  features  to  capture  time-dependent patterns  in  energy  consumption.  Their  research  showed  how  such  features  could  be  used  to improve model performance, especially for energy consumption predictions. Ibrahim et al. (2022) examined the impact of lagged features on short-term load forecasting in smart grids, highlighting the role of time-based features in capturing seasonal and daily demand variations.

These  studies  significantly  contribute  to  the  broader  understanding  of  how  temporal features  such as lagged values and rolling averages can improve forecasting accuracy. However, these  approaches  largely  focus  on  aggregated  data  and  do  not  fully  account  for  the  granular, appliance-level  details,  which  are  essential  for  residential  energy  forecasting.  For  example, Schaffer  et  al.  (2022)  work  with  hourly  energy  consumption  data  but  do not specifically address how to reconcile these values with cumulative data over different timescales. Similarly, Rubattua et al.  (2023)  emphasize  the  role  of  lagged  variables  but  lack a more refined approach for handling appliance-specific  consumption  patterns,  which  could  be  crucial  in  enhancing  accuracy  at  the appliance level.

Our  study  extends  these  aggregation  techniques  by  ensuring  that  hourly  totals  are reconciled  with  cumulative  energy  values  using a 5% deviation threshold. Additionally, we create and validate temporal features such as hour-of-day, day-of-week, and holiday indicators to capture cyclical  patterns  in  appliance  energy  use.  These features enable our model to better account for daily  and  seasonal  variations  in  energy  consumption,  addressing  gaps  in  the  aforementioned studies.  By  focusing  on  appliance-level  data,  we  enhance  the  ability of the model to understand

micro-level  consumption  trends,  thus  improving  the  forecasting  accuracy  and  enabling  more precise predictions for residential energy use.

## 2.2.4 Final Dataset Assembly and Weather Data Integration

Forecasting  accuracy  in  energy  consumption  modeling  can  be  significantly  improved  by effectively  integrating  exogenous  variables  such  as  weather  data  into  the  energy  forecasting process.  Studies  in  energy  forecasting  (Mystakidis  et  al.,  2024)  highlight  the  importance  of preprocessing and evaluation metrics to enhance the accuracy of forecasting models, particularly when  integrating  multiple  data  sources.  Mystakidis  et  al.  (2024)  emphasize  how  integrating weather data, such as temperature, humidity, and wind speed, with energy consumption data helps improve  the  reliability  of  forecasts,  particularly  in  systems  where  energy  demand  is  strongly influenced by environmental  conditions. Neumann  et  al.  (2023)  similarly  discuss  how  the synchronization of weather data with energy time series improves the overall forecasting accuracy by addressing the challenges of temporal consistency and data integration.

In  addition,  Rubattua  et  al.  (2023)  provide  insights  into  the  importance  of  creating additional  features  that  account  for  both  temporal  and  environmental  factors  in load forecasting. They highlight  the  value  of  integrating  weather-related  variables,  such  as  temperature, humidity, and rainfall, to capture the influence of environmental changes on energy demand. This aligns with our approach of integrating these weather variables into energy forecasting models, particularly for appliance-level forecasting, which is more sensitive to localized weather patterns.

However,  these  studies  often  focus  on  broader  energy  systems  or  aggregated  data, leaving  a  gap  in  the  application  of  weather  data  integration  at the appliance level. For example, while  Mystakidis  et  al.  (2024)  and  Neumann  et  al.  (2023)  explore  weather  integration  in  energy forecasting,  their  focus  is  primarily  on  aggregate  demand,  and  they  do  not  address  the  specific challenges  of  integrating  high-resolution  appliance-level  data  with  real-time  weather  information. Additionally,  Rubattua et al. (2023) discuss the use of environmental variables in load forecasting but  do  not  emphasize  the  importance  of  synchronizing  weather  data  with  individual  appliance energy readings at high temporal resolutions, such as 10-minute intervals.

To bridge these gaps, our study integrates real-time weather data from the OpenWeatherMap API, incorporating temperature, humidity, and rainfall as exogenous variables alongside appliance energy data. We  ensure synchronization between the weather and appliance-level  energy  consumption  readings,  using  rigorous  temporal  consistency  checks  and physical plausibility validations to ensure high-quality data for forecasting. Furthermore, we apply a 5% deviation threshold for the reconciliation of hourly energy totals with cumulative energy values, ensuring  the  integrity  of  our  dataset.  This  approach  enhances  the  robustness  of appliance-level forecasting models, addressing  the limitations of previous studies that typically focus  on larger-scale  or  aggregate  data without the fine-grained synchronization and validation needed for residential energy forecasting.

## 2.3 Synthetic Data Generation Using GANs and Time-Series Generators

This  section  reviews key works on GAN-based synthetic time-series generation and their extensions to energy consumption data. The first subsection discusses general-purpose time-series  GAN  architectures,  including  TimeGAN  and  its  improvements  and  transfer-based variants  designed  for  small-sample  settings.  Meanwhile,  the second subsection focuses on GAN applications  in  energy  data  reconstruction,  highlighting  their  strengths,  limitations,  and  the  gaps that motivate this study's TimeGAN-based, Meralco-constrained household reconstruction pipeline.

## 2.3.1 Synthetic Data Generation Using GANs

A more recent contribution  to GAN-based time-series generation is the work of Zhang et al. (2025), who applied a TimeGAN-driven augmentation framework to building electricity load data characterized  by  strong  workday-holiday  imbalances.  Their  approach  integrates  TimeGAN  with K-means clustering, sliding-window segmentation, and a CNN-LSTM forecasting model optimized using a genetic algorithm. The study demonstrated that locally targeted augmentation substantially improves  holiday  prediction  accuracy,  increases  R²,  and  reduces  NRMSE  and  NMAE.  Although their  work  focuses  on  building-level  loads,  it  highlights  how  TimeGAN  can  effectively  address sample imbalance, preserve temporal behavior, and enhance downstream predictive performance-principles that are relevant to reconstructing missing residential energy data.

Building  on  similar  foundations,  Tang  et  al.  (2025)  proposed  an  Improved  TimeGAN  for augmenting industrial energy  consumption  time-series.  Their model  enhances  the  original TimeGAN  by  incorporating  a  multi-head  self-attention  mechanism  within  the  recovery  module, enabling better long-range dependency modeling, particularly valuable under  limited data availability.  After  preprocessing  through  outlier  removal  and  min-max  normalization,  the  authors evaluated  synthetic  data  quality  using  statistical  similarity  metrics  (mean,  standard  deviation, quartiles,  skewness,  kurtosis)  and  dimensionality  reduction  tools  such  as  PCA  and  t-SNE.  The Improved TimeGAN achieved average differences below 0.5% for means and quartiles, variance errors below 10%, and improved RMSE, MAE, and R² in subsequent forecasting tasks. However, the  method  remains  limited  to  single-source  industrial  equipment  data  and  does  not incorporate household-specific constraints such as monthly billing totals or multi-appliance behavior.

In  a  different domain, Chen et al. (2024) introduced DLT-GAN, a dual-layer transfer GAN designed  for  small-sample  speech  time-series.  The  architecture  consists  of  a  Coarse  Transfer Network and a Fine Transfer Network, enabling the reuse of learned representations and reducing irrelevant noise when transferring features across related tasks. DLT-GAN demonstrated improved convergence, enhanced realism, and better timbre consistency in small-sample speech datasets. Although  not  energy-focused,  this  work  directly  addresses  challenges  associated  with  limited sample  availability,  a  situation  similar  to  having  only  two  months  of  real  smart-plug  data  in  the present study. Still, DLT-GAN does not incorporate concepts unique to the energy domain, such as kWh scaling, tariff alignment, or appliance-level decomposition.

Taken together, these GAN-based time-series generators show that temporal structure can be  preserved  through  architectures  such  as  TimeGAN,  which  couple  embedding  networks, supervised  step-ahead  prediction,  and  adversarial  learning.  Studies  such  as  Tang  et  al.  (2025) demonstrate that architectural enhancements like multi-head self-attention improve reconstruction quality  and  long-range  dependency  modeling,  while  works  like  Chen  et  al.  (2024)  highlight  how transfer-based  GAN  designs  can  strengthen  robustness  under  small-sample  conditions.  These findings  establish  a  solid foundation for applying advanced GAN frameworks to realistic synthetic time-series generation.

However,  none  of  these  works  directly  address  the  challenges  of  residential  energy reconstruction  under  the  constraints  of  incomplete  yearly  smart-plug  data,  known  monthly  kWh totals  from  utility  bills,  and  the  need  for  per-appliance  synthetic  profiles  aligned  with  household billing. To address these gaps, the present study adapts an Improved-TimeGAN-style architecture to  the  household  electricity  domain.  The model is trained on two months of daily household load curves  and  then  used  to  generate  synthetic  daily  sequences  for  the  missing  months. Unlike the original  TimeGAN  and  DLT-GAN  implementations,  the  synthetic  sequences  in  this  study  are subsequently  scaled  to  match  Meralco  monthly  energy  consumption  and  decomposed  into appliance-level  profiles using real appliance shares. This ensures that the generated data remain physically consistent,  seasonally  aligned,  and  economically  accurate  with  respect  to  actual household billing.

## 2.3.2 GANs in Energy Data Reconstruction and Their Limitations

Asre and Anwar (2022) proposed a Time-Variant GAN for synthetic energy data generation using electricity consumption data from AEMO across five Australian states (VIC, NSW, QLD, SA, TAS) at 30-minute intervals.  Their  architecture includes generator, discriminator, embedding, and recovery  components, and uses min-max normalization followed by PCA and t-SNE to compare real and synthetic distributions. They evaluate performance using 'train on synthetic, test on real' (TSTR)  strategies  and  show  that  the  synthetic  state-level  load  retains  similar  statistics  (mean, standard deviation, interquartile range) and temporal behavior, while also supporting privacy-preserving modeling. However, their focus is on aggregated state-level energy rather than household or appliance-level data. The model does not incorporate monthly billing information, nor does it decompose total load into appliance segments. Training is also relatively complex and not designed to handle very short monitoring windows, which is a key constraint in the present study.

Yilmaz  and  Korn  (2022)  investigated  multiple  GAN  architectures,  RCGAN,  TimeGAN, CWGAN,  and  RCWGAN,  for  synthetic  electricity  demand  generation  at  the  individual  customer level using 15-minute interval residential data. They apply robust scaling and analyze distributions of  mean,  skewness,  kurtosis,  as  well  as  autocorrelation  patterns,  to assess how well each GAN reproduces  real  consumption  behavior.  Their  findings  indicate  that  all  four  GANs  can  generate realistic load profiles, with CWGAN achieving the closest match in kurtosis and RCGAN producing

the  most  stable  synthetic  sequences.  TimeGAN  performs  comparatively  worse  in  modeling low-load  periods.  The  primary  contribution  is  a  comparative  evaluation  of  GAN  variants  for one-dimensional  household  demand,  without  extending  to  monthly  reconstruction,  appliance breakdown, or integration with utility billing data.

Tang  et  al.  (2025)  (as  discussed  earlier)  apply  their  enhanced  TimeGAN  model  to manufacturing energy consumption with 15-minute sampling. They use the synthetic sequences to augment limited real data and then train a CNN-GRU forecasting model, showing improvements in RMSE,  MAE,  and  R²  when  synthetic  data  are  included.  Statistical  metrics  (mean,  variance, quartiles,  skewness,  kurtosis)  and  visualization  methods  (PCA,  t-SNE)  confirm  that  synthetic sequences closely match real process-level loads. While this work provides a strong precedent for using  Improved TimeGAN in energy applications, it operates in a single-source industrial context, assumes  continuous  process  operation,  and  does  not  incorporate  constraints  such  as  monthly billing totals or appliance heterogeneity, which are central to residential use cases.

Kaselimi  et  al.  (2022)  offer  an  extensive  review  of  non-intrusive  load  monitoring  (NILM) techniques, which aim to disaggregate aggregate household load into appliance-level signals using advanced deep learning models, including CNNs,  RNNs,  LSTMs,  sequence-to-sequence architectures,  and  GAN-based  NILM  formulations.  Their  survey  emphasizes  challenges  such  as noisy  measurements,  imbalanced  datasets,  generalization  across  households,  privacy,  and  the need  for  explainable  and  trustworthy  models.  While  GANs  are  highlighted  as  a  promising component  of  NILM  pipelines,  these  approaches  depend  heavily  on  high-frequency  or  richly labeled  data  and  focus  on  disaggregation rather than reconstructing missing months of historical consumption. NILM techniques also tend not to enforce consistency with monthly billing data, and they are not designed to synthesize entirely missing seasons from short observation windows.

Across these studies, several common limitations emerge when evaluated in the context of the  current  research  problem.  Many  GAN-based  energy  works  operate  at  the  aggregated  level, such  as  state-level  grids  or  industrial  process  data,  rather  than  focusing  on  household-  or appliance-level  signals,  limiting  their  applicability  to  fine-grained  residential  forecasting.  Existing methods also rarely incorporate external energy constraints such as monthly kWh totals from utility

bills,  meaning  that  synthetic  outputs  may  resemble  real  load  shapes  statistically  but  are  not constrained to match actual billed consumption. Most prior approaches generate only a single total load  profile  and  do  not  perform  appliance-level  reconstruction  aligned with measured smart-plug data  or  appliance  energy  shares.  Furthermore,  although  several  works  address  limited-data settings,  they  do  not  directly  tackle  the  specific  challenge  of  having  only  two  months  of  real household measurements while requiring a complete 12-month dataset for seasonal forecasting. Finally, the majority of GAN applications are designed for data augmentation rather than historical reconstruction,  and  therefore  do  not  enforce  consistency  with  both  real smart-plug readings and utility billing records when generating missing months of consumption data.

The  present  study  addresses  these  gaps  by  adapting  an  Improved  TimeGAN-style architecture to a residential household context and embedding it into a constrained reconstruction pipeline.  First,  two  months  of  10-minute  appliance-level  smart  plug  data  are  preprocessed  and segmented into daily sequences for TimeGAN training. Second, the trained generator is used to produce synthetic daily load profiles for all missing days in the year. Third, for each month without full smart-plug coverage, the synthetic daily profiles are scaled so that their aggregate kWh exactly matches  the  corresponding  Meralco  bill,  enforcing  an  energy  constraint  that  prior  works  do  not implement. Finally,  using  appliance  energy  shares  derived  from the two months of real data, the scaled household load is decomposed into appliance-level synthetic profiles, providing a 12-month high-resolution dataset suitable for SARIMAX forecasting and cost estimation.

By combining GAN-based time-series generation with utility-bill scaling and appliance-level reconstruction,  this  study  extends  the  existing  literature  in a direction that is directly aligned with practical  household  energy  management.  Rather  than  relying  on  NILM  or  large-scale  industrial datasets, the proposed approach leverages a short window of real smart-plug measurements and publicly  available  billing  information  to  reconstruct  a  complete,  appliance-resolved,  10-minute dataset that would otherwise be unavailable.

## 2.4 Forecasting Model Design and Validation for Appliance-Level Energy Consumption

This  section  presents  the  full  forecasting  pipeline  for  hourly  appliance-level  electricity consumption. The approach integrates statistical pre-modeling checks, adaptive SARIMAX model

fitting with exogenous variables, and rigorous evaluation procedures. Prior studies inform individual components of this pipeline,  but  none  combine  them  at  the  hourly  appliance level with adaptive seasonal tuning, rolling-origin forecasting, and diagnostic visual analytics for interpretation.

## 2.4.1 Pre-Modeling Checks &amp; Stationarity

Accurate  appliance-level  forecasting  begins  with  preparing  each  appliance's  time  series and  validating  its  statistical  properties  before  modeling.  Several  studies  have  emphasized  the importance of testing  for  stationarity,  identifying  seasonality,  and stabilizing load patterns prior to forecasting.  For  example,  Shadkam  (2020)  used  the  Augmented  Dickey-Fuller  (ADF)  test  to assess  stationarity  and  applied  SARIMAX  with  exogenous  variables  such  as  temperature  and humidity  to  forecast  building-level  energy  demand.  This  supports  our  use  of  ADF  to  evaluate whether  an  appliance's  hourly  energy  signal  is  stationary,  and  to  apply  differencing  (including seasonal differencing) if it is not.

Muñoz  et  al.  (2023)  further  demonstrated  that  decomposition  and  differencing  improve model performance by reducing noise and enforcing stationarity in building-level load forecasting. This  motivates  our  use  of  preprocessing  (first  differencing,  seasonal  differencing,  and  optional decomposition) to stabilize highly intermittent appliance loads, such as fans and refrigerators, that exhibit on/off bursts rather than smooth consumption curves.

At the same time, prior reviews such as Ma et al. (2023) argued that short-term residential load forecasting requires models that can adapt to evolving usage routines (for example, changes in  occupant  behavior  across  weekdays  vs.  weekends),  and  that fixed seasonal assumptions are often  too  rigid.  Chen  (2025)  reinforced  this  point  at  the  appliance  level  by  showing  that  static SARIMA  configurations  often  underperform  more  adaptive  machine  learning  models  (e.g., XGBoost)  when  forecasting  hourly  appliance  consumption.  This  gap  highlights  the  need  for adaptive seasonal tuning rather than relying on a single fixed seasonal period and parameter set.

To  address  this,  our  approach  not  only  detects  repeating  daily  structure  (like  24-hour appliance  usage  cycles)  using  autocorrelation  patterns,  but  also  systematically  refines  seasonal ARIMA parameters through rigorous model identification and validation procedures. We employ a

comprehensive model selection process that evaluates multiple seasonal orders (P,D,Q)s based on information criteria (AIC/BIC) and forecast error metrics for each appliance. Unlike the static model selection  used  in  Shadkam  (2020),  Kienhuis  (2023),  and  Chen  (2025),  our  seasonal  parameter identification  is  tailored  per  appliance and validated through rolling-origin evaluation, allowing the model to capture changing usage routines over time (for example, fans used more at night during hotter weeks).

## 2.4.2 SARIMAX Model Fitting with Exogenous Features and Rolling Forecasting

Once  the  series  is  prepared  and  seasonality  is  characterized,  forecasting  is  performed using a Seasonal Autoregressive Integrated Moving Average with Exogenous Variables (SARIMAX) model. Prior work has established SARIMAX as a strong baseline for energy demand forecasting  when  external  drivers  are  included.  Shadkam  (2020)  modeled  university  building demand using SARIMAX with temperature and humidity as exogenous regressors and selected ARIMA/SARIMA  orders  with  AIC.  This  directly  informs  our  use  of  SARIMAX  to  model  hourly appliance-level  energy  consumption  and  our  use  of  weather  and  temporal  context,  such  as temperature, humidity, rainfall, hour of day, day of week, weekend/holiday flags, recent lags (lag at t-24), and rolling means, as an exogenous feature vector X t

Chen (2025) showed that, at the appliance level, forecast accuracy improves substantially when time-derived features (lags,  rolling  averages) are engineered and fed into the model rather than  relying  on  raw  consumption  alone.  We  incorporate  that  insight  by  explicitly constructing an exogenous feature vector per timestamp that blends environmental factors (weather), behavioral/calendar features, and autoregressive structure. This preserves interpretability because each regressor in  X t   has  a  coefficient  that  can  be  inspected,  unlike in opaque machine learning models.

However,  most  existing  studies  either  evaluate  models  with  a  simple  train/test  split (Kienhuis,  2023;  Chen,  2025)  or  assume  a  fixed  training  window  (Shadkam,  2020).  These evaluation  strategies  do  not  fully  reflect  how  forecasting  systems  behave  in  deployment,  where models must repeatedly forecast 'the next day' given everything observed so far. To close this gap, we  adopt  a  rolling-origin  evaluation  procedure:  at  each  step  in  the  testing  period,  the  model  is

retrained on all data available up to time t, and then asked to predict future consumption (like the next  24  hours).  This  rolling  approach  mimics  real  operational  forecasting  rather than a one-time offline benchmark.

In  addition,  while  prior  work  such  as  Ma  (2023)  stresses  the  need  for  adaptive  and interpretable forecasting in homes,  it does  not present an  implementation  that  jointly  (1) incorporates exogenous weather and behavioral context, (2) applies  systematic  seasonal parameter selection for appliance-level patterns, and (3) evaluates under rolling-origin conditions at the appliance level. Our study integrates all three, producing forecasts that are both traceable (via SARIMAX coefficients) and robust to behavioral drift.

## 2.4.3 Forecast Accuracy, Diagnostic Validation, and User-Interpretable Insight

After  fitting  the  model,  it  is  not  sufficient  to  report  a  single accuracy score. Prior studies have relied on standard metrics such as Mean Absolute Error (MAE) and Root Mean Square Error (RMSE)  to  compare  forecasting  models  (Kienhuis,  2023;  Chen,  2025).  These  metrics  remain essential, and we also compute Mean Absolute Percentage Error (MAPE) and R² to quantify how much of the appliance's consumption variance is explained by the model. This multi-metric view lets  us  compare  our  SARIMAX  approach  against  traditional  baselines  and  machine  learning alternatives.

However,  numerical  error  alone  does  not  confirm  model  reliability.  Shadkam  (2020) emphasized the importance of residual diagnostics, checking that the residuals behave like white noise,  exhibit  no  remaining  autocorrelation,  and  pass  statistical  goodness  checks  such  as  the Ljung-Box test. We adopt that practice by analyzing the autocorrelation function (ACF) and partial autocorrelation function (PACF) of residuals and applying the Ljung-Box Q-test to confirm that the model  has  captured  temporal  structure.  This  step  is  critical  for  validating  that  the  model  is statistically well-specified, not just 'good on average.'

Ma (2023) further highlights that residential forecasting must be explainable and adaptive, since  household  users  and  operators  need to understand not only 'how much will we consume,' but also 'why did we miss here?' and 'under what conditions does the model struggle?' Inspired by

that  need  for  interpretability,  we  extend  beyond  purely statistical diagnostics and generate visual diagnostics,  including  (1)  hourly  heatmaps  of  forecast  error  to  reveal  time-of-day  patterns,  (2) per-appliance residual boxplots to identify which appliances are hardest to predict, and (3) scatter plots  of  forecast  error  versus  temperature  to  expose  weather-related  bias.  These  visual  tools translate model behavior into actionable insight for users and system designers.

In contrast to prior work. which often ends at reporting MAE or RMSE on a static test split, our evaluation loop treats validation as an ongoing process. We combine quantitative error metrics, statistical residual  testing,  rolling-origin  realism,  and  appliance-level  visual  diagnostics.  This produces a forecast model that is not only accurate but also auditable, explainable, and ready to be surfaced to end users in the context of appliance-level energy budgeting and cost control.

## 2.5 System Implementation and Validation for Appliance-Level Energy Forecasting and Cost Estimation

This section covers the implementation  and  validation of  a  system  designed  for appliance-level energy forecasting and cost estimation. By integrating IoT devices, real-time data, and forecasting models, our study  develops  a  framework  that  provides  accurate  energy consumption  and  cost  predictions.  The  system  is  tailored  to  the  Philippine  context,  ensuring effective energy management and cost control for residential users.

## 2.5.1 Cost Estimation Methodology

Forecasting  accuracy  in  energy  consumption  modeling  can  be significantly enhanced by integrating  cost  estimation  methodologies  at  the  appliance  level.  Many  previous  studies  have explored  energy  consumption  forecasting  but  often  overlook  providing  a  detailed  framework  for cost  estimation.  For  instance,  Erru  Torculas  et  al.  (2023)  employ machine learning algorithms to predict energy consumption but do not include any cost estimation model or break down the costs at  the  appliance  level.  Their  focus  on  forecasting  energy  consumption  patterns  fails  to  translate these predictions into actionable cost predictions, thereby leaving a gap in managing energy costs effectively. Similarly, Jelly Grace A. Caw-it et al. (2025) apply ARIMA to forecast monthly electricity expenses but do not provide appliance-level forecasts or cost breakdowns. Their study is limited to

household-level  consumption  predictions,  which makes it less useful for understanding how each appliance contributes to overall energy costs.

In  a  similar  vein,  Oscar  Bryan  M.  Magtibay  et  al.  (2021)  focus  on  energy  consumption monitoring  using  IoT  devices.  Although  their  work  tracks  energy  use,  they  do  not  provide  any detailed  cost  estimation  methods  or  appliance-level  energy  cost  analysis.  This  is  a  significant limitation in practical applications, as understanding the financial impact of energy consumption is critical  for  consumers  and  utility  companies.  Additionally,  Mitesh  Singh  et  al.  (2021)  present  an energy monitoring system with data visualization, but they omit any discussion on cost estimation. This  is  a common gap, as it is essential for users to understand the financial implications of their energy consumption to optimize their energy use.

The  studies  reviewed  primarily  focus  on  forecasting  energy  consumption  or  monitoring energy  use  but  lack  detailed  cost  estimation  methodologies  that  are  crucial  for  understanding energy  expenses  at  the  appliance  level.  Unlike  these  studies,  our  approach  integrates  energy consumption forecasting with appliance-specific cost estimation. Moreover, our study incorporates cost  translation  models  that  account  for  time-of-use  tariffs,  which  many  previous  studies  fail  to address.  This  allows  our  study  to  provide  energy  costs  for  each  appliance  and  identify  the top-consuming appliances that contribute most to overall household energy expenses. By providing this  level of detail, our study offers actionable insights for consumers, helping them optimize their energy consumption and manage costs effectively, something that has been overlooked in prior research.

## 2.5.2  Budget Threshold and Alert Engine

Effective management of energy costs can be significantly enhanced by integrating budget thresholds  and  alert  mechanisms  for  energy  consumption  and  cost  at  the appliance level. Many studies  have  explored  energy  management  and  optimization  strategies,  but  few have integrated real-time  budget  monitoring  with  alert  systems  for  appliance-level cost forecasting. For example, Shaban  et  al.  (2025)  discuss  optimizing  appliance  scheduling  under  varying  tariff  systems  to reduce energy costs. However, their study lacks a real-time alerting mechanism that notifies users when their energy consumption approaches a predefined budget threshold. While their focus is on

scheduling strategies, it does not incorporate dynamic monitoring and alerting features necessary for  proactive  cost  management.  Similarly,  Eirinaki  et  al.  (2022)  focus on real-time energy-saving recommendations for appliance usage but do not include any system for managing energy budgets or  alerting  users  when  budget  thresholds  are  reached.  Their  study's  recommendations can help reduce energy consumption but fail to address the practical challenge of budget control, which is essential for users managing energy costs effectively.

Zhao et al. (2025) in their study on residential energy consumption and price forecasting, look at energy  scheduling  and  price forecasting but do  not integrate real-time alerts or appliance-level cost forecasting. The lack of real-time alerts in their system is a significant limitation for consumers who need to manage energy costs effectively on a daily basis, particularly as their study does not focus on providing detailed budget control mechanisms.

Assadian &amp; Assadian (2023) present a data-driven model for predicting energy consumption  at  the  appliance  level,  but  similarly,  they  omit  any  budget  management  or  alert systems.  While  their  model  offers  valuable  insights  into  energy  usage  predictions,  it  does  not address the critical issue of providing users with alerts when their energy costs are about to exceed a set budget, which would allow them to take action to reduce consumption before costs spiral.

These  studies,  while  offering  valuable  energy  consumption  forecasting  techniques  and energy-saving strategies, overlook the need for systems that combine budget threshold management with real-time alerts. The absence of dynamic alerts when users are approaching or exceeding  their  budget  limits  presents  a  significant  gap  in  real-time  energy  cost  management. Additionally,  most  studies  focus  on aggregate-level data or generic recommendations without the finer appliance-level breakdown required for effective cost control.

To  address  these  gaps,  our  study  integrates  real-time  budget  management  and  alert mechanisms, offering a system that allows users to set budget thresholds for energy consumption and cost.  When thresholds are close to being exceeded, the system triggers alerts to notify the user,  providing  them  with  the  opportunity  to  adjust  their  usage.  Furthermore,  we  incorporate detailed  cost  estimation  models  that  account  for time-of-use tariffs, which many previous studies

fail  to  address.  By  offering  these  features,  our  system  not  only  enhances  the  ability  to  manage energy  budgets  but  also  provides  actionable  insights  for  consumers  to  optimize  their  energy consumption  and  control  costs  effectively.  This  integrated  approach  addresses  shortcomings  in previous  studies,  which  generally  overlook  the  combined  functionality  of  budget  control  and real-time alerting at the appliance level.

## 2.5.3  System Artifacts and Validation

Several studies have explored energy consumption forecasting and monitoring, but many have overlooked integrating user-facing features, such as dashboards and alert systems, which are essential  for  effective energy management. For example, Erru Torculas et al. (2023) developed a machine learning-based system for energy consumption forecasting but did not include any user interface  artifacts,  such  as  dashboards,  which  are  essential  for  enabling  users  to  visualize  and interact with the data effectively. This lack of user-facing features makes it difficult for users to take full advantage of the system and manage their energy consumption effectively.

Similarly, Oscar Bryan M. Magtibay et al. (2021) proposed an IoT-based energy monitoring system for the Mabini Building in De La Salle Lipa but did not include a user-friendly dashboard or cost  estimation features. Although the system focuses on energy monitoring, the absence of cost breakdowns  and  interactive  interfaces  limits  its  usability  for  consumers  who  need  actionable insights into their energy expenses.

In another  example,  Mitesh  Singh  et  al.  (2021)  discussed  an  energy  consumption monitoring and  control system  using  data  visualization  and  IoT,  but  their  system  lacks  a user-friendly  dashboard  that  would allow users to manage energy usage effectively and see how individual  appliances  contribute  to  total  energy  costs.  While  they  provide  visualization  of energy data,  the  lack  of  context,  such  as  cost  estimation  or  budget  management  features,  limits  the system's practical value for consumers.

The studies reviewed mainly focus on energy consumption forecasting or monitoring but fail  to  provide  comprehensive  user-facing  artifacts  that  allow  for interactive engagement with the system.  Unlike  these  studies,  our  system  integrates  a  web  dashboard  that  offers  a  clear  and

accessible  visualization of energy consumption, cost breakdowns, and alerts for proactive energy management. This dashboard is designed to enhance user interaction with the system and provide actionable  insights  into  their  energy  consumption  patterns.  Furthermore,  by incorporating mobile alerts,  users  are  notified  when  they  are  nearing  budget  thresholds  or  exceeding  their  set  limits, empowering them to make real-time decisions to optimize their energy use.

In  addition  to  user-facing  features,  validating  the  accuracy  of  the  energy  consumption forecasts  and  cost  estimates  is  crucial  for  ensuring  the  system's  reliability  and  precision.  Many previous studies have developed forecasting models without providing detailed validation procedures,  leaving  uncertainties  regarding  the  accuracy  of  their  predictions.  For  instance,  Erru Torculas et al. (2023) focus on energy forecasting using machine learning algorithms, but they do not  include  a  formal  validation  process  to  assess  the  accuracy  of  their  forecasts,  which  may undermine the system's reliability.

Similarly,  Jelly  Grace  A.  Caw-it  et al. (2025) apply the ARIMA model to forecast monthly electricity expenses but do not include any validation framework to assess the performance of their model, leaving  their  forecasting  results  uncertain.  Mitesh  Singh  et  al. (2021) describe an energy monitoring  and  control  system  without  a  detailed  validation  process,  raising  concerns  about  the accuracy and reliability of their system.

In  contrast,  our  study  incorporates  a  comprehensive  validation  framework that assesses the accuracy  of  both  energy  consumption  forecasts  and  cost  estimates.  By  validating  the forecasting  models  with  real-world  data  and  using  methods  such  as  cross-validation  and  error metrics,  we  ensure  the precision of our predictions. This rigorous validation process confirms the reliability of the system, providing users with confidence in the accuracy of the forecasts and cost estimates generated. Our approach to system artifacts and validation addresses the gaps identified in  previous  studies,  ensuring  not  only  a  user-friendly  interface  but also reliable, accurate energy management and cost estimation.

## 2.6 Synthesis

Our methodology builds directly on prior studies in IoT energy monitoring, preprocessing, forecasting,  and  cost-oriented  decision  support,  but  we  extend  them  into  a  single  end-to-end system  that  works  at  the  appliance  level,  on  an  hourly  horizon,  under  Philippine  household conditions.  First,  studies  by  Condon (2023) and Ahmed (2022) demonstrated that low-cost smart plugs  like  the  Sonoff  POW  R2  can  be deployed to capture real-time appliance-level energy data and  stream  it  to  cloud  services  for  analysis,  proving  that  continuous  monitoring  is  technically feasible  at  the  device  level.  These  works,  along  with  findings  from  Santos  (2023),  Hernandez (2020),  Petralia  (2023),  and  Athanasoulias  (2024), also explored practical issues such as sensor accuracy and sampling frequency, with results suggesting that very high-frequency logging (e.g., every  10  seconds)  improves  detail  but  increases  storage  and  network  load,  while  5-10  minute sampling can still capture meaningful appliance behavior. Meanwhile, other studies in energy and demand forecasting (Santos, 2021; Ampountolas, 2021; Liu, 2023; Aguirre-Fraire, 2024) showed that  using  external  variables  like  temperature,  humidity,  and  electricity  prices  as  exogenous features  improves  prediction  quality,  although  these  works  mostly  operated  at  the  building  or household aggregate level and did not translate appliance-level usage into consumer-facing cost. Building  on  these  foundations,  our  system  adopts  readily  available  Tuya-based  smart  plugs (SMATRUL 16A sockets), but instead of assuming their readings are always correct, we enforce a Physics Consistency and Scaling Verification  step  that  recomputes  power  from  voltage,  current, and  power  factor  and  compares  it  against  the  plug's  own  reported  wattage  using  a  strict  ±5% tolerance  rule.  We  also  run  a  continuous Python-based logger on an Azure VM that polls Tuya's cloud  API  every  10  minutes,  stores  all  readings  per  appliance  in  CSV,  and  interpolates  brief outages to prevent timeline gaps. This logging cadence matches what the literature identifies as an effective  compromise  between  resolution  and  long-term  feasibility,  and  we  later  aggregate  that cleaned 10-minute data to hourly values, which aligns with our 24-hour forecast horizon. Finally, unlike  previous  work,  we  enrich  every  appliance's  series  with  aligned  contextual  variables, localized temperature, humidity, and rainfall from OpenWeatherMap,  calendar information (time-of-day, day-of-week, weekend/holiday), and the current Meralco residential tariff ( ₱ /kWh), so that  each  appliance's  consumption  can  be  related  not  only  to  behavior  and weather, but also to cost in pesos for Filipino households.

The  next  methodological  layer  addresses  preprocessing  and  data  cleaning,  which  prior studies  identified  as  critical  but  did  not  fully  specify  for  noisy  commodity  IoT data. Chen (2025), Eirinaki  (2022),  and  Mystakidis  (2024)  emphasized  that  forecasting  models  like  SARIMAX  and LSTM depend heavily on consistent timestamps, correct units, and well-structured historical logs. Dhaou (2023) warned that smart plug outputs can become physically inconsistent if scaling factors for  voltage,  current,  or  power  factor  drift.  Other  work,  such  as  Ünal  (2021)  and  Arvanitidis  &amp; Bargiotas  (2022),  focused  on  interval  validation,  outlier  removal,  and  interpolation,  while  Weber (2021)  and Schaffer (2022) tackled the challenges of missing intervals and converting cumulative energy counters into usable per-interval energy values. However, most of these studies dealt with household- or building-level meters sampled every 15 to 60 minutes, and did not fully address the messy realities of appliance-level data at 10-minute resolution: counter resets, Wi-Fi/API gaps, and partial  logging.  Our  methodology  takes  those  ideas  and  turns  them  into  a  strict,  auditable preprocessing  pipeline  for  each  appliance.  We  begin  by  enforcing  schema  and  timestamp conformance at the source: every incoming record from the smart plug is aligned to a 10-minute cadence in UTC+8, and every weather reading is aligned to an hourly cadence, which we then merge later.  We  perform Physics Consistency and Scaling Verification, where we recompute true power from voltage × current × power factor and verify that the plug-reported wattage is physically plausible  and  within  tolerance;  if  not,  we  correct  it.  We  then  derive  per-interval  energy  in  two independent ways: (1) from changes in the device's cumulative kWh register and (2) from average power over the interval  multiplied  by  elapsed  time. We compare both, accept whichever value is within  a  ±10%  decision  window,  and  fall  back  to  the  physics-derived  estimate  if  the  cumulative register is reset or glitched. Short gaps (≤20 minutes) are interpolated in terms of voltage/current/power and then re-derived; larger gaps are explicitly marked as missing instead of 'guessed'  to  avoid  hallucinating  consumption.  Sudden  negative  jumps  in  cumulative  energy indicate  counter  resets,  which  are  automatically  detected  and  corrected.  We  also  run  daily reconciliation:  after cleaning all 10-minute intervals, we sum them and compare against the day's reported  cumulative  change  to  ensure  the  total  energy  for  that  appliance  is  still  physically consistent,  reprocessing  if  the  deviation  exceeds  5%.  Only  then do we aggregate to hourly kWh and attach engineered features such as hour-of-day, weekday/weekend flags, holiday indicators, lag  values  (e.g.,  previous  day  at  the  same  hour,  previous  week  at  the same hour), 24-hour and 168-hour  rolling  means,  and  synchronized  weather  variables  at  that  hour.  This  end-to-end

procedure operationalizes  what  previous  authors recommended in parts, validation, interpolation, outlier  control,  cumulative-to-interval  conversion,  weather  alignment,  but  applies  it  specifically  at the appliance level with explicit numeric tolerance rules and auditability.

We  next  integrate  insights  from  recent  advances  in  GAN-based  synthetic  time-series generation  to  address  a  unique  constraint  that  no  prior  study  addressed:  the  requirement  to reconstruct  an  entire  year  of  appliance-level  data  from  only  two  months  of  real  measurements. Recent works show that GANs can preserve temporal structure and generate realistic synthetic loads even under imbalance or limited data. Zhang et al. (2025)  demonstrated  that  a TimeGAN-based  augmentation  pipeline  with  K-means  clustering  and  a  CNN-LSTM  predictor improves forecasting for imbalanced building loads (e.g., holidays vs. workdays), while Tang et al. (2025)  showed  that  an  Improved  TimeGAN  with  multi-head  attention  can  generate  energy sequences  with  &lt;0.5%  mean  and  quartile  error  and  enhance  downstream  forecast  accuracy  in industrial settings.  Similarly,  Chen  et  al.  (2024)  improved  small-sample  generation  using  a Dual-Layer  Transfer  GAN,  and  studies  by  Asre  &amp;  Anwar  (2022)  and  Yilmaz  &amp;  Korn  (2022) confirmed  that  GANs  can  replicate  temporal  statistics  of  aggregated  or  household-level  energy data. However, these works did not incorporate household billing constraints, did not operate at the appliance  level,  and  did  not  address  reconstructing  long  missing  periods  from  short  monitoring windows.  Building  on  the  core  strengths  identified  in  these  studies,  temporal  preservation, imbalance handling, small-sample robustness, and statistical  fidelity,  our methodology adapts an Improved-TimeGAN-style approach to household data. We train the generator using two months of real daily household load curves, then synthesize daily sequences for the missing months. Unlike previous  GAN  works,  we  scale  each  month's  synthetic  load  to  exactly  match  the  household's Meralco bill and then decompose the scaled load into appliance-level profiles using real appliance energy  shares.  This  produces  a  physically  consistent,  seasonally  aligned,  and  economically accurate 12-month appliance-level dataset suitable for SARIMAX forecasting and cost estimation, something not achieved in any prior GAN-based literature.

From  there,  our  forecasting  methodology  builds  on  statistical  and  adaptive  modeling strategies found in previous work, but extends them to handle hourly appliance-level demand in a way that is both explainable and deployable. Earlier forecasting studies such as Shadkam (2020),

Muñoz  (2023),  and  Kienhuis  (2023)  showed  that  Seasonal  ARIMA/SARIMAX  with  exogenous variables, combined  with  pre-model  tests  like  the  Augmented  Dickey-Fuller  (ADF)  test  for stationarity,  can  accurately  forecast  building-level  or  campus-level  load.  These  works  also  used differencing and seasonal differencing to stabilize non-stationary series before fitting the model. At the  same  time,  residential  forecasting  literature  (Ma,  2023)  and  appliance-level forecasting work (Chen, 2025) stressed two problems: (1) occupant behavior shifts over time, and (2) static SARIMA configurations  underperform  when  patterns  drift.  Drawing  from  these  findings,  our  methodology applies ADF-based differencing, autocorrelation analysis for seasonal detection, and appliance-specific model  identification rather  than  a  one-size-fits-all  seasonal  structure.  We evaluate  multiple  seasonal  orders  and  determine  the best configuration using information criteria and  forecast  error  metrics,  then  validate  each  appliance's  model  using  rolling-origin  evaluation, which mirrors real deployment more closely than the static train/test splits used in earlier studies.

Finally,  our  validation  strategy  draws  from  both  statistical  diagnostics  and interpretability requirements  identified  in  previous  literature.  Shadkam  (2020)  emphasized  residual  diagnostics (ACF, PACF, Ljung-Box), while Ma (2023) highlighted the need for interpretable diagnostics that help identify where and why forecasts fail. Inspired by these findings, we use MAE, RMSE, MAPE, and R² alongside residual whiteness tests, and generate visual diagnostics including forecast-error heatmaps,  per-appliance  residual  boxplots,  and  error-temperature  relationships.  This  creates  a validation loop that is not only statistically rigorous but also operationally transparent.

## 2.7 Theoretical Framework

This  section  presents  the theoretical foundation that underpins the framework adopted in this study. It outlines the Modified Box-Jenkins Methodology proposed by Arash Shadkam (2020), a  structured  and  iterative  approach  to  developing, training, and validating time-series forecasting models.  The  framework,  specifically  tailored  to  energy  consumption  forecasting,  integrates  both traditional and extended elements to ensure a comprehensive approach to data processing, model development, and evaluation.

Step

Input

Operation

Output

Data Collection and preprocessing

Data

Data collection

Extract data o Load data

· Weather data

preprocessing

Identification

Domain

Figure 2.1. Modified Box-Jenkins methodology

<!-- image -->

The Modified Box-Jenkins Methodology, which is an extension of the classical Box-Jenkins approach for time-series  forecasting,  provides  the  analytical  foundation  for  this thesis, offering a structured and iterative approach for developing, training, and validating time-series models. In this study,  the  SARIMAX  (Seasonal  AutoRegressive  Integrated  Moving  Average  with  eXogenous factors) model is used to forecast energy consumption. The traditional Box-Jenkins methodology is typically  divided  into  three  primary stages: Identification, Estimation, and Diagnostic Checking. In this  research,  we  extend  this  framework  by  incorporating  two  additional  critical  steps:  Data Collection and Preprocessing at the start and Performance Evaluation at the end. This modification creates  a  robust,  five-stage  process that is highly applicable to real-world smart energy systems, ensuring that the data is properly handled and evaluated before forecasting takes place.

The Conceptual Framework serves as the system architecture that directly implements the theoretical  Modified  Box-Jenkins  workflow,  ensuring  a  smooth  and  logical  flow  from  raw  data  to actionable user insights. The process begins with Data Collection, where essential inputs such as Appliance Metadata, Smart Plug Data, Weather Data, and Tariff Data are gathered. This raw data then  moves into the next stage, Data Preprocessing &amp; Preparation, where it undergoes cleaning, validation,  and  transformation.  This  aligns  with  the  theoretical  step  of  Preprocessing  in  the

Train the SARIMAX

model

Estimation and

Diagnostics

Forecasting

Performance evaluation

Performance metrics

Box-Jenkins methodology, where data is processed and prepared for time-series modeling. This preparation is crucial to ensure the dataset is suitable for the subsequent model training.

In  the  core  of  the  analytical  process  lies the Forecasting Model, which executes the key stages of the traditional Box-Jenkins methodology. It starts with Pre-modeling Checks, corresponding  to  the  Identification  step,  where  the  appropriate  SARIMAX  model  structure  is determined  based  on  the  characteristics  of  the  data.  This  is  followed  by  Estimation,  where  the optimal  parameters  (such  as  p,  d, q, P, D, Q) are identified through a grid search process, using criteria like the AIC score. Next, Diagnostics are performed to evaluate the model's residuals and ensure its statistical robustness, which mirrors the Diagnostic Checking step in Box-Jenkins. Once the model is validated, it moves into the Forecasting phase, where energy consumption predictions are generated.

Following  forecasting,  the  system  enters  the  Performance  Evaluation  phase,  where  the forecasted  consumption  values  are  combined  with  Tariff  Data  to  perform  Cost  Estimation.  This estimated  cost  is  then  monitored  by  the  Budget  Threshold  &amp;  Alert  Engine,  which  ensures  the practical  value  of  the  forecast  by  providing  alerts  if  the  predicted  costs  exceed  the  set  budget. Finally, the results are communicated to the user through the Web Dashboard &amp; Visualization and Mobile Notifications, delivering both analytical insights and actionable information.

## 2.8 Conceptual Framework

To  provide  a  clear  overview  of  the  study's  methodological  flow,  Figure  2.2  presents  the conceptual framework of this study, which adopts the Input-Process-Output (IPO) model. It traces the flow from inputs through  processing  to  outputs,  describing  how  the  system  forecasts appliance-level electricity  consumption,  estimates  cost,  and  delivers  user  visualizations  and notifications.

TUYA Smart Plug

OpenWeatherMap

Household Survey

Meralco Rate

Smart Plug Data

Weather Data

Data Preprocessing

&amp; Preparation

· Data Integrity

Standardization

Verification and

· Data Cleaning and

Forecasting Model

· Pre-modeling Checks

· SARIMAX Forecasting

Model

· Model Evaluation and

<!-- image -->

Error Analysis

Web Dashboard &amp;

Visualization

Mobile Notification

Figure 2.2. Conceptual Framework of the Appliance-Level Electricity Consumption Forecasting and Cost Estimation System

The  conceptual  framework  for  this  study  begins  with  four  key  inputs:  smart  plug  data, weather  data,  appliance  metadata,  and  tariff  information.  Among  these,  the  smart  plug  data, weather data, and appliance metadata form the primary sources feeding into the data preparation workflow.  Smart  plug  data  provides  high-resolution  appliance-level  electricity  measurements, weather data captures external environmental  conditions that  influence  consumption,  and appliance metadata supplies descriptive information such as appliance type, wattage, and location. Tariff data, meanwhile, is reserved for the system's cost estimation stage.

These  inputs  first  enter  the  Data  Preprocessing  and  Preparation  phase,  where  raw measurements are transformed into a clean, consistent, time-aligned dataset suitable for modeling. This  phase  begins  with  data  integrity  verification  and standardization, ensuring that all input files follow  the  required  schema  and  that  units  such  as  volts,  watts,  and  timestamps  are  properly aligned. The system then proceeds to data cleaning and energy derivation, applying physics-based checks, tolerance rules, fallback estimation, and cumulative-energy validation to produce accurate 10-minute  interval  energy  readings.  Because  the  forecasting  model  operates  on  an  hourly timescale,  the  validated  10-minute  intervals  are  aggregated  into  hourly  energy  totals  and paired with their corresponding  hourly  weather  observations.  Additional features,  such  as  lagged consumption, rolling averages, and time-based indicators, are created during feature construction. Finally, the data undergoes final transformation, producing a modeling-ready dataset representing two months of real historical measurements.

To  extend  this limited real dataset into a full historical window, the processed real data is passed to the Synthetic Data Generation Using TimeGAN module. Using the Improved TimeGAN architecture  discussed  in Section 3.5, the system learns daily consumption patterns from the real data  and  reconstructs  an  additional  twelve  months  of realistic 10-minute appliance-level profiles. These  synthetic  months  are  then  denormalized,  scaled  to  match  Meralco  billing  totals,  and decomposed  into  appliance-level  components,  yielding  a  complete  14-month,  high-resolution dataset.  This  expanded  dataset  is  then  looped  back  into  the  preprocessing  pipeline,  where  it  is aligned and synchronized with the real data to ensure full compatibility with the forecasting model.

Once consolidated, the 14-month dataset enters the Forecasting Model stage. This stage begins  with  pre-modeling  checks,  such  as  stationarity  testing,  seasonality  detection,  and  initial SARIMAX  identification.  The  SARIMAX  forecasting  model  is  then  trained  using  the  merged real-and-synthetic dataset, allowing it to capture both daily and long-term seasonal patterns. After training,  the  model  generates  24-hour  ahead  appliance-level  energy  forecasts,  incorporating exogenous  factors  such  as  weather,  day  type,  and  temporal  features.  Model  performance  is rigorously  assessed  using  error  metrics  and  rolling-origin  validation  to  ensure  that  predictions remain reliable and consistent.

The resulting  forecasts  flow  into the Cost Estimation module. Here, the predicted energy consumption  is  combined  with  tariff  data  to  compute  estimated  electricity  costs.  This  cost information  is  also  passed  to the Budget Threshold and Alert Engine, where users can configure consumption or cost limits. When forecasts indicate that a user's usage or cost is likely to exceed their set threshold, the system automatically triggers alerts.

Finally,  the  system  produces  two  core  outputs.  First,  a  web dashboard and visualization interface presents users with detailed insights on real consumption, synthetic trends, forecasts, and projected costs. Second, a mobile notification system sends real-time alerts and summary updates directly to the user's device. Together, these outputs ensure that the user is continuously informed and can make proactive decisions based on both actual and forecasted energy behavior.

## CHAPTER III METHODOLOGY

This  chapter  presents  the  methods  and  procedures  to  be  undertaken  in  conducting  the study.  It  outlines  the  research  design,  data  collection,  and  data  processing  methods  that will be applied  in  developing  the  appliance-level  electricity  consumption  forecasting  and cost estimation system.  It  further  describes  the  proposed  modeling  approach,  system  implementation  plan,  and validation procedures intended to ensure the accuracy and reliability of the prototype system.

## 3.1 Research Design

This  section explains the overall research design and methodological flow adopted in the study. It outlines the type of research conducted, the logical approach used to achieve the study's objectives,  the  respondents  who  will  participate,  and  the  implementation  of  the  preliminary household survey that guides appliance selection. The  study  will employ  a  Quantitative Applied-Developmental  Research  Design  with  Descriptive  and  Predictive  Components.  Each component of this design plays a distinct role in the conduct of the research.

## 3.1.1 Research Approach

Building upon the adopted research design, the study follows a structured methodological approach that connects descriptive analysis, predictive modeling, and applied system development into a single continuous process.

The  quantitative  aspect  lies  in  the  collection  and  analysis  of  numerical  data  from  smart sockets and weather APIs. The entire process, from energy measurement to statistical forecasting, relies  on  numerical  computations  and  objective  accuracy  metrics.  The  descriptive  component focuses on examining household energy use behavior before forecasting. It identifies appliances that  contribute  most  to  overall  consumption,  determines  periods  of  peak  demand,  and observes how exogenous patterns influence usage.

The  predictive  component  is  embodied  in  the  modeling  phase,  where  a  Seasonal AutoRegressive  Integrated  Moving  Average  with  Exogenous  Variables  (SARIMAX)  model  is

developed  to  forecast  appliance-level  electricity  consumption  up  to  twenty-four  hours  ahead. Meanwhile,  the  applied-developmental  nature  of  the study is reflected in  the  design  and implementation  of  a  working  system  prototype  that  integrates  data  collection,  preprocessing, forecasting, cost estimation, and alert functions, transforming research outputs into a practical tool for real-world energy awareness and management.

Although the study collects data from a selected participating household, its primary focus is not to generalize specific consumption behaviors but to validate a methodological framework for appliance-level  electricity  forecasting.  It  aims  to  demonstrate  that  combining  household-level energy  data  with  exogenous  variables  under  the  SARIMAX  algorithm  significantly  improves forecasting accuracy compared to models without such features. Thus, while the implementation is household-specific, the proposed process remains replicable and adaptable  across  other residential settings with similar data availability.

## 3.1.2 Research Respondents

The  respondents  of  the  study  consist  of  a  residential  household  located  in  Parañaque, Metro  Manila,  selected  through  convenience  sampling  and  operating  under  standard  Meralco residential tariff conditions. The participating household is excluded from the Peak/Off-Peak (POP) and Time-of-Use (TOU) programs to ensure that the recorded consumption reflects normal usage behavior unaffected by time-based pricing schemes. The selected household serves as a suitable implementation site for appliance-level energy monitoring, forecasting, and system validation under realistic residential conditions.

## A. Sampling Technique

The  study  utilizes  Convenience  Sampling,  a  non-probability  sampling  method  in  which respondents are selected based on accessibility, availability, and their ability to meet the technical and  operational  requirements  of  the  study.  This  sampling  approach  is  appropriate  for  applied developmental  research  that  involves short-term, high-resolution appliance-level monitoring, system prototyping, and methodological validation rather than population-level inference.

The participating household must meet the following conditions at the time of selection:

- Located in Parañaque, Metro Manila
- Using the standard Meralco Residential Rate (R-1)
- Not enrolled in Peak/Off-Peak (POP) or Time-of-Use (TOU) programs
- With stable Wi-Fi connectivity to support cloud-based data logging
- Willing to allow smart-plug installation and make appliances accessible for monitoring
- Capable of continuous 10-minute interval data collection for a minimum of two months
- Willing  to  provide  access  to  historical  Meralco  electricity  bills  for  energy  scaling  and validation
- Having  a  safe  and  suitable  environment  for  IoT  device  installation  in  compliance  with electrical safety standards

Convenience sampling is appropriate because probability-based sampling is not feasible for studies that require physical access to private residences, installation of IoT monitoring devices, and continuous short-term appliance-level  data  collection  under  controlled  conditions.  The study further  requires  stable  network  infrastructure,  user  cooperation  over  an  extended  monitoring period, and integration of external data sources such as weather and tariff information, all of which limit the practicality of random household selection.

Given  these  constraints,  convenience  sampling  allows  the  researcher  to  ensure  data completeness,  system  reliability,  and  participant  safety,  which  are  critical  for  validating  the forecasting  methodology  and  evaluating  the  functional  performance  of  the  proposed  system prototype.

## B. Research Population &amp; Sample Size

The  broader  population  relevant  to  the  study  consists  of  residential  households  in Parañaque, Metro Manila, operating under the standard Meralco Residential Service Rate (R-1). According to the Philippine Statistics Authority (PSA), Parañaque recorded 182,216 households in the 2020 Census of Population and Housing.

This  population  context  is provided to define the residential scope of the study; however, the research does not aim to draw statistical generalizations across this population.

The study employs one (1) residential household as its research respondent, with three (3) household appliances selected for continuous monitoring. The sample size is intentionally limited due  to  the  applied  and  developmental  nature  of  the  research,  which  prioritizes  methodological validation and system functionality over population-level representation.

## C. Methodological Rationale

Despite  the limited number  of  respondents,  the  study  does  not  aim  to  generalize consumption  patterns  across  Parañaque,  Metro  Manila  households.  Instead,  the  objective  is  to validate  an  appliance-level  energy  forecasting  methodology  and  integrate  it  into  a  functional monitoring and cost estimation system prototype.

The three appliances monitored within the household are selected based on responses to a  preliminary  household  intake  form.  This  ensures  that  commonly  used  and  energy-relevant appliances are captured, allowing diverse and meaningful appliance usage profiles to be observed and ensuring that the forecasting framework is tested under realistic residential conditions.

To  ensure  ethical  compliance,  the  participating  household  is fully informed of the study's objectives, procedures, and scope prior to participation.  Informed  consent  and  voluntary participation  are strictly observed, with the right to withdraw at any time without consequence. All collected household and personal data from the participating household are anonymized, securely stored,  and  handled  in  accordance  with  the  Data  Privacy Act of 2012 (Republic Act No. 10173). Non-maleficence  and  safety  are  upheld  through  the  proper  handling  of  smart  sockets  and prototype equipment following established electrical safety standards. Ethical approval, permission letters, and participant consent forms are secured prior to data collection to ensure full compliance with research ethics and data protection principles.

## 3.1.3 Research Appliance Selection

Before  data  collection  begins,  the  participating  household  is  informed  of  the  study's objectives, procedures, and scope. Informed consent is obtained to ensure voluntary participation

and  compliance  with  the  Data  Privacy  Act  of  2012  (Republic  Act  No.  10173).  All  collected household information is anonymized and treated with strict confidentiality throughout the study.

The study employs a household intake form as a preliminary data-gathering instrument. This form is completed by the participating household and serves to identify which appliances will be included in the monitoring setup. The form is concise and structured, collecting information on commonly  used  appliances,  their  usage  characteristics,  and  their  perceived  importance  in  daily household activities.. Appliance selection follows these criteria:

1. Frequency of Use - Operated regularly or multiple times per day.
2. Power Consumption - Contributes significantly to total household electricity usage.
3. Predictable Usage Pattern - Exhibits consistent behavior suitable for forecasting.
4. Operational Necessity - Essential or non-negotiable in daily household activities.
5. Device Compatibility - Only appliances within the allowable load rating and safe operating range of the Tuya Smart Socket (discussed in Section 3.2.1) were eligible for installation. Appliances whose wattage exceeded the smart socket's rated capacity were excluded for safety and equipment protection.

Based on the responses captured in the household intake form, the selected appliances undergo continuous monitoring. This approach  ensures  that  the  recorded  data  focus  on energy-relevant  and  commonly  used  appliances,  while  complying  with  safety  requirements  and hardware compatibility constraints.

.

## 3.2 Data Collection Procedures

This  section  describes  how  the  data  required  for  the  study  are gathered and organized. Data  collection begins  with smart  sockets  recording independent  appliance-level  electricity consumption  for  each  monitored  device,  followed  by  the  acquisition  of  appliance  metadata, weather data, and electricity  tariff  rates.  These  datasets  form  the  foundation  for forecasting and cost estimation. Because each smart socket tracks one appliance separately, the system produces three  (3)  distinct  time-series  datasets,  one  for  each  monitored  appliance,  which  will  later  be processed and modeled individually rather than combined into a single multivariate sequence.

V

A

R

I

A

L

E

S

Appliance

Weather

OpenWeatherMap

TUYA

→

Smart Plug

Metadata →

CSV

TARIFF

Rate

CSV

API

ablo

Logger

CSV

Figure 3.1. Overview of the Data Collection Process

<!-- image -->

As shown in Figure 3.1, an appliance is connected to a SMATRUL Tuya Smart Socket, which transmits  real-time  readings  to  the  Tuya  Cloud  API.  A  Python-based  logger  running  on  a cloud  virtual  machine  (VM)  retrieves  these  readings  and  stores  them  in  CSV  files.  Appliance metadata are recorded separately as a reference file. Weather information is gathered hourly from the  OpenWeatherMap API, while tariff data is  independently  compiled  from  official  Meralco  rate advisories. Together, these four datasets constitute the complete inputs for the study's forecasting and cost estimation components.

## 3.2.1 Hardware and Instrumentation

The data collection process begins with the installation of SMATRUL Tuya Smart Sockets, which serve as the main sensing instruments for appliance-level monitoring. These Wi-Fi-enabled smart  plugs  contain  built-in  energy  sensors  capable  of  recording  electrical  parameters  such  as voltage (V), current (A), and power (W), and automatically computing the total energy consumption (kWh) over time. Each selected appliance is connected to a SMATRUL Tuya Smart Socket, which transmits readings at ten-minute intervals via the Tuya Cloud API Once connected to a household's Wi-Fi network, each socket communicates directly with the Tuya Cloud API. The device transmits

58mm

45mm readings every ten minutes, ensuring regular data acquisition while remaining within the developer plan's  monthly  limit.  The  participating  household  operates  under  a  dedicated  Tuya  IoT  Project account.

33mm

After deployment,  the  smart  plug begins  logging data automatically  whenever  the connected  appliance  is  in  use.  The  recorded  readings  are  accessed  by  a  Python-based  logger running  on  a  cloud  virtual  machine (VM) configured for continuous operation, which retrieves the data  from  the  Tuya  Cloud  API  and  stores  them  in  a  local  CSV  file.  The  complete  hardware specifications of the SMATRUL Tuya Smart Socket are summarized in Table 3.1, while Figure 3.2 presents the actual device used for data collection.

Table 3.1. SMATRUL Tuya Smart Socket Specifications

| Component             | Description                             |
|-----------------------|-----------------------------------------|
| Brand                 | SMATRUL Tuya Smart Socket (Wi-Fi, 16 A) |
| Logging Frequency     | 10-minute interval (600 s)              |
| Connectivity          | Wi-Fi 2.4 GHz                           |
| Data Access           | Tuya Cloud API (developer access)       |
| Rated Load            | 100-250 V AC, 16 A / 3000 Wmax          |
| Operating Temperature | -20 °C to 60 °C                         |

Figure 3.2. SMATRUL Tuya Smart Socket

<!-- image -->

The device is designed for standard household use, equipped with built-in protection and compliant with international safety and performance standards. It carries the Federal Communications Commission (FCC) certification, which verifies that the socket's Wi-Fi components operate safely within approved frequency ranges and without causing interference.

## 3.2.2 Data Logging Setup

This section describes how the system continuously records and stores readings from the Tuya  Cloud  API  using  an  automated,  cloud-based  logging  process.  The  logging  process  is managed  through  a  Python-based  automation  script  that  communicates  directly  with  the  Tuya Cloud API. Every ten (10) minutes, the script retrieves the latest readings from the three (3) active smart  plugs  registered  under  the  participating  household's  Tuya  account.  The  data  retrieval program  runs  continuously  on  a  Cloud  Virtual  Machine  (Microsoft  Azure),  provided  through  the first-year  academic  credits.  The  Azure  environment  hosts  a  daemon-style  Python  process designed  for  continuous,  automated  data  logging.  This  process  operates  independently  of  local computers, ensuring 24/7 operation even when on-site machines are turned off. Once fetched, all readings are stored in a local CSV file. For efficient data management, each monitored appliance is assigned a dedicated CSV  file that stores its individual readings. This structure allows appliance-level tracking, and aligns with the system's objective of forecasting energy consumption per appliance.

To maintain data integrity during unexpected interruptions, a fallback estimation mechanism is implemented. When brief data gaps occur, the system uses a fallback variable to interpolate missing values based on the most recent valid readings. This method preserves dataset continuity across the monitoring timeline.

## 3.2.3 Collected Variables

After the hardware setup and data logging systems have been established, the next stage involves  gathering  the  variables  required  to  characterize  household  electricity  consumption.  The data collection process integrates multiple sources to capture both appliance-level and contextual factors  influencing  energy  use.  Real-time  measurements  from  the  Tuya  Cloud  API  serve  as the primary  dataset,  recording  actual  power  consumption  from each connected appliance. Alongside

these,  appliance  metadata  are  gathered  to  describe  device  characteristics,  weather  data  are retrieved  to  represent  environmental  conditions,  and  electricity  tariff  records  are  collected  to provide cost references for later estimation.

As shown in Table 3.2, it   summarizes their  respective  sources,  frequency of collection, and intended use.

Table 3.2. Summary of Collected Variables

| Source              | Medium                | Frequency        |
|---------------------|-----------------------|------------------|
| Appliance Metadata  | Device Registration   | Once             |
| Smart Plug Readings | Tuya Cloud API        | Every 10 minutes |
| Weather Data        | OpenWeatherMap API    | Hourly           |
| Tariff Data         | Meralco Official Site | Monthly          |

## A. Appliance Metadata

These selected appliances are then individually registered and assigned to corresponding SMATRUL Tuya Smart Sockets for real-time monitoring. Each registered appliance is documented in  an  appliance  metadata  sheet,  which  links  the physical device to its corresponding smart plug. This metadata serves as the reference layer that allows every energy reading to be traced back to a specific appliance and household.

The variable household\_id designates the participating household (H1), while appliance\_id follows  the  naming  convention  1H1P,  which  represents  the  first  household and first plug pairing. The internal label device\_id records the unique Tuya-assigned identifier of the smart socket used for monitoring that appliance, allowing easier cross-referencing between the Tuya device ID and its corresponding  metadata.  The  appliance\_name  specifies  the  type  of  device,  and  brand\_model documents  the  manufacturer  and  model  name  for  validation  purposes.  The  rated\_power\_watts refers  to  the  nominal  power  requirement  indicated  on  the  device  label,  while  voltage\_rating represents  the  operational  voltage  range,  typically  220-240  V  AC.  These  metadata  variables describe the characteristics of each monitored appliance.

To  provide  a  clear  overview  of  the  metadata  structure,  Table  3.3  presents  the  list  of variables used, along with their corresponding data types, formats, and descriptions

Table 3.3 Appliance Metadata Variables Structure

| Variable Name      | Type        | Format / Example          | Description                                                           |
|--------------------|-------------|---------------------------|-----------------------------------------------------------------------|
| household_id       | Categorical | H1, H2, H3                | Identifies the participating household.                               |
| appliance_id       | String      | 1H1P, 2H1P                | Unique internal code linking a household and its monitored appliance. |
| device_id          | String      | bf12abc345xyz             | Tuya-assigned smart socket identifier used for API mapping.           |
| appliance_name     | String      | Electric Fan, Rice Cooker | Appliance type/name used for classification.                          |
| brand_model        | String      | Asahi CF-835              | Manufacturer and model for reference and validation.                  |
| rated_power_watt s | Integer     | 65 W, 800W                | Nominal power rating of the appliance.                                |
| voltage_rating     | String      | 220-240 V AC              | Operating voltage range compatible with the smart plug.               |

In addition, a sample entry for illustrative purposes is also shown in Table 3.4.

Table 3.4. Sample Appliance Metadata Variables

| household_i d   | appliance_id   | device_id      | appliance_n ame   | brand_mode l   | rated_power _watts   | voltage_rati ng   |    |
|-----------------|----------------|----------------|-------------------|----------------|----------------------|-------------------|----|
| H1              | 1H1P           | bf12abc345 xyz | Electric Fan      | Asahi CF-835   | 65W                  | 220-240 AC        | V  |

## B. Smart Plug Variables

Once  registered,  the  system  begins  recording  electrical  measurements  every  ten  (10) minutes.  Each  record  contains  both  raw  and  processed  variables  to  ensure  data  verification capability.  Although  the  Tuya  smart  plug  provides  only  the  raw  measurements  (voltage, current,

power,  cumulative  energy,  switch  status,  device  identifier,  and  timestamp),  the  logging  script expands these readings into additional  variables  for  validation  and  analysis.  The  logger records both the raw data point values and their processed equivalents, and also computes derived fields such as power factor (pf).

The timestamp field marks the exact time of data collection in UTC + 8 (DateTime), while the  device\_id  (String)  associates  each  record  with  its  corresponding  Tuya  Smart  Socket.  Core electrical parameters  include  voltage\_v  (supply  voltage,  volts  [V]),  current\_a  (instantaneous current,  amperes  [A]),  and  power\_w  (real-time  power  draw,  watts  [W]).  The  cumulative  energy reading  for  each  device  is  stored  as  kwh\_total  (kilowatt-hours  [kWh]),  while  switch  (Boolean) represents  the  device's  operational  status,  recorded  as  True  when  the  socket  is  ON  and  False when it is OFF. The pf (decimal value) variable, or power-factor estimate, provides an indicator of electrical  efficiency, while additional raw parameters, such as voltage\_raw (volts [V]), current\_raw (amperes  [A]),  power\_raw  (watts  [W]),  and  kwh\_raw  (kilowatt-hours  [kWh]),  are  retained  for cross-checking and validation.

To provide a clear overview of these measurements, Table 3.5 presents the complete list of smart-plug variables, their data types, formats/units, and descriptions.

| Variable Name   | Type     | Format / Unit        | Description                                                      |
|-----------------|----------|----------------------|------------------------------------------------------------------|
| timestamp       | DateTime | YYYY-MM-DD HH:MM:SS  | Exact moment the reading was logged (UTC+8).                     |
| device_id       | String   | e.g., bf12abc345xy z | Tuya-assigned identifier of the smart socket.                    |
| switch          | Boolean  | True / False         | Indicates whether the socket is turned ON (True) or OFF (False). |
| voltage_raw     | Float    | Volts (V)            | Raw voltage reading retrieved directly from the Tuya API.        |
| current_raw     | Float    | Amperes (A)          | Raw current measurement before validation.                       |

Table 3.5. Smart Plug Variables Structure

| power_raw   | Float   | Watts (W)   | Raw instantaneous power reading from the API.       |
|-------------|---------|-------------|-----------------------------------------------------|
| kwh_raw     | Float   | kWh         | Raw cumulative energy counter from the device.      |
| voltage_v   | Float   | Volts (V)   | Cleaned and validated voltage value.                |
| current_a   | Float   | Amperes (A) | Cleaned and validated current value.                |
| power_w     | Float   | Watts (W)   | Cleaned and validated real-time power draw.         |
| kwh_total   | Float   | kWh         | Validated cumulative energy value.                  |
| pf          | Float   | 0.00-1.00   | Estimated power factor based on validated readings. |

In  addition,  a  sample  of  all  recorded  variables for illustrative purposes is shown in Table 3.6.

Table 3.6 Sample Smart Plug Data Record

| timestamp            | devide_id      | switch   |   voltage_ra w |   current_ra w |   power_ra w |   kwh_raw |   voltage_v |   current_a |   power_w |   kwh_total |   pf |
|----------------------|----------------|----------|----------------|----------------|--------------|-----------|-------------|-------------|-----------|-------------|------|
| 2025-10-1 7 08:00:00 | bf12abc34 5xyz | True     |          228.5 |           0.31 |         70.8 |     0.024 |       228.5 |        0.31 |      70.8 |       0.024 | 0.92 |
| 2025-10-1 7 08:10:00 | bf12abc34 5xyz | True     |          227.9 |           0.29 |         66   |     0.036 |       227.9 |        0.29 |      66   |       0.036 | 0.91 |
| 2025-10-1 7 08:20:00 | bf12abc34 5xyz | True     |          229.3 |           0.32 |         72.5 |     0.048 |       229.3 |        0.32 |      72.5 |       0.048 | 0.92 |

## C. Weather Variables

To capture external usage  influences, the  study  integrates  weather  data,  such  as temperature,  humidity,  and rainfall, as exogenous variables that will later be used to enhance the accuracy of forecasting models.

## C.1 Primary Data Source

The OpenWeatherMap API serves as the primary source of weather data for this study. It enables hourly data logging, allowing the system to capture weather variations simultaneously with appliance-level  energy  readings.  The  API  supports  up  requests per day under its free developer plan, which is sufficient enough for the participating household.

A Python-based script running on the Cloud Virtual Machine (Microsoft Azure) retrieves the latest temperature, humidity, and rainfall measurements at hourly intervals. Each record includes a local  timestamp  (DateTime,  UTC  +8),  ensuring  alignment  with  appliance  energy  data  collected through  the  Tuya  Cloud  API.  The  temperature  variable  represents  the  ambient  air  temperature measured in degrees Celsius (°C), while humidity denotes the relative humidity expressed as a percentage  (%).  The  rainfall  variable  indicates  the  amount  of  precipitation  recorded  within  the previous  hour,  measured  in  millimeters  (mm).  To  clearly  present  the  structure  of  the  weather dataset, Table 3.7 lists the variables, their types, formats, and descriptions.

Table 3.7 Weather Variables Structure

| Variable Name   | Type     | Format / Unit        | Description                                                       |
|-----------------|----------|----------------------|-------------------------------------------------------------------|
| timestamp       | DateTime | YYYY-MM-DD HH:MM:SS  | Local time (UTC+8) at which the weather measurement was recorded. |
| temperature     | Float    | Degrees Celsius (°C) | Ambient air temperature at the recorded time.                     |
| humidity        | Float    | Percentage (%)       | Relative humidity level at the recorded time.                     |
| rainfall        | Float    | Millimeters (mm)     | Precipitation amount recorded during the previous hour.           |

Additionally, a sample of the recorded weather variables for illustrative purposes is shown in Table 3.8.

Table 3.8. Weather Variables

| timestamp           |   temperature |   humidity |   rainfall |
|---------------------|---------------|------------|------------|
| 2025-10-17 08:00:00 |          32.4 |        6.7 |          0 |

## C.2 Supplementary Data Source

The  Meteostat  API  is used  as  a  supplementary  data  source  for  verification  and comparison. It provides historical  weather  records,  some  sourced  from  PAGASA-affiliated meteorological  stations,  though  with  a  typical  one-day  delay  in  availability.  Once  the  monitoring period  concludes,  a  complete  Meteostat  dataset  covering  the  same  timeframe  is  retrieved  for cross-checking accuracy.

## D. Meralco Tariff Variables

To achieve an accurate reference to the prevailing residential tariff rates, the study collects monthly tariff data directly from the official Meralco rate advisories, which are publicly released at the  beginning of each billing month. These advisories provide the total cost of electricity in pesos per kilowatt-hour ( ₱ /kWh), reflecting the combined charges for generation, transmission, distribution, system loss, and government taxes.

Each  tariff  record  includes  the  month\_start  (DateTime)  representing  the  first  day  of  the rate's validity period, the month\_end (DateTime) marking when it expires, and the tariff\_rate (pesos per  kilowatt-hour, ₱ /kWh)  indicating  the  total  residential  electricity  rate  applied  for  that  billing month.  These  tariff  records  serve  as  the  official  reference  data  used  by  the  system's  cost estimation component.

To provide a clear overview of the structure and meaning of each tariff variable, Table 3.9 summarizes the fields, types, formats, and descriptions.

Table 3.9 Meralco Tariff Variables

| Variable Name   | Type            | Format / Unit   | Description                                                                          |
|-----------------|-----------------|-----------------|--------------------------------------------------------------------------------------|
| month_start     | DateTime        | YYYY-MM-DD      | First day of the tariff's validity period, based on the official Meralco advisory.   |
| month_end       | DateTime        | YYYY-MM-DD      | Last day the tariff applies before a new adjustment is released.                     |
| tariff_rate     | Float / Decimal | ₱ /kWh          | Total residential electricity rate in pesos per kilowatt-hour for the billing month. |

Furthermore, a sample of the recorded tariff variables for illustrative purposes is presented in Table 3.10.

Table 3.10 Meralco Tariff Variables

| month_start   | month_end   | tariff_rate   |
|---------------|-------------|---------------|
| 2025-10-01    | 2025-10-31  | ₱ 11.95       |

To  validate  accuracy,  the  study  also  utilizes  the  Meralco  Appliance  Calculator, an online tool  that  estimates  household  electricity  costs  based  on  power  rating,  duration  of  use,  and  the prevailing tariff rate. This  comparison  ensures  that  the  system's  computed  results  remain consistent with actual household billing estimates.

## E. Big Data Characteristics (4 V's)

The complete dataset used in this study, consisting of two months of real high-resolution smart-plug  measurements and twelve months of synthetic TimeGAN-generated profiles, exhibits the  qualitative  characteristics  of  Big  Data  within  the  context  of  IoT-driven  residential  energy monitoring.  Although  the  system  operates  at  the  household  scale,  the  continuous,  multi-source, and  heterogeneous  nature  of  the  data  aligns  with  the  4V's  of  Big  Data.  Understanding  these characteristics  is  essential  because  they  influence the design of the data pipeline, preprocessing workflow, synthetic generation procedures, and forecasting model.

## 1. Volume

Smart  plugs  record  measurements  every  10  minutes,  producing  144  readings  per appliance per day.

Over the actual two-month monitoring period (60 days), each appliance generated: 144 x 60 = 8, 640 real observations.

With (3) monitored  appliances,  the real dataset contains: 8, 640  x  3  =  25,  920 appliance-level real records.

When the twelve (12) synthetic months are appended using TimeGAN for the same three appliances, an additional: 144 x 305 synthetic days x 3 appliances = 131, 760 synthetic records are added to the dataset.

This  results  in 157,680 appliance-level records at a 10-minute resolution. Hourly weather data  contributes  an  additional  8,760  entries,  which  are  synchronized  with  the  energy  dataset. Overall, the final dataset comprises approximately 166,440 records across all data sources.

Although  the  full  dataset  contains  approximately  157,  680  ten-minute  observations,  the data  used  for  SARIMAX  forecasting  is  aggregated  to  hourly  intervals.  Aggregation  reduces  the series  to  hourly  points  per  appliance,  improving  model  stability  while  maintaining  the  original volume characteristics for the Big Data assessment.

This extended volume introduces data engineering challenges typical of Big Data systems:

- Higher storage requirements due to long-term high-frequency data
- Greater computational cost for cleaning, aggregation, and validation
- The need for efficient file structures (organized by appliance and by time)
- Longer historical windows to support annual seasonality and multi-month forecasting

Although small compared  to  enterprise-scale datasets, the final  14-month  dataset becomes  substantial  within  a  residential  IoT  setting  and  is  large  enough  to  require  systematic processing pipelines.

## 2. Velocity

The system handles multiple data streams operating at different time intervals:

- Smart plug telemetry every 10 minutes
- Weather data every hour
- Logger ingestion processes occurring continuously
- Dashboard updates occurring in near real time during system operation

This multi-stream velocity introduces Big Data challenges, such as:

- Real-time ingestion via the Azure VM Python logger
- Handling API delays, missing pings, or intermittent connectivity
- Ensuring synchronization across different update frequencies
- Updating the forecast and cost dashboard with fresh data

Because  forecasting  depends  on  the  most  recent  values,  the  system  must  process incoming data quickly enough to maintain up-to-date consumption profiles. This velocity characteristic directly influences the design of the automation scripts, the fallback estimation rules, and the rate at which the forecasting model is recalculated.

## 3. Variety

The  dataset  integrates multiple heterogeneous  sources,  each  differing  in  structure, purpose, and temporal granularity:

- Real IoT Smart Plug Data: voltage, current, power, and energy (10-minute numerical time series)
- GAN-Generated  Synthetic  Data:  Twelve  (12)  months  of  reconstructed  appliance-level profiles for each monitored appliance, generated to follow validated statistical and temporal patterns.
- Weather Data: temperature, humidity, rainfall (hourly environmental time series)
- Tariff Data: monthly electricity rates (reference table)
- Appliance Metadata: device categories, watt ratings, locations (static descriptive data)

To  demonstrate  the  heterogeneous  structure  of  the  dataset,  the  following tables present sample entries from each data source, illustrating variety:

## A. Smart Plug Data (10-minute intervals)

Table 3.11 Smart Plug Data

| timestamp        | device_id     | switch   |   voltage_raw |   current_raw |   power_raw |   kwh_raw |
|------------------|---------------|----------|---------------|---------------|-------------|-----------|
| 2025-10-17 08:00 | bf12abc345xyz | True     |         228.5 |          0.31 |        70.8 |     0.024 |

## B. Synthetic Appliance Load (10-minute intervals)

Table 3.12 Synthetic Data

| timestamp        |   synthetic_power_w |
|------------------|---------------------|
| 2025-03-01 08:10 |                68.4 |

## C. Weather Data (Hourly)

Table 3.13 Weather Data

| timestamp        |   temperature | humidity   | rainfall   |
|------------------|---------------|------------|------------|
| 2025-10-17 08:00 |          32.4 | 67.0%      | 0.0 mm     |

## D. Tariff Data (Monthly)

Table 3.14 Tariff Data

| month_start   | month_end   | tariff_rate   |
|---------------|-------------|---------------|
| 2025-10-01    | 2025-10-31  | ₱ 11.95       |

## E. Appliance Metadata (Static Descriptive)

Table 3.15 Appliance Metadata

| appliance_id   | appliance_name   | brand_model   | rated_power_watt s   | voltage_rating   |
|----------------|------------------|---------------|----------------------|------------------|
| 1H1P           | Electric Fan     | Asahi CF-835  | 65W                  | 220-240 V AC     |

Each table presents only a simplified subset of variables to illustrate the structural format of each data source, while the full variable definitions are provided in Section 3.2.3. Such diversity requires a flexible and carefully coordinated pipeline capable of:

- Parsing heterogeneous formats and schemas
- Standardizing units and physical scales
- Merging time series with different resolutions
- Aligning real and synthetic datasets into a single continuous structure
- Supporting both consumption forecasting and cost estimation

The inclusion of synthetic months significantly increases dataset variety  because generative models introduce reconstructed temporal sequences that must remain compatible with real-world measurements.

## 4. Veracity

Veracity  refers  to  the  accuracy,  reliability,  and  trustworthiness  of  the  data,  an  essential requirement for forecasting tasks. Both real and synthetic components of the dataset must satisfy high veracity standards.

For  smart  plug  data,  issues  may  arise  during  collection  and  transmission,  resulting  in irregularities or gaps that affect the accuracy of the recorded measurements. These issues include the following:

- Missing 10-minute intervals
- Device measurement errors
- Load fluctuations causing noisy readings
- Cumulative reset anomalies
- Temporary API outages

To address these issues, the data pipeline applies a sequence of validation and correction mechanisms  designed  to  restore  accuracy,  continuity,  and  physical  consistency  in  the  dataset. These measures include the following:

- Physical consistency checks (P = V × I × PF)

- Tolerance rules for detecting abnormal deviations
- Fallback estimation for missing intervals
- Cumulative reset correction
- Validation of hourly totals before modeling

On  the  other  hand,  for  weather  data,  irregularities  may  occur  due  to  API  transmission delays,  temporary  gaps  in reporting, or environmental readings that fall outside expected ranges. These issues may include the following:

- Missing hourly weather points
- API latency
- Occasional irregularities in rainfall or humidity data
- Your system resolves these through:
- Forward-fill imputation
- Timestamp validation
- Accuracy checks based on plausible environmental ranges

To  address  these  issues,  the  preprocessing  workflow  applies  correction  and  validation procedures to ensure environmental data accuracy and completeness. These measures include the following:

- Forward-fill imputation for missing hourly data
- Plausibility checks using realistic environmental thresholds
- Timestamp validation to ensure alignment with energy data
- Consistency checks across temperature, humidity, and rainfall patterns

Furthermore,  for  synthetic  data  veracity,  the  twelve  months  of  reconstructed  data  must match the statistical  distribution  and  temporal structure of the real dataset. This ensures veracity through:

- Statistical comparison (mean, variance, quartiles, skewness, kurtosis)
- PCA similarity analysis
- t-SNE neighborhood consistency plots
- Denormalization and reconstruction checks

## ● Energy-scaling alignment with Meralco bills

These steps ensure that synthetic months remain physically plausible and consistent with the  participating  household's  observed  behavior  High  veracity  across  real,  environmental,  and synthetic  data  ensures  that  the  SARIMAX  forecasting  model  receives  a  clean,  coherent,  and trustworthy  14-month  dataset.  The  resulting  dataset  supports accurate modeling of daily, weekly, and annual patterns and enables robust appliance-level energy forecasting and cost estimation.

## 3.3 Data Preprocessing and Preparation

This  section  describes  how  the  raw  readings  recorded  from  the  Tuya  smart  plug  and weather sources are transformed into a modeling-ready dataset. The preprocessing stage ensures that all recorded values are physically consistent, temporally continuous, and properly synchronized with the corresponding environmental conditions before being used for forecasting and  analysis.  The  procedure  follows  a  four-stage  sequence:  (1)  Data  Integrity  Verification  and Standardization, (2) Cleaning  and  Energy  Derivation,  (3)  Hourly  Aggregation  and  Feature Construction, and (4) Final Dataset Assembly.

It  is  important  to  note  that  only  the  smart-plug  and  weather  datasets  undergo  the preprocessing and preparation procedures. Meanwhile, the appliance metadata serves only as a descriptive  reference,  and  the  electricity  tariff  is  separately  used  for  cost  computations  in  later stages.

## 3.3.0 Tuya API Log Restructuring and Variable Reconstruction

Before data integrity checks and physics-based validation can be applied, the raw energy logs  retrieved  from  the  Tuya  Cloud  API  must  first  be  restructured  and  normalized.  Unlike  the modeling-ready  smart-plug  dataset  described  in  later  stages,  the  Tuya  export  is  recorded  in  a long-format  key-value  structure,  where  each  timestamped  record  contains  only  a  single  device property  and  its  corresponding value. This subsection describes the preprocessing steps used to convert the raw Tuya logs into a horizontal, time-indexed dataset and subsequently reconstruct the electrical variables required for analysis.

## 0. Daily Energy Log Consolidation

Before  the  restructuring,  scaling, and validation stages (Stages A-E) can be applied, the raw Tuya energy logs must first be consolidated. During data acquisition, the energy logger exports one  CSV file  per  day,  each  containing  all  data  points  recorded  within  that  calendar  date.  Since subsequent  preprocessing  steps  assume  a  continuous  time-series  input,  these  daily  logs  are merged into a single master dataset ordered from the earliest monitored date (20260103) to the most recent available file.

All daily CSV files are first collected from the monitoring directory. Each filename contains an 8-digit date stamp in the format: YYYYMMDD

This date stamp is extracted from each filename and used as the sorting key. The files are then ordered chronologically. This ordering guarantees that earlier days are appended before later days, preserving the natural temporal sequence of logging.

Once  ordered,  the  daily  datasets  are  merged  through  row-wise  concatenation.  At  this stage, the dataset remains in its original Tuya long-format structure, where each row represents a single (timestamp, device, property) observation. No reshaping, scaling, or validation is performed yet; this step ensures only that all datapoints across the monitoring period are contained in a single table.

After  concatenation,  all  records  are  sorted  globally  by  timestamp  in  ascending  order. Because Tuya exports may contain overlapping records at daily boundaries (for example, the same polling instant appearing at the end of one file and the beginning of the next), duplicate entries are screened using the tuple: (timestamp, device, property)

If duplicates are detected, only one instance is retained to prevent double-counting during subsequent pivoting, scaling, and energy computations.

## A. Long-to-Wide Restructuring of Tuya Datapoints

Each Tuya API response records appliance telemetry as multiple rows sharing the same timestamp and device identifier,  but  differing in the reported property. Table X illustrates a typical raw snapshot returned by the API at a single polling instant, where voltage, current, power, energy counters, and control flags are stored as separate records.

Presented in Table 3.1 is an example of a the default retrieved data from TUYA API

| timestamp           | device   | property          |
|---------------------|----------|-------------------|
| 2026-01-03 14:35:47 | Aircon   | switch_1          |
| 2026-01-03 14:35:47 | Aircon   | countdown_1       |
| 2026-01-03 14:35:47 | Aircon   | add_ele           |
| 2026-01-03 14:35:47 | Aircon   | cur_current       |
| 2026-01-03 14:35:47 | Aircon   | cur_power         |
| 2026-01-03 14:35:47 | Aircon   | cur_voltage       |
| 2026-01-03 14:35:47 | Aircon   | voltage_coe       |
| 2026-01-03 14:35:47 | Aircon   | electric_coe      |
| 2026-01-03 14:35:47 | Aircon   | power_coe         |
| 2026-01-03 14:35:47 | Aircon   | electricity_coe   |
| 2026-01-03 14:35:47 | Aircon   | fault             |
| 2026-01-03 14:35:47 | Aircon   | relay_status      |
| 2026-01-03 14:35:47 | Aircon   | overcharge_switch |
| 2026-01-03 14:35:47 | Aircon   | light_mode        |
| 2026-01-03 14:35:47 | Aircon   | child_lock        |
| 2026-01-03 14:35:47 | Aircon   | cycle_time        |
| 2026-01-03 14:35:47 | Aircon   | random_time       |
| 2026-01-03 14:35:47 | Aircon   | switch_inching    |

Although  these  values  are  logged  simultaneously,  they  are  not  directly  usable  for  time-series modeling in their vertical form. Therefore, the first preprocessing operation restructures the dataset into  a  horizontal  format,  producing  one  row  per  timestamp  per  device,  with  each  Tuya  property represented as a column.

This restructuring is performed through an operation defined as follows:

- Index: timestamp, device
- Columns: property
- Values: corresponding Tuya-reported value

After this, all properties associated with the same timestamp are consolidated into a single record.

## B. Selection and Mapping of Energy-Relevant Tuya Datapoints

Once the Tuya log has been restructured into a horizontal format, the next step identifies which of the available Tuya data points correspond to electrical energy measurements required for analysis. Although the horizontal table contains numerous operational and configuration parameters, only a subset directly describes appliance energy behavior.

From  the  full  set  of  Tuya  properties,  the  preprocessing  pipeline  selects  the  following energy-relevant datapoints:

- switch\_1 - device ON/OFF state
- cur\_voltage - instantaneous voltage reading
- cur\_current - instantaneous current reading
- cur\_power - instantaneous active power
- add\_ele - cumulative electrical energy counter

All remaining fields, such as countdown timers, relay flags, child locks, random timers, and calibration  coefficients,  such  as  voltage\_coe,  electric\_coe,  power\_coe,  are  excluded  from  the modeling dataset at this stage. These parameters do not represent physical energy consumption

and are therefore  not  required  for  forecasting  or  cost  estimation. However, their presence in the original wide-format table allows later inspection if device-specific calibration issues arise.

After selection, the Tuya-specific property names are mapped into the study's standardized smart-plug variable naming convention. This ensures consistency across appliances and aligns the dataset with the schema defined in the data collection stage.

The mapping is defined as follows:

- switch\_1 to switch
- cur\_voltage to voltage\_raw
- cur\_current to current\_raw
- cur\_power to power\_raw
- add\_ele to kwh\_raw

At  this  point,  the  values  remain  raw,  meaning  they  retain  the  numeric  representation provided by the Tuya API and have not yet been validated or corrected. The variables are simply renamed  and  isolated  to  create  a  clean  bridge  between  the  device-specific  telemetry  and  the thesis-wide smart-plug schema.

## C. Unit Scaling and Conversion to Engineering Quantities

After  the  relevant  Tuya  datapoints  have  been  isolated  and  mapped  to  the  standardized variable  names,  the  next  step  converts  these  raw  values  into  meaningful  engineering  units. Although  the  variables  are  now  semantically  aligned,  the  Tuya  API  often  reports  electrical measurements  as  scaled  integers  rather  than  direct  physical  quantities.  Therefore,  numerical scaling must be applied before any physics-based validation can be performed.

Each  raw  electrical  variable  is  converted  using  a  predefined  scale  factor  derived  from Tuya's  device  specifications  and  empirically  verified  during  data  inspection.  The  general  scaling relationship applied to all raw measurements is expressed as:

<!-- formula-not-decoded -->

pf =

power\_tu power\_w =

voltage\_u =

voltage\_raw current\_raza

power\_raw kwh\_total =

hwh\_rawu

10

10

1000

100

voltage\_u × current\_a where Xraw is the integer value reported by the device and SX is the corresponding scale factor for that  parameter.  For  the  smart  plug  devices  used  in  this  study,  the  following  conversions  are applied:

- Voltage

where cur\_voltage values such as 2293 are interpreted as 229.3 V.

- Current

where a reported value of 310 corresponds to 0.31 A.

- Power

where a raw value of 708 represents 70.8 W.

- Cumulative Energy

where a reported counter value of 48 corresponds to 0.48 kWh.

## D. Derivation and Initialization of Power Factor

With voltage, current, power, and cumulative energy now expressed in consistent engineering units, the final variable required to complete the smart-plug schema is the power factor (pf). The Tuya API does not consistently provide a direct power factor reading across devices; therefore, power factor is estimated analytically from the scaled electrical measurements.

Power factor is defined as the ratio between real (active) power and apparent power. For each timestamped record, it is computed as:

current\_a =

Dø + sort(Da, timestamp)

current\_a = 0

0.00 ≤ pf ≤ 1.00

Da = {=¡| device\_idi = a}

This computation is applied only under valid load conditions. When the socket is switched OFF (switch = False) or when the measured current is zero, the appliance is assumed to be in a no-load state and the power factor is set to zero:

To maintain physical plausibility, all computed power factor values are constrained within the theoretical bounds:

Any value exceeding unity due to measurement noise or rounding is clipped to 1.00, while negative values are set to 0.00.

## E. Appliance-Specific Dataset Segmentation

After the smart-plug schema has been fully reconstructed (Stages A-D), the resulting dataset still contains readings from multiple appliances in a single table. Because each appliance is modeled independently in later stages, the final step of this subsection divides the dataset into separate appliance-specific files, producing one CSV per monitored load.

Each record already includes the identifier of the source plug through device\_id. Using this identifier, the dataset is partitioned into three subsets corresponding to the three appliances used in the study:

- Air Conditioner dataset: all rows where device\_id = Aircon
- Refrigerator dataset: all rows where device\_id = Refrigerator
- Electric Fan dataset: all rows where device\_id = Electric\_Fan

Formally, for a given appliance a, the extracted dataset is:

where xi represents a complete smart-plug observation row containing: timestamp, device\_id, switch, voltage\_raw, current\_raw, power\_raw, kwh\_raw, voltage\_v, current\_a, power\_w, kwh\_total, pf.

To ensure that the exported files remain usable for the next preprocessing stages, each appliance subset is sorted chronologically:

pf =0 if

This segmentation ensures that each appliance's energy behavior is isolated before data integrity verification (Section 3.3.1), preventing cross-device mixing and allowing appliance-specific validation, correction, and forecasting to be applied consistently across the pipeline.

## 3.3.1 Data Integrity Verification and Standardization

Following data collection, the first stage focuses on verifying the structure and validity of all input data. Before any computation, the raw files are examined to confirm that their columns, data types, and time formats are correct.

## A. Schema Alignment and Unit Validation

Each dataset follows a defined schema. After collection, the smart-plug dataset contains timestamped electrical  readings  that  describe  appliance-level energy behavior, while the weather dataset  provides  environmental  parameters corresponding to each observation period. Both CSV files  must  follow  the  expected  structure  and  declare  consistent  measurement  units.  Each  file  is inspected  to  confirm  the  presence  of  the  required  columns  and proper data types. The declared measurement  units,  such  as  volts,  amperes,  watts,  and  kilowatt-hours  for  the  smart  plug,  and degrees, percentage, and millimeters for the weather data, are checked for consistency across all files.

Both of  the  expected  smart-plug and weather schemas are defined in the data collection stage. For illustration, Table 3.6 presents three  consecutive  10-minute  readings  from  one appliance,  showing  the  structure  of  the  smart-plug  data  used  in  this  stage.  Similarly,  Table  3.8 presents  an  hourly  record  of  weather  variables.  All  timestamps  are  standardized  to  UTC+8, ensuring synchronization between the energy and weather datasets.

## B. Time Standardization and Ordering

Once  the  schema  and  units  have  been  verified,  all  timestamps  are  standardized  to Philippine Standard Time (UTC +8) to ensure temporal consistency across datasets. Each device's data  is  then  sorted  chronologically  so  that  the  sequence  of  readings  reflects  the  actual order in which they were recorded.

For  the  smart-plug  dataset,  the  expected  interval  between  consecutive  readings  is  600 seconds  (10  minutes).  To  confirm  this,  the  time  difference  between  successive  timestamps  is calculated as:

<!-- formula-not-decoded -->

If  the  smart  plug  data's  internal\_seconds  =  600,  the  data  sequence  is  considered continuous.  Any  deviation  from  this  expected  interval  is  flagged  for  review  and  correction in the next  preprocessing  stage.  Similarly,  for  the  weather  dataset  (Table  3.8),  the  time  difference between  successive  records  is  computed  using  the  same  Equation  (a).  If  the  weather  data's internal\_seconds weather  = 3600, the weather data is confirmed to be recorded at consistent one-hour intervals. In the sample smart-plug values from Table 3.6, all three records are exactly ten minutes apart, confirming that the data were captured continuously.

## C. Physics Consistency and Scaling Verification

At this stage, numerical validation begins to ensure that all recorded values reflect realistic electrical behavior and  that  any  integer-scaled  'raw'  readings  are  correctly  converted  into engineering  units.  This  verification  is  applied  to  all  readings  and  follows  a  physics-guided procedure, from recomputing voltage, current, power, and cumulative energy from their raw values, comparing  the  recomputed  and  scaled  values  to  detect  incorrect  scaling,  to  adjusting  scaling factors per appliance if consistent mismatches are found, then re-run all dependent computations. The general scaling relation is applied depending on the scale factor assigned to each parameter based on TUYA's specifications. For the sample dataset in Table 3.6, the readings are already in scaled  engineering  units.  However,  this  verification  step  is  still  performed  to  ensure consistency across  different  devices.  In  this  case,  if  the  raw  and  scaled  values  match  exactly, it requires no further conversion.

## C.1 Recomputation of Power

With  scaled  voltage  (V)  and  current (I) available, power is re-derived from the measured voltage, current, and estimated power factor (pf), calculated as:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

If the deviation, solved using the percentage deviation formula below,

<!-- formula-not-decoded -->

between the computed power and the device-recorded power is within ±5 %, the recorded value is accepted.  Otherwise,  computed power replaces it.  This  ensures  that  all  power  readings  remain physically consistent. As an example, for the 08:00 AM reading (Table 3.6).

<!-- formula-not-decoded -->

Although slightly  above  the  5%  threshold, this difference is acceptable for demonstration purposes.  In  the  actual  preprocessing  pipeline,  however,  such  a  case  would  trigger  automatic re-evaluation of scaling parameters.

## C.2 Recomputation of Cumulative Energy

After  interval  energies  are  computed  in  the  next  stage,  the  cumulative  total  energy  is verified using the formula below:

<!-- formula-not-decoded -->

The  recomputed  cumulative  values  are  then  compared  with  the  plug's  recorded  kWh readings to confirm that no scaling errors occurred during logging. Using the data from Table 3.6,

<!-- formula-not-decoded -->

Then the interval energy between 08:00 and 08:10 is

<!-- formula-not-decoded -->

Using a similar equation, between 08:10 and 08:20, the ∆𝐸 08:20-0:10 = 0. 012 𝑘𝑊ℎ

The cumulative total is then verified as

<!-- formula-not-decoded -->

.

These ranges act as checks to ensure that the smart plugs are correctly capturing data that  aligns  with  typical household conditions and usage. If any recorded values fall outside these

ranges, it might signal a problem, and those values will be flagged for further review and potential correction through physics-based recomputation.

## C.5 Power Factor Consistency Check

Finally, the measured power factor is recalculated to verify its alignment with the estimated power factor. This is calculated below:

<!-- formula-not-decoded -->

Using the values for the 08:00AM record from Table 3.6,

Since the recomputed matches the plug's recorded value (0.048 kWh), the cumulative

𝐸

𝑡3

energy is confirmed consistent, indicating no scaling or accumulation errors during logging.

## C.3 Comparison and Tolerance Rule

To maintain accuracy, is compared against both the device-recorded and, 𝑃 𝑐𝑎𝑙𝑐 𝑃 𝑟𝑒𝑐𝑜𝑟𝑑𝑒𝑑 if available, scaled . 𝑃 𝑟𝑎𝑤,𝑠𝑐𝑎𝑙𝑒𝑑

If  the  median  absolute  percentage  deviation  over  a  calibration  window  exceeds  5  %, scaling  factors  are  corrected  per  appliance  and all dependent fields are recomputed, then re-run

the

. Otherwise, the recorded values are retained.

∆𝑘𝑊ℎ

## C.4 Validation Ranges and Plausibility Screening

All variables are screened against expected household operating ranges, in accordance to

International Electrotechnical Commission, to ensure physical plausibility:

- Voltage: 220 - 240 V
- Current: &gt; 0 A and typically &lt; 15 A (when switch\_1 = True)
- Power: &gt; 0 W and typically &lt; 3000 W (when switch\_1 = True)
- ●
- Power factor: 0.85 - 1.00

<!-- formula-not-decoded -->

The  recalculated  power  factor  falls  within  the  expected  range  (0.85  -  1.00).  Persistent divergence  between and triggers  recalibration  of and  a  re-evaluation  of  the 𝑝𝑓 𝑐𝑎𝑙𝑐 𝑝𝑓 𝑃 𝑐𝑎𝑙𝑐 tolerance rule. The  raw  energy  data  (kWh\_raw)  is  is  kept alongside the scaled data ( to  maintain  transparency  and  enable  auditing.  The  recorded  cumulative  energy 𝑘𝑊ℎ 𝑟𝑎𝑤,𝑠𝑐𝑎𝑙𝑒𝑑 ) used over time is stored as kwh\_total.

## 3.3.2 Data Cleaning and Energy Derivation

The next stage computes the energy consumed per interval. This involves deriving energy values from the cumulative energy counter, applying fallback calculations for incomplete readings, and validating  each  interval  with  a  hybrid  decision  rule.  Additional  procedures handle temporary gaps, resets, and outliers to maintain consistent energy profiles across the monitoring period.

## A. Interval Energy Computation

The  Tuya  smart  plug  records  the  total  cumulative  energy  as  kWh\_total.  To  obtain  the actual energy consumed  in each 10-minute interval, the  difference  between  consecutive cumulative readings is computed. The formula is expressed:

<!-- formula-not-decoded -->

Using the values from 08:00 AM to 08:10 AM from Table 3.6

<!-- formula-not-decoded -->

So,  the  interval  energy  values  are  calculated  as 0.011 kWh, and the same is applied for further  intervals.  If  the  cumulative  meter  temporarily  freezes,  resets,  or  a  record  is  missing,  the system computes a fallback energy estimate using the average power and elapsed time between

the  two  readings,  using  the  Equation  3.8  for  calculating the average power and Equation 3.9 for calculating the energy\_fallback.

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

After both values are calculated, a hybrid selection rule determines which value is retained as  the  validated  interval  energy.  The  final  energy  for  each  interval  (energy\_final)  is  determined based on the following conditions:

1. If both interval energy  (energy\_interval) and  fallback energy  (energy\_fallback) are available:
- The  final  energy  will  be  the  interval  energy  (energy\_interval),  provided  that  the absolute difference between the two is less than or equal to 10%.
2. If  the  cumulative  reading  is  missing,  negative,  or  inconsistent,  the  final  energy  will  be based on the fallback energy (energy\_fallback).
3. If  the  switch  is  OFF  (switch  =  False),  the  final  energy  will  be  0,  regardless  of  the other conditions.

Where:

- is  the  direct  energy  difference  from  the  cumulative  meter  (preferred  when 𝐸 𝑖𝑛𝑡𝑒𝑟𝑣𝑎𝑙 consistent)
- is the physics-based estimate using average power and time 𝐸 𝑓𝑎𝑙𝑙𝑏𝑎𝑐𝑘
- is the validated hybrid energy for downstream calculations 𝐸 𝑓𝑖𝑛𝑎𝑙

To demonstrate this process, the same readings from Table 3.6 are used for illustration.

Table 3.16 Interval Energy Derivation Using Cumulative and Fallback Methods

| Timestamp        |   Voltage (V) |   Current (A) |   Power (W) |   kWh Total |   Interval (kWh) |   Δ Fallback (kWh) |   Final (kWh) |
|------------------|---------------|---------------|-------------|-------------|------------------|--------------------|---------------|
| 2025-10-17 08:00 |         228.5 |          0.31 |        70.8 |       0.024 |                  |                    |               |
| 2025-10-17 08:10 |         229   |          0.32 |        71.5 |       0.035 |            0.011 |             0.0118 |         0.011 |
| 2025-10-17 08:20 |         230.2 |          0.33 |        72   |       0.046 |            0.011 |             0.012  |         0.011 |

The  difference  between  ΔkWh  and  fallback  is  approximately  7%,  which  is  within  the acceptable  range  (≤10%),  so  the  cumulative  difference  value  is  retained.  This  same  validation process is applied to all intervals within the dataset to ensure consistent energy values.

## B. Handling Gaps, Resets, and Outliers

If  any  interruptions  or  anomalies  occur,  In  practical  data  collection,  each  situation  is handled through a defined rule to preserve both physical accuracy and temporal continuity.

## 1. Minor gaps (≤ 20 minutes).

When a single 10-minute reading is missing but the neighboring records are available, the voltage,  current,  and  power  values  are  estimated  using  linear  interpolation  between  the  two surrounding points, shown in Equation 9.

<!-- formula-not-decoded -->

For example, if voltage readings are available at 08:00 and 08:20 but missing at 08:10, the interpolated value is computed as:

<!-- formula-not-decoded -->

The  same  procedure  applies  to  current  and  power,  using  Equation  (j),  where  n  is  the number of sub-intervals  between timestamps. These interpolated values are used for diagnostics

and  continuity  validation,  not  for  generating  new  energy  values.  If  the  missing  interval  affects energy computation, a fallback  estimate  is  recalculated  using  interpolated  power (Equation 3.9), and the hybrid validation rule finalizes the interval energy.

## 2. Long gaps (&gt; 20 minutes).

If an appliance goes offline for an extended period, interpolation is avoided, and the energy for  those  intervals  is  recorded  as  0  kWh  to  maintain  chronological  structure  without  distorting cumulative totals.

## 3. Cumulative resets.

If the cumulative energy counter (kwh\_total) decreases, often due to a restart, the affected interval's ΔkWh becomes invalid. In this case, the interval energy is set to 0, and a fallback energy is recomputed using Equation (3.9). The hybrid rule then selects the valid final value.

## 4. Outliers or spikes.

Occasionally,  the plug may register implausible readings. In such cases, voltage, current, and power readings are replaced with the nearest-neighbor rolling mean, using the formula below:

<!-- formula-not-decoded -->

As an example, assume a power reading at 08:10 AM is flagged as implausible. Using the data in Table 3.6, the neighboring valid reading is at 08:00 AM and 08:20 AM.

<!-- formula-not-decoded -->

The  flagged  value  is  replaced  with  71  W  and  a  new  fallback  energy  is  derived  and validated using the hybrid rule.

## C Daily Consistency Check

After all intervals are validated, a final check ensures the total daily energy aligns with the cumulative progression of the smart plug's meter. The sum of all validated interval energies should match the net change in the cumulative reading between the first and last records of the day. The total energy for the day can be approximated using the formula:

<!-- formula-not-decoded -->

The deviation is expressed as:

<!-- formula-not-decoded -->

If the deviation exceeds  5%,  the  affected  intervals are flagged  and  automatically reprocessed through the hybrid validation  rule until consistency is achieved. Using the data from Table 3.16,

<!-- formula-not-decoded -->

Since the  deviation is 0%, which is within the acceptable range (5%), no further action is needed.  At  the  end  of  this  stage,  each  10-minute  record  contains  a  verified,  physics-consistent measure of energy consumption. All corrections are logged for traceability with tags, ensuring full transparency of this pipeline.

## D. Visual Inspection and Time-Series Diagnostics

As a final validation step, diagnostic time-series plots are generated for each appliance to verify  that  sensor  readings  exhibit  consistent  behavior.  The  following  plots  are  created  for  each appliance:

- Power (W) vs. Time: Observes ON/OFF patterns and daily usage cycles.
- Voltage  (V)  and  Current  (A)  vs.  Time:  Ensures  voltage  stays  within  the  expected  range (220-240 V) and current changes align with power

- Cumulative  Energy  (kWh\_total)  vs.  Time:  Confirms  the  cumulative  energy  increases monotonically, indicating valid metering without resets or gaps.

These plots allow for quick identification of scaling errors, device resets, or extended idle periods.  They provide a final check to ensure that the data is physically plausible and structurally complete before modeling.

## 3.3.3 Data Aggregation and Feature Construction

After  validating  and  cleaning the interval-level energy values, the data is aggregated into hourly  records  and  enriched  with  exogenous  features.  This  ensures  alignment  of  variables on a consistent time scale.

## A. Hourly Resampling

Each smart plug records readings every 10 minutes. To create hourly energy totals, the six validated 10-minute intervals within the hour are summed using the formula below:

<!-- formula-not-decoded -->

This produces the total energy consumed during each one-hour period. After aggregation, a  reconciliation  step  compares  the  aggregated  total  to  the  cumulative  (kWh\_total)  for  the  same hour. If the deviation exceeds 5%, affected intervals are reprocessed  using  the  hybrid recomputation  rule  to  ensure  alignment.  Using  the  same  values  in  Table  3.16  (assuming  they represent 1 hour),

<!-- formula-not-decoded -->

The deviation would be:

<!-- formula-not-decoded -->

This gives the total energy consumed during the 1-hour period.

## B. Validation of Weather Data

Weather  inputs  from  the  OpenWeatherMap  API  validation  procedure.  This  multi-stage process prioritizes intrinsic data checks before external comparisons, ensuring that only physically and temporally consistent weather data are used.

## 1. Range validation (physical plausibility).

All weather variables are checked to ensure they fall within realistic physical limits. Values outside these boundaries are removed and handled using interpolation below:

<!-- formula-not-decoded -->

- Temperature: -10°C &lt; T &lt; 45°C
- Humidity: 0 &lt; Humidity ≤ 100%
- Rainfall: rainfall ≥0

For example, if temperatures at 08:00 AM and 10:00 AM are 32.4°C and 32°C,

The temperature at 09:00 AM could be interpolated as:

## 2. Temporal consistency check.

Excessive hour-to-hour changes in weather data are flagged, as they often indicate sensor errors or glitches. The following thresholds are applied:

- | ΔT | &gt; 5°C per hour
- | Δhumidity | &gt; 20% per hour

Values exceeding these thresholds are corrected using the nearest valid measurements. The erroneous value is typically replaced with a linearly interpolated value based on nearby valid readings  (Equation  o).  This  can  also  be  illustrated  using  the  interpolation  method  applied in the previous computation.

## 3. Cross-source comparison.

If  anomalies  persist  after internal validation, data are cross-checked with an independent reference. Discrepancies beyond thresholds trigger manual inspection and correction. This ensures the weather data is both physically plausible and externally verified when needed.

<!-- formula-not-decoded -->

## C. Derived Time and Historical Features

To  improve  the  predictive  capability  of  the  model,  additional  features  are  derived  from timestamps and energy data, capturing cyclical time patterns and autocorrelation.

## 1. Calendar and time-based features.

These  features  help  identify  patterns  like  peak-hour  usage,  weekend  consumption,  and holiday usage. From each hourly timestamp, the following time indicators are extracted:

- hour of day = t mod 24
- day of week = t mod 7
- is\_weekend = 1 if day of week ∈ {6, 7}, else 0
- Is\_holiday = 1 if the date corresponds to an official Philippine holiday, else 0

## 2. Historical (Lagged) features.

Lagged energy variables are created to capture autocorrelation across time:

- Lag24  = E t-24h
- Lag168  = E t-168h

For  example,  lag\_24  represents  energy  consumption  at  the  same  hour  on  the  previous day, and lag\_168 captures energy consumption from the same hour a week earlier.

## 3. Rolling (moving average) features.

To  smooth  fluctuations  and  highlight  recent  trends,  rolling  averages  are  computed  over 24-hour (Equation p) and 168-hour (Equation q) windows:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

These  averages  help  capture  trends  like  gradual  changes  in  energy  demand  due  to temperature or behavior. For example,

<!-- formula-not-decoded -->

This  procedure  aggregates  the data over the past 24 hours for the 24-hour rolling mean, and over the past 168 hours for the 168-hour rolling  mean.  Since the SARIMAX model handles seasonality,  trigonometric  encodings  are  not  required.  Starting  from  two  months  of  10-minute smart-plug readings (144 points per day), the data for each appliance were aggregated into hourly totals, yielding 1,440 hourly observations per appliance for the real monitoring period.

## 3.3.4 Final Data Transformation

The final stage consolidates all processed variables into a single, modeling-ready dataset. This integrates hourly energy consumption with environmental and temporal attributes, forming the complete input for forecasting and cost estimation.

## A. Weather Synchronization

Since the smart plug data has already been aggregated into validated hourly energy totals and  the  weather  data  is  collected  at  an  hourly  frequency,  these  two  time-series  inputs  must  be synchronized  before  final  modeling.  Only  these  variables  require  synchronization,  because  they share a temporal structure  and  must refer to the same hour for the SARIMAX model to correctly associate consumption with environmental conditions.

The smart plug readings, originally  captured  at  10-minute  intervals,  are  first  aggregated into  hourly  kWh.  Weather  data  from  the  OpenWeatherMap  API  is  already  provided  at an hourly resolution.  Once  both  datasets  have  been  validated,  each  hourly  energy  value  is paired with its corresponding temperature, humidity, and rainfall measurements. Synchronization is performed by aligning  both  datasets  through  a  timestamp-based  merge,  ensuring  that  every  hour  contains  a complete and accurately matched set of energy and weather attributes.

For  clarification,  tariff  data  and  appliance  metadata  are  not  part  of  the  synchronization process. Tariff values are incorporated only after forecasting during the cost-estimation phase, and therefore do not require temporal alignment with the model inputs. Likewise, appliance metadata is static  descriptive  information  used  for  labeling,  analysis, and dashboard visualization. Because it does not vary over time, it is not included in the time-series synchronization step.

This synchronization stage results in a unified hourly dataset.  For  example,  the synchronized hourly record for 08:00-09:00 is:

Table 3.17 Hourly Aggregated Energy with Corresponding Weather Variables

| Timestamp        |   Total Energy |   Temperature |   Humidity |   Rainfall |
|------------------|----------------|---------------|------------|------------|
| 2025-10-17 08:00 |          0.022 |          32.4 |        6.7 |          0 |

## B. Final Variable Structure for Modeling

The compiled dataset includes the validated hourly appliance-level energy  target, synchronized weather features, and derived temporal and historical predictors. The final variable structure for modeling is summarized below:

| Variable        | Type     | Description                                        |
|-----------------|----------|----------------------------------------------------|
| timestamp       | datetime | Hour start (UTC+8)                                 |
| kWh             | float    | Validated hourly energy target                     |
| temperature     | float    | Ambient air temperature (°C)                       |
| humidity        | float    | Relative humidity (%)                              |
| rainfall        | float    | Precipitation per hour (mm)                        |
| hour_of_day     | int      | Hour of the day (0-23)                             |
| day_of_week     | int      | Day of the week (1-7)                              |
| is_weekend      | binary   | 0 = weekday, 1 = weekend                           |
| is_holiday      | binary   | 0 = not holiday, 1 = holiday                       |
| lag_24          | float    | kWh recorded at the same hour of the previous day  |
| lag_168         | float    | kWh recorded at the same hour of the previous week |
| rolling_mean_24 | float    | Average kWh over the preceding 24 hours            |

Table 3.18 Final Variable Structure of the Modeling-Ready Dataset for Energy Forecasting

| rolling_mean_168   | float   | Average kWh over the preceding 168 hours (7 days)   |
|--------------------|---------|-----------------------------------------------------|

Each  variable  describes  energy  usage  behavior  over  time,  environmental  changes,  and historical  trends.  Meanwhile,  the  timestamp  serves  as  the  temporal  index,  defining  the  hourly frequency used by the SARIMAX model. It is not included as a regressor since its information is encoded in the temporal features and the model's inherent time structure. All variables retain their original  units  to  preserve  interpretability.  Since  the  SARIMAX  model  operates  effectively  on  raw data, no normalization or standardization is required. At the end of this stage, the pipeline outputs three (3) preprocessed real datasets, one for each monitored appliance.

## 3.4 Synthetic Data Generation Using TimeGAN

This  section  describes  how  the  study  reconstructs  a  complete 14-month, high-resolution household  electricity  dataset  using  a  generative  deep-learning  model.  This  process  is  essential because  only  two  months  of  appliance-level  smart  plug  measurements  are  available  from  the actual monitoring period, which is insufficient to support seasonal analysis, pattern extraction, and forecasting model training.

To  address this limitation, the study employs an Improved TimeGAN model based on the architecture  presented  by  Tang  et  al.  (2025).  TimeGAN  (Time-series  Generative  Adversarial Network) is  specifically designed to learn temporal relationships within multivariate sequences. In this  study,  the  Improved  TimeGAN  serves  as  a  data reconstruction engine rather than a generic augmentation tool.

## 3.4.1 Preprocessing for Training the Improved TimeGAN+

Before  the  Improved  TimeGAN model can learn appliance-level electricity  patterns  from the smart-plug data, the preprocessed 10-minute power readings (from Section 3.3.2) must first be transformed into clean, normalized, and temporally consistent sequences.

## A. Outlier Removal

The  first  step  ensures  that  all  input  values  reflect  realistic  appliance-level  electricity behavior. Although the readings have already passed the initial preprocessing pipeline, the dataset must  undergo  an  additional  layer  of  outlier  removal  tailored  specifically  for  GAN  training.  The following criteria are applied:

## 1. Physical Consistency Screening

Each 10-minute record is checked against expected residential appliance operating limits:

- Voltage: 220-240 V

- Current: &gt; 0 A and typically &lt; 15 A

- Power: &gt; 0 W and typically &lt; 3000 W

- ●

- Power factor: 0.85-1.00

Any  reading  that  violates  these  bounds  is  removed.  Table  3.19  shows  a  sample  of  a detected physical outlier.

Table 3.19 Smart Plug Physical Outlier Data

| Timestamp           | Power_w   |
|---------------------|-----------|
| 2025-10-17 14:50:00 | 4020W     |

This  reading exceeds the appliance's rated wattage and violates the established physical tolerance  rules;  it  is  not  plausible  for any device connected to a 16A smart plug and is therefore discarded.

## 2. Sudden Spike Detection

Even  if  a  value  is  within  physical  limits,  abrupt  unrealistic  jumps  are  removed,  where  a threshold  τ  is  computed  from  historical  variance.  Readings  with  unrealistic  jumps  are  removed using:

<!-- formula-not-decoded -->

For example, consider the following preprocessed power values, in Table 3.20:

Table 3.20  Sample of Preprocessed Power Values

| Timestamp        |   Power (W) |
|------------------|-------------|
| 2025-10-17 08:00 |        70.8 |
| 2025-10-17 08:10 |        71.5 |
| 2025-10-17 08:20 |        72   |
| 2025-10-17 08:30 |       185   |

For the monitored appliance, the expected change between consecutive intervals typically falls within 0.5 to 1.2 W, but the actual jump from 08:20 to 08:30, when evaluated using Equation 3.18,

exceeds the allowable threshold τ.  Therefore,  the  185 W reading is identified as a spike and removed from the dataset.

## 3. Missing or Frozen Readings

Although TimeGAN uses only the 10-minute power values as training input, the cumulative energy  counter  (kWh\_total)  is  used  during  preprocessing  as  a  consistency  indicator.  Because kWh\_total must increase whenever an appliance is ON, any frozen or non-monotonic values signal a  faulty  interval.  In  such  cases,  interpolation  is  applied. Below, shown in Table 3.21, it illustrates examples of a frozen reading.

Table 3.21 Sample of Frozen Reading Records

| Timestamp   | Power_w   |   kWh_total |
|-------------|-----------|-------------|
| 10:00       | 70W       |       0.152 |
| 10:10       | 71W       |       0.152 |
| 10:20       | 73W       |       0.161 |

Since kWh\_total must always increase when the appliance is ON, 10:10 cannot remain equal to 10:00. This will be fixed   using linear interpolation between the valid values at 10:00 and 10:20. For example,

From 10:00 to 10:20, the total change is:

<!-- formula-not-decoded -->

The number of 10-minute steps inside this interval:

- 10:00 - 10:10
- 10:10 - 10:20

So there are 2 segments, each segment increment is:

<!-- formula-not-decoded -->

Next, starting from 10:00 (0.152):

<!-- formula-not-decoded -->

Thus, the corrected value at 10:10 becomes: 0.1565 kWh

The original  frozen  value  of  0.152  kWh  is replaced with the interpolated value of 0.1565 kWh, thereby restoring the expected monotonic progression of the cumulative energy counter. After fixing this inconsistency, power\_w will be recomputed. For example,

If the corrected kWh\_total at 10:10 becomes: 0.1565 Then:

Using the kWh difference computer earlier:

<!-- formula-not-decoded -->

Thus, the recomputed power\_w  at 10:10 becomes  approximately  consistent  with neighboring interval values, replacing the unreliable value produced by the frozen counter.

## B. Min-Max Normalization

Before  TimeGAN training, each 10-minute power reading must be scaled into the range [0,1] using Min-Max Normalization:

Where:

- x = original power value

<!-- formula-not-decoded -->

ror ru.o:

Inorm =

For 71.5W:

Enorm =

For 72.0W

Enom =

70.8 - 12

810 - 12

=

71.5 - 12

798

798

58.8

798

s 0.0736

- xmin = minimum power recorded in the two months
- xmax = maximum power recorded in the two months

60.0

For demonstration, consider the following preprocessed 10-minute power values from one appliance: =

Table 3.22 Sample of Preprocessed Power Values

| Timestamp        |   Preprocessed Power (W) |
|------------------|--------------------------|
| 2025-10-17 08:00 |                     70.8 |
| 2025-10-17 08:10 |                     71.5 |
| 2025-10-17 08:20 |                     72   |

Assume that across the full two-month monitoring period, this appliance has:

- Minimum recorded power: xmin = 12W
- Maximum recorded power: xmax = 810W

<!-- formula-not-decoded -->

All  144  values  of  each  day  are  transformed  using  the  same  Min-Max  parameters (xmin,xmax).  This  normalization  step  ensures  that  the  Improved  TimeGAN  learns  the  relative shape and temporal progression of daily appliance usage  rather  than  absolute  wattage magnitudes.  Absolute  values  are  restored  later  during  the  monthly  scaling  procedure  using  the

participating household's Meralco billing data. The table 3.23 illustrates the min-max normalization of the 10-minute power readings.

Table 3.23 Sample Min-Max Normalization of 10-Minute Power Readings

| Timestamp        |   Preprocessed Power (W) |   Normalized Value |
|------------------|--------------------------|--------------------|
| 2025-10-17 08:00 |                     70.8 |             0.0736 |
| 2025-10-17 08:10 |                     71.5 |             0.0746 |
| 2025-10-17 08:20 |                     72   |             0.0752 |

## C. Daily Segmentation

Once  all power  readings  are  normalized,  the  continuous  10-minute  time  series  is segmented into daily windows, each representing one complete 24-hour cycle. For example:

```
Given a 10-minute interval: Let the normalized sequence be: where T is the total number of normalized 10-minute points in the two-month dataset. For each day d, we extract a window of 144 values: Thus, with  approximately  60 days of real monitoring, N = 60 daily sequences are obtained per
```

monitored appliance

Each sequence becomes one training sample for the Improved TimeGAN. The objective of this  study  is  full-day  appliance-level  consumption  reconstruction.  Therefore,  each  sequence encodes morning ramp-up, mid-day stable periods, evening peaks, and night decline. This ensures the Improved TimeGAN learns the full temporal structure of daily load behavior.

| Timestamp        |   Normalized Power |
|------------------|--------------------|
| 2025-10-17 00:00 |               0.12 |

Table 3.24 Example of a Daily Training Sequence

| 2025-10-17 00:10   | 0.1030   |
|--------------------|----------|
| 2025-10-17 00:20   | 0.0995   |
| …                  | …        |
| 2025-10-17 08:00   | 0.0736   |
| 2025-10-17 08:10   | 0.0746   |
| 2025-10-17 08:20   | 0.0752   |
| …                  | …        |
| 2025-10-17 23:50   | 0.2000   |

Shown in Table 3.24 is an example of a normalized daily training sequence derived from the smart-plug dataset. This table illustrates how all 10-minute normalized power readings for one full  day  are  grouped  into  a  single  TimeGAN  training  example.  Each row represents a 10-minute interval within a 24-hour period, resulting in 144 normalized values per day per appliance.

At  this  point,  the  Improved  TimeGAN  receives  a  clean,  normalized,  and  temporally complete set of  approximately  sixty  (60)  daily  sequences per monitored appliance. Each sample contains 144 time steps, corresponding to one full day of appliance-level electricity consumption.

## 3.4.2 Improved TimeGAN Architecture

The generative model used in this study is based on the Improved TimeGAN architecture proposed by Tang et al. (2025). Its structure, shown in Figure 3.3, combines adversarial learning and  supervised  temporal  modeling  to  generate  synthetic  time-series  data  that  preserve  both statistical similarity and sequential dynamics of real household daily load curves.

Reconstructions

Recovery

Latent Codes

Embedding

Real Sequences

Classifications

Discriminate

Supervised

Figure 3.3 The structure of the TimeGAN model

<!-- image -->

The overall structure (Figure 3.3) integrates five interacting neural  modules-the Embedding,  Recovery,  Generator,  Discriminator,  and  Supervisor  networks.  These  components operate  on  shared  latent  representations called latent codes, enabling the model to capture both the  shape  of  daily  electricity  consumption  profiles  and  the  temporal transitions between different periods of the day.

## Forward Pass Overview

- Encoding Real SequencesEach normalized daily sequence (144 time steps) is first passed through  an  LSTM-based  Embedding  Network  (E),  which  converts  the  real  data  into  a compact latent representation.
- Reconstruction

The latent code is then passed to the Recovery Network (R), which attempts to reconstruct the  original  sequence.  The  difference  between  the  real  and  reconstructed  sequences produces  the  reconstruction  loss,  which  teaches  the  encoder-decoder  pair  to  preserve temporal structure.

- ●
- Generation of Synthetic Latent Codes

The Generator (G) receives random noise and produces synthetic latent codes designed to mimic the structure of real latent sequences.

- Adversarial Classification

Unsupervised

Loss

The Discriminator (D) attempts to distinguish real latent codes (from E) from synthetic ones (from  G).This  forms  the  unsupervised adversarial loss, encouraging synthetic sequences to resemble real ones.

## ● Temporal Supervision:

The  Supervisor  (S)  predicts  the  next  latent  step  in  a  sequence.  This  produces  the supervised  temporal  loss,  ensuring  that  TimeGAN  learns  realistic  day-to-day  transitions and long-range temporal dependencies.

With these, the Improved TimeGAN learns both:

- statistical similarity of real household consumption
- temporal continuity across the 144 points of each daily curve

## A. Components of the Improved TimeGAN

The  Improved  TimeGAN  retains  the  five  core  modules  but  enhances  the  Recovery Network by integrating Multi-Head Self-Attention, as shown in Table 3.25.

Table 3.25 Components of the Improved TimeGAN

| Component         | Description                                                                                         |
|-------------------|-----------------------------------------------------------------------------------------------------|
| Embedding (E)     | Converts real sequences into latent space using LSTM layers                                         |
| Recovery (R)      | Reconstructs time-series from latent codes using GRU layers enhanced with Multi-Head Self-Attention |
| Generator (G)     | Produces synthetic latent codes from random noise using GRU layers                                  |
| Discriminator (D) | Classifies real vs. generated latent codes using GRU layers                                         |
| Supervisor (S)    | Predicts latent transitions to enforce temporal continuity                                          |

## B. Multi-Head Self-Attention in the Recovery Module

An  improvement  introduced  by  Tang  et  al.  (2025),  and  retained  in  this  study,  is  the integration of the Multi-Head  Self-Attention  (MHSA)  layer  within  the  Recovery  module.  As

Reconstructions

Attention(Q, K, V) = softmax

MultiHlead(Q, K, V) = Concat(head1,..., heads) WO

Linear illustrated in Figure 3.4, this mechanism allows the network to assign varying attention weights to different time steps when reconstructing each point in the sequence.

Scaled Dot-Product Attention

Linear

Linear

Gate Recurrent Unit

Gate Recurrent Unit hs, hir

Figure 3.4 The Structure of the Improved Recovery Module

<!-- image -->

Mathematically, single-head attention is computed as:

For multi-head attention:

QKT

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

This attention layer strengthens  the  model's  ability  to  capture  long-range  temporal patterns, periodic household  behaviors,  and  subtle  correlations  across  different  time-of-day segments. This is especially important for reconstructing 144-point daily curves, where dependencies may span many hours.

Is=E

LA=E

113-1133+s8-ed

## C. Loss Functions

Training the Improved TimeGAN involves three loss functions operating simultaneously:

## 1. Reconstruction Loss

Ensures the recovered sequence matches the original normalized day:

<!-- formula-not-decoded -->

## 2. Unsupervised Adversarial Loss

Encourages synthetic sequences to resemble real ones:

## 3. Supervised Temporal Loss

Forces the Generator to match real temporal transitions:

<!-- formula-not-decoded -->

These losses teach the model to generate sequences that are (1) statistically similar, (2) temporally smooth, realistic, and structurally consistent with real household electricity data.

## D. Training Hyperparameters

The  training  hyperparameters  adopted  in  this  study  are  based  on  the  configuration proposed by Tang et al. (2025), with adjustments to accommodate the smaller residential dataset composed  of  approximately  60  normalized  daily  sequences.  Table  3.26  summarizes  the  final hyperparameter settings to be used for training the Improved TimeGAN model.

| Parameter       | Value   |
|-----------------|---------|
| RNN units       | 64      |
| Attention heads | 4       |
| Learning rate   | 3x10 -5 |

<!-- formula-not-decoded -->

Table 3.26 Training Hyperparameters

| Batch size   |   128 |
|--------------|-------|
| Epochs       |   800 |

As shown in Table 3.26, the selected hyperparameters provide a balance between training stability and model expressiveness. The Improved TimeGAN uses 64 RNN units and four attention heads, with a learning rate of 3×10 -5 to ensure stable convergence during training. The batch size was reduced from 256, as used in Tang et al. (2025), to 128 to better accommodate the smaller scale  of  the  residential  dataset  while preventing overfitting. The model is trained for 800 epochs, which is sufficient to capture complex daily electricity patterns without introducing instability.

## 3.4.3 Generating Synthetic Days

After the Improved TimeGAN has been fully trained on the 60 normalized daily sequences obtained  from  the  two  months  of  real  smart-plug  monitoring  per  monitored  appliance,  the  next stage is to use the trained model to generate the missing daily profiles for the remaining months of the historical period. The goal is to construct a complete 14-month dataset at 10-minute resolution, even though only two months contain real appliance-level measurements.

Since the dataset must span 14 total months, and only 2 months are real:

14 𝑚𝑜𝑛𝑡ℎ𝑠  -  2 𝑚𝑜𝑛𝑡ℎ𝑠  =  12 𝑠𝑦𝑛𝑡ℎ𝑒𝑡𝑖𝑐 𝑚𝑜𝑛𝑡ℎ𝑠

Given  that  each  month  contains  28-31  days,  the  Improved  TimeGAN  must  generate approximately: depending  on 12 × (30 ± 2) ≈ 360 - 370 𝑠𝑦𝑛𝑡ℎ𝑒𝑡𝑖𝑐 𝑑𝑎𝑖𝑙𝑦 𝑝𝑟𝑜𝑓𝑖𝑙𝑒𝑠 the number of days per month.

Each synthetic day is a sequence of 144 normalized points, corresponding to 24 hours × 6 samples per hour (10-minute intervals).

TimeGAN generates these sequences by sampling from a learned latent distribution. For each missing day, the Generator receives a combination of (a) random latent noise and (b) optional

conditioning  information  that  guides  generation  toward  realistic  seasonal  patterns.  Improved TimeGAN produces one synthetic daily load curve through the following steps:

## 1. Sample Latent Noise Vector (z)

A latent noise vector is drawn from a multivariate distribution:

<!-- formula-not-decoded -->

This noise  introduces  natural  day-to-day  variability,  preventing  repeated  or  identical synthetic days.

## 2. Create a Condition Vector (c)

The model supports optional conditioning information, which can encode:

- weekday vs. weekend
- approximate month or season
- coarse-level appliance-level load tendency

This helps the GAN generate day-profiles appropriate for their target month.

## 3. Pass z and c Into the Generator (G)

The generation process can be expressed as:

where:

- z = a latent noise vector that introduces natural variation between synthetic days
- c  =  a  condition  vector,  which  may  encode  weekday  or  weekend  status,  approximate season, broad consumption tendency for the month.

This  conditional  setup  allows  the  Generator  to  resemble  the  participating  household's observed appliance-level behavior but also follow the high-level seasonal context of each month.

## 4. Supervisor Enforces Temporal Structure

<!-- formula-not-decoded -->

12 months × 30 ₺ 2 = 360-370 synthetic days

Nynthetic E 360-370 normalized daily sequences

60 real days † 360 synthetic days ‹ 420 total days

The Supervisor predicts next-step latent transitions, ensuring:

- smooth curves
- realistic 144-step daily progression

## 5. Recovery Network Reconstructs a Daily Load Curve

<!-- formula-not-decoded -->

This  produces  the  144-point  normalized  synthetic  daily  sequence,  which  has  the  same structure as the real normalized daily sequences used for training.

6. Repeat for All Missing Days

The  process  repeats  until synthetic profiles  for  all  missing  12  months  have  been generated, resulting in:

* = R(H)

Equation 3.28

These are combined with the 60 real days per monitored appliance to form:

Equation 3.29

This  becomes  the  full  high-resolution  dataset  for  each  monitored  appliancet  needed  for scaling, appliance decomposition, and SARIMAX forecasting.

## A. Number of Synthetic Days Generated

Since the household provided two months of real data:

- Total required months: 14

- Real months: 2

- Synthetic months: 12

Approximate number of synthetic days required:

Equation 3.30

Each generated day is a normalized 144-step sequence. This synthetic day count applies independently to each monitored appliance.

## B. Characteristics of Raw Synthetic Output

The  raw  synthetic  output  produced  by  the  Generator  exhibits  certain  characteristics. Specifically:

## 1. Smoother Curves Compared to Real Data

TimeGAN tends to produce sequences with reduced noise and fewer abrupt fluctuations.

This behavior is expected and desirable because:

- GANs learn the underlying pattern, not sensor noise.
- Noise from the physical device is not reproduced.

## 2. Preservation of Daily Structure

Even with smoother profiles, the synthetic curves still reflect morning rise in load, plateau or  mid-day  baseline,  evening  peak,  and  night-time  decline  to  indicate  a  successful  learning  of household usage cycles.

## 3. Natural Variation from Day to Day

The random latent vector z causes the model to generate slightly different shapes each day, preventing unnatural repetition or 'copy-pasted' daily curves.

## 4. Seasonal Patterns Reintroduced During Later Scaling

While TimeGAN learns general day-level shapes, it does not directly encode hotter-month consumption,  cooler-month  consumption,  and  seasonal  appliance  behavior.  These  patterns  are reintroduced  during  the  monthly  rescaling  stage,  where  each  synthetic  month  is  matched  to the participating  household's  actual  Meralco  energy consumption for that month, with scaling applied proportionally across appliances.

| Time   |   Synthetic Day 1 |   Synthetic Day 2 |   Synthetic Day 3 |
|--------|-------------------|-------------------|-------------------|
| 00:00  |              0.08 |               0.1 |              0.07 |

Table 3.27 Example of Normalized Raw Synthetic Daily Output

| 00:10   | 0.07   | 0.09   | 0.08   |
|---------|--------|--------|--------|
| …       | …      | …      | …      |
| 23:50   | 0.19   | 0.17   | 0.21   |

These values, shown in Table 3.27, represent the raw synthetic daily output generated by the  Improved  TimeGAN before any rescaling is applied. Actual dates are assigned sequentially during the synchronization stage to ensure continuity with the real two-month dataset

## 3.4.4 Monthly Energy Scaling Using Meralco Bills

Once the Improved TimeGAN has generated the normalized synthetic daily profiles, the next  step  is  to  convert  these  normalized  values into realistic appliance-level wattage and energy consumption,  proportionally  aligned  with  the  participating  household's  monthly  electricity  usage. TimeGAN provides only the shape of the daily load curves, not the absolute magnitude. Therefore, each synthetic month must be scaled so that the combined appliance-level energy aligns with the actual household monthly energy consumption reported in the Meralco bill.

This  stage  ensures  that  the  reconstructed dataset reflects true energy usage rather than arbitrary GAN-generated magnitudes.

## A. Compute Synthetic Monthly Energy

For each synthetic day, the normalized 144-point load curve is first denormalized back into estimated  wattage  values.  These wattage values are then converted to kWh using the 10-minute sampling interval.

1. Denormalize the Synthetic Daily Curve

For each synthetic day (144 normalized points), denormalize using:

<!-- formula-not-decoded -->

## Where:

- xnorm = TimeGAN output

s0.

ror u.vo al uu.00.

Znorm = 0.08

Emax - Imin = 810 - 12 = 798

z = 0.08 × 798 + 12

z = 63.84 + 12 = 75.84 W

For 0.07 at 00:10

Znorm = 0.07

- xmin,xmax = from the real 2-month dataset

z = 0.07 x 798 ÷ 12

This returns the data to watts (W). For example,

· = 55.86 + 12 = 67.86 W

For 0.19 at 23:50

Inorm = 0.19

From earlier, across the 2-month dataset, it was assumed:

z = 0.19 x 798 ÷ 12

So:

This step is applied to the normalized synthetic values for Synthetic Day 1, as presented in Table 3.27.

<!-- formula-not-decoded -->

As a result, the values shown in Table 3.28 represent the denormalized outputs produced after applying the inverse scaling procedure.

| Time   |   Normalized Power (Synthetic Day 1) |   Denormalized Power (W) |
|--------|--------------------------------------|--------------------------|
| 00:00  |                                 0.08 |                    75.84 |
| 00:10  |                                 0.07 |                    67.86 |

- Xmin = 12W
- Xmax = 810W

AI 00.00. r = 10.04VV

144

144

Ed = 2

· = 0.01264 kWh

Pt

Pt

75.84

6000

t=1

1= bours

6000

Ed = I

6000

6000

ДІЛА Ч !

t=1

Table 3.28 Example of Denormalizing a Synthetic Daily Sequence

| …     |    … |      … |
|-------|------|--------|
| 23:50 | 0.19 | 163.62 |

The  normalized  values  come  directly  from  the  TimeGAN  sample  table,  while  the denormalized values are computed using the same xmin and xMax parameters applied during the Min-Max normalization stage.

## 2. Convert Denormalized Watts to kWh

Each 10-minute interval corresponds to:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

The total energy for a synthetic day d is computed as:

<!-- formula-not-decoded -->

The raw synthetic monthly energy consumption is then:

<!-- formula-not-decoded -->

Using the corresponding denormalized wattage values shown in Table 3.28, the next step computes the energy contribution of each 10-minute interval.

<!-- formula-not-decoded -->

Thus:

Assume inat ine tull-day

EDD:10 =

= = 0.01131 kWh

67.86

Eraw =

6000

Ex = 6.95 kWh

Ed d=1

At 23:50: P = 163.62W

E23:50 =

<!-- formula-not-decoded -->

163.62

6000

After  converting  the  denormalized  power  readings  into  their  equivalent  10-minute  kWh values, the resulting energy values are summarized in Table 3.29.

Table 3.29 Example of Denormalized Power to kWh

| Timestamp   | Power (W)   | kWh for 10 min   |
|-------------|-------------|------------------|
| 00:00       | 75.84       | 0.01264          |
| 00:10       | 67.86       | 0.01131          |
| …           | …           | …                |
| 23:50       | 163.62      | 0.02727          |

After that, total energy is computed by adding all 144 10-minute kWh values.

Assume that the full-day total comes to:

This  represents  the  raw  appliance-level  synthetic  energy  total  prior  to  household-level scaling.

3. Compute Raw Synthetic Monthly Energy

If a month has D days:

<!-- formula-not-decoded -->

il ine syntelic mont nas 31 days.

Emonitored, mr

Eraw = 31 × 6.95 = 215.45 kWh

EMeralco,m = household kWh from the Meralco bill

Emonitored, m =

DEB appliances

Coveragem =

EMeralco,m where D is the number of days in the month (28-31 depending on the month). This value is usually lower or higher than the real household consumption, because GANs learn the shape but not the absolute consumption.

## For example:

<!-- formula-not-decoded -->

## B. Compute the Scaling Factor

Before  computing  the  scaling  factor,  it  is  important to clarify that the Meralco bill reflects the entire household's monthly electricity consumption, while the study monitors only three selected appliances. To contextualize this difference, the monitored portion of the household's total monthly energy is  estimated  for each of the two months where real smart-plug and Meralco data overlap. For each month m,

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

The monthly coverage ratio is then computed as:

<!-- formula-not-decoded -->

This  provides  a  month-by-month  indication  of  how  much  of  the  household's  energy  is represented  by  the  monitored  subset.  The  study  reports  both  month-specific  coverage  and  the overall average across the two months. This percentage is used only as contextual information; the Meralco  scaling  factor  is  derived  from  household-level  totals  but  applied  proportionally  to  the

appliance-level  synthetic  data,  because  the  Improved  TimeGAN  generates  appliance-level  load curves, while the Meralco bill reflects total household consumption.

The Meralco bill provides the actual monthly energy consumption in kWh. Let:

- EMeralco  = actual monthly energy in kWh
- Eraw  = raw GAN total for that same month

The scaling factor α is computed as:

<!-- formula-not-decoded -->

This factor indicates how much the appliance-level synthetic month must be expanded or reduced so that the combined energy matches the household's actual energy usage. If α &gt; 1, the raw synthetic month is too low and must be scaled upward; if α &lt; 1, the raw synthetic month is too high and must be scaled downward.

For example:

For the month of March, the household's Meralco bill reports:

The Improved TimeGAN produces a raw synthetic monthly total of:

Then:

Thus, the synthetic month is 19.7% lower than the true consumption, and must be scaled upward by multiplying every 10-minute wattage value by 1.197.

## C. Apply Scaling to the Synthetic Month

All appliance-level wattage values in the synthetic month are rescaled:

scaling lactor.

scaling lactor.

240

a =

225

262

6000

pocaled = aPt

= 1.197

a =

= 0.916

This ensures that:

<!-- formula-not-decoded -->

This preserves the shape, determined by the GAN, and the size (magnitude), determined by real Meralco kWh. The result is a synthetic month that accurately reflects both daily behavioral patterns and true household energy consumption.

Table 3.30. Example of Synthetic Month Scaling

| Month   |   Meralco kWh |   Raw GAN kWh |     α |   Final kWh |
|---------|---------------|---------------|-------|-------------|
| March   |           225 |           188 | 1.197 |         225 |
| April   |           240 |           262 | 0.916 |         240 |

As illustrated in Table 3.30, the monthly scaling procedure corrects discrepancies between the raw synthetic output and the actual Meralco billing data.

For March, the synthetic month underestimated consumption at 188 kWh Scaling factor:

,

which is  an  upward  adjustment  of  approximately  19.7% to match the true household usage of 225 kWh.

In contrast, the April synthetic output slightly overestimated consumption at 262 kWh Scaling factor:

This requires the values to be scaled downward by about 8.4% using a factor of 0.916.

After  scaling,  the  combined  appliance-level  synthetic  energy  for  each  month  perfectly matches the household's true energy consumption, correcting the natural magnitude limitations of GAN outputs.

188

<!-- formula-not-decoded -->

Inus.

225

pacaled = a. Pt

188

0 =

= 1.197

Assume that for one synthetic da

P08:00 = 82.5 W

08:00

Substituting:

08:00

## D. Scaling Applied to 10-Minute Interval Values

Once  the  monthly  scaling  factor  α  has  been  computed,  it  is  applied  directly  to  every 10-minute  wattage  value  generated  by  TimeGAN.  This  step  is  essential  because  the  Improved TimeGAN  produces  daily  sequences  at  fixed  10-minute  resolution  (144  points  per  day).  The structure of these sequences must remain intact throughout scaling.

The scaled wattage for each interval t is computed as:

- Synthetic Day 1 → 144 points × α
- Synthetic Day 2 → 144 points × α
- Synthetic Day 3 → 144 points × α
- …
- Synthetic Day D → 144 points × α

where D is the number of days in the synthetic month (28-31).

To  illustrate  how  the  scaling  factor  α  is  applied  to  each  10-minute  interval,  consider the month of March, in Table 3.30, where:

- EMeralco = 225 kWh
- Eraw = 188 kWh

Thus:

Assume that for one synthetic day in March, the raw denormalized wattage at 08:00 is:

The scaled wattage for this interval is computed as:

Substituting:

Equation 3.43

144 intervals/day × D days/month

Posaled

= 98.66 W

144 intervals/day × D days/month

Rounded:

Dscaled

08:00

598.7 W

Rounded:

Shown in Table 3.31 is raw synthetic wattage of 82.5 W becomes 98.7 W after applying the monthly scaling factor for March.

Table 3.31 Example of Interval-Level Scaling

| Timestamp        |   Raw Synthetic Power (W) |   Scaling Factor α |   Scaled Power (W) |
|------------------|---------------------------|--------------------|--------------------|
| 2025-03-05 08:00 |                      82.5 |              1.197 |               98.7 |

This interval-level computation is applied to all 144 points of each synthetic day within the month. After scaling every interval, the total monthly energy automatically equals the Meralco-recorded value (225 kWh for March), while the original TimeGAN shape remains intact. This  ensures  that  every  individual  10-minute  interval  is  scaled  proportionally,  adjusting  only magnitude while preserving the temporal pattern generated by the GAN. Importantly, the procedure does not scale daily  totals  or  monthly  totals directly; instead, the totals adjust automatically after interval-wise scaling.

## E. Preservation of 10-Minute Structure After Scaling

After  the  scaling  factor  has  been  applied,  the  10-minute  temporal  resolution  remains unchanged. Only the wattage values are modified, not the number of intervals.

- Before scaling:
- After scaling:

Thus, all timestamps remain unchanged, and the daily load shapes produced by the model are  preserved.  Only  the  magnitudes  of  the  synthetic  values are adjusted proportionally to match

3

Share, = -

Etotal = LEa

Ex = Total energy consumed by appliance a (over 2 months)

Etotal the  participating  household's  actual  monthly  consumption.  As  a  result,  the  final  scaled  dataset maintains the original temporal structure while ensuring that each month's total aligns exactly with the corresponding Meralco billing record.

## 3.4.5 Appliance-Level Reconstruction

After  generating  and  scaling  the  synthetic  daily  load  profiles  for  all  missing  months,  the final  step  is  to  convert  the  aggregated  synthetic  load  curve  into  per-appliance  synthetic  energy curves. This step is necessary because:

- The Improved TimeGAN was trained on the aggregated monitored load, and
- The forecasting framework requires appliance-level time series, consistent with the actual smart-plug data structure.

Thus, the  GAN produces synthetic data representing the total monitored subset, and this total must be decomposed back into separate appliance curves.

## A. Computing Real Appliance Energy Shares

The disaggregation process begins by analyzing the real 2-month smart-plug dataset. For each monitored appliance a, the total energy consumption is computed and compared to the total aggregated monitored load. Let:

Equation 3.44

<!-- formula-not-decoded -->

The appliance's share is then computed as:

where:

- Ea = total energy consumed by appliance a during the real two-month period

<!-- formula-not-decoded -->

- Etotal = total household energy during the same period

These shares reflect  the  real  usage  proportions  found  during  monitoring. They serve as weighting factors for allocating the synthetic aggregated load.

## B. Allocating the Synthetic Aggregated Load to Appliances

Once  a  synthetic  day  has  been  generated  and  scaled  using  the  Meralco-based  energy adjustment (Section 3.4.4), the resulting curve represents:

- a 144-point, 10-minute synthetic load sequence
- for the combined monitored appliances

To recover appliance-specific synthetic sequences, each 10-minute synthetic power value Pt is multiplied by the appliance's share:

<!-- formula-not-decoded -->

This computation is applied across all appliances, for all 144 ten-minute intervals per day, and  for  all  synthetic  days  within  the  twelve  reconstructed  months.  This  guarantees  that  every synthetic data point is preserved, appliance-level patterns remain proportionally realistic based on their measured energy shares, and that the reconstructed appliance curves collectively sum back to the scaled synthetic household load for each interval.

An example of this proportional decomposition for a single synthetic day is shown in Table 3.31.

Table 3.31 Sample Appliance-Level Decomposition for a Synthetic Day

| Time   |   Total |   Ref 30% |   Fan 10% |   Others 60% |
|--------|---------|-----------|-----------|--------------|
| 08:00  |     400 |       120 |        40 |          240 |
| 20:00  |     550 |       165 |        55 |          330 |

For example:

Suppose the GAN-generated and scaled synthetic value at 08:00 is:

If two-month monitoring found:

- Refrigerator = 30%
- Electric Fan = 10%
- Other monitored appliance = 60%

Then, for ref at 30%

0.30 x 400 = 120W

For Fan at 10%

0.10 x 400 = 40W

For Others at 60%

0.60 x 400 = 240W

At every time interval t:

Equation 3.48

The  same  proportional  allocation  is  applied  at  every  10-minute  interval  throughout  the synthetic  day.  After  proportional  allocation,  the  process  yields  three  synthetic  appliance-level datasets,  each  covering  the  full  14-month  period  at  the  original 10-minute resolution (144 points per day). These reconstructed sequences match the structure of the real smart-plug logs, providing complete,  appliance-specific  time  series  that  are  rready  for  individual  appliance-level  SARIMAX model training.

## C. Aggregating the Appliance-Level Synthetic kWh to Hourly Resolution

Before  SARIMAX forecasting, the reconstructed 10-minute appliance-level synthetic data must be aggregated to hourly resolution, so that other variables align correctly. Each hour consists of six 10-minute intervals, therefore:

## 1. Hourly Energy Calculation

For appliance a in hour h:

<!-- formula-not-decoded -->

Where each 10-minute interval contributes:

<!-- formula-not-decoded -->

## 3.4.6 Post-Generation Validation

After  generating  and  scaling the synthetic daily profiles, the final step is to verify that the reconstructed  dataset  preserves  the  statistical  and  temporal  characteristics  of  the  participating household's real  appliance-level  electricity  data.  If the GAN-generated data deviates too far from the  real  appliance-level  distribution,  it  may  introduce  bias  into  the  forecasting  model  or  distort seasonal trends.

To ensure  the quality of  the  synthetic  dataset,  this  study  replicates  the  validation procedures  used  by  Tang  et  al.  (2025),  which  include  three  classes  of  evaluation:  statistical comparison, Principal Component Analysis (PCA), and t-Distributed Stochastic Neighbor Embedding (t-SNE).

## A. Denormalization of Synthetic Data

Before  any  comparison  can  be  made,  the  normalized  synthetic  daily  sequences  are converted back into their original physical units (watts and kilowatt-hours). This is performed using the inverse of the min-max scaling applied during preprocessing:

<!-- formula-not-decoded -->

Denormalization ensures that all validation procedures reflect realistic energy values and can be directly compared against real smart-plug measurements.

## B. Statistical Comparison

Once denormalized, both the real and synthetic datasets undergo a statistical comparison across the following metrics:

- Mean (Central Tendency)

=

= D

1

-

77

7T.

71.

Kurtosis =

2(1 - 12)]

Skewness =

[7 + z)z

TL.

[7-1][n-2)(7-3)

1=1

i=1

(17- 1)(17- 2)

1=1

The average energy level across the day:

<!-- formula-not-decoded -->

- Standard deviation (Dispersion)

The variability or dispersion:

<!-- formula-not-decoded -->

(* - ")

- Quartiles (Q1, Median, Q3)

The distribution shape and depth. Quartiles are computed from the empirical distribution of values within each daily sequence and provide a robust measure of distribution depth and symmetry.

- Skewness (Distribution Asymmetry)

The asymmetry in consumption patterns. Using the adjusted Fisher-Pearson coefficient:

<!-- formula-not-decoded -->

- Kurtosis

Tail  heaviness  or  peak  sharpness.  The  closer  synthetic  kurtosis  is  to  real  kurtosis,  the more faithfully the GAN captures rare peaks and tail behavior.

Equation 3.55

These  statistics  are  computed  for  every  daily  sequence  and  then  summarized  into comparative  tables.  The  expectation  is  that  synthetic  data  should  maintain  a  mean  error  below 0.5%,  quartile  differences  within  0.5%,  variance  errors  under  10%,  and  skewness  and  kurtosis values that closely match those of the real dataset. In this study, the same tolerance thresholds are applied. Synthetic daily curves that fall within these ranges are regarded as statistically consistent with  the  participating  household's  observed  appliance-level  load  patterns,  indicating  that  the

3(7 - 1)2

Improved  TimeGAN  has successfully captured both the distributional  properties  and  the  natural variability present in the real smart-plug data.

## C. PCA Visualization

To  evaluate  similarity  in  structural  patterns,  both  real  and  synthetic  sequences  are projected into  a  lower-dimensional  space  using  Principal  Component  Analysis  (PCA).  PCA condenses  the  144  time-step  daily  sequence  into  a  few  comprehensive  components  while preserving  the  major  variance  directions.  If  the  Improved TimeGAN has successfully learned the underlying daily load dynamics, the PCA scatter plot should show:

- overlapping clusters of real and synthetic days
- similar spread, density, and orientation

Such  alignment  indicates  that  the  synthetic  days  exhibit  comparable  structure  to  the participating household's real appliance-level electricity patterns. PCA is performed by:

1. Standardizing each sequence.
2. Computing the covariance matrix

<!-- formula-not-decoded -->

3.Performing eigenvalue decomposition to extract principal components.

Because PCA preserves directions of maximum variance, overlapping clusters of real and synthetic  points  in  the  2-D  PCA  plot  indicate  that  the  synthetic  data  capture  the major temporal patterns (morning rise, midday plateau, evening peak) present in real household usage.

## D. t-SNE Visualization

While  PCA  captures  linear  relationships,  t-Distributed  Stochastic  Neighbor  Embedding (t-SNE)  evaluates  non-linear  similarity.  This  method  projects the sequences into a 2-dimensional manifold that highlights local neighborhood relationships. In a successful validation:

- synthetic points intermix naturally with real points
- no obvious isolated synthetic clusters appear
- local shapes and groupings remain preserved

Gij =

Pili =

ер (-||zi - x;||2 /20?)

9ij

Ex+exp(-|z-*l2/203)

1. High-dimensional similarity (Gaussian kernel) For each pair of real data points xi, xj:

<!-- formula-not-decoded -->

2. Low-dimensional similarity (Student t-distribution)

3. Optimization objective (KL divergence)

t-SNE finds low-dimensional representations by minimizing:

<!-- formula-not-decoded -->

If real and synthetic daily profiles form intermixed clusters with similar density and shape in t-SNE space, this indicates that the GAN has correctly learned both the local and global geometric structure of the participating household's appliance-level daily usage patterns. Only when all three validations  indicate  acceptable  alignment  does  the  appliance-level  dataset proceed to SARIMAX model training.

## E. Synchronization of Real, Synthetic, and Weather Datasets

The final step is the synchronization of all components into a single continuous 14-month time series. This unified dataset contains:

- Two months of real, preprocessed appliance-level 10-minute measurements per monitored appliance, and
- Twelve months of scaled, per-appliance synthetic profiles  generated  and  adjusted using the Improved TimeGAN.

Synchronizing Real (2-Month) and Synthetic (12-Month) Data

1. Identify the final timestamp of the real dataset

<!-- formula-not-decoded -->

For  the  participating household, the last valid timestamp of the real preprocessed data is determined.  For  example,  the  final  datapoint  is  2025-03-01  23:50.  This  marks  the  boundary between real and synthetic portions.

## 2. Assign dates to synthetic days

Each synthetic daily sequence contains 144 points (10-minute intervals). Synthetic  Day  1  is  assigned  to  the  calendar  day  immediately  after  the last real observation. For example, in Table 3.32:

Table 3.32 Assignment of Dates

| Synthetic Day   | Assigned Date   | Time Range   |
|-----------------|-----------------|--------------|
| Day 1           | 2025-03-02      | 00:00 →23:50 |
| Day 2           | 2025-03-03      | 00:00 →23:50 |
| Day 3           | 2025-03-04      | 00:00 →23:50 |
| …               | …               | …            |
| Day 31          | 2025-04-01      | 00:00 →23:50 |

This continues until all synthetic days (≈ 360-370) are mapped to concrete calendar dates, filling the remaining 12-month gap.

## 3. Ensure full 14-month continuity

Because  the  real  dataset  covers  ~60  days  and  the  target  is  14  months  (≈  425  days), synthetic timestamps are assigned sequentially without gaps until the final required calendar day is reached.

This produces:

- A single continuous timeline
- No missing days
- No timestamp collisions
- 144 consistent rows per day

## Integration of Weather Data

Weather  variables  (temperature,  humidity,  rainfall)  were  collected  hourly  via  API.  Since TimeGAN data is at 10-minute resolution, synchronization follows:

## 1. Real 2-month segment

- Appliance data (10 min) is aggregated to hourly
- Weather data directly matches each hourly timestamp

## 2. Synthetic 12-month segment

- Synthetic appliance curves are aggregated to hourly (mean of 6×10-min intervals)
- These hourly points are joined with the weather API's hourly timestamps

After synchronization and weather alignment, each appliance has:

## Per Appliance

- 14 months × ~30.4 days per month × 144 points per day ≈ 61,200 rows (10-minute)
- Hourly aggregated version: 14 months × ~30.4 days × 24 hours ≈ 10,200 hourly rows
- For the Three Monitored Appliances
- ~61,200 × 3 = 183,600 10-minute records
- ~10,200 × 3 = 30,600 hourly records

## Total Duration

- ~425 calendar days
- ~10,200 hours

| Timestamp         | Appliance_ ID   | Hourly_kW h   | Temp_C   | Humidity_ %   | Rain_mm   | is_real   |
|-------------------|-----------------|---------------|----------|---------------|-----------|-----------|
| 2025-01-1 5 08:00 | H1_Fan          | 0.0698        | 28.4     | 65            | 0.0       | 1         |
| 2025-01-1 5 09:00 | H1_Fan          | 0.0720        | 29.1     | 63            | 0.0       | 1         |
| …                 | …               | …             | …        | …             | …         | …         |

Table 3.33 Sample of the Final Integrated Hourly Dataset

| 2025-03-0 2 00:00   | H1_Fan   |   0.0837 |   27.0 |   72 |   0.1 |   0 |
|---------------------|----------|----------|--------|------|-------|-----|
| 2025-03-0 2 01:00   | H1_Fan   |   0.0792 |   26.4 |   74 |     0 |   0 |

A  sample  portion  of the final synchronized  dataset,  combining  the  real  10-minute observations,  the twelve months of synthetic appliance-level values per monitored appliance, and the  aligned  hourly  weather  variables,  is  presented  in  Table  3.33.  The  appliance\_id  column  is included in the final dataset only as a label used to organize and filter the data.

## 3.5 Modeling Approach

This section outlines the end-to-end  pipeline for forecasting hourly  appliance-level electricity  consumption  for  each  monitored  appliance.  The  approach  builds  on  the  validated appliance-level dataset (Table 3.33) and covers pre-modeling checks, SARIMAX model estimation, baseline performance evaluation, diagnostic validation, and error analysis.

## 3.5.1 Pre-Modeling Checks

## A. Stationarity Assessment

SARIMAX  models  assume  a  stationary  time  series.  Stationarity  was  verified  using  the Augmented Dickey-Fuller (ADF) test, which checks whether the mean and variance of Y t  remain constant  over  time.  The  ADF test essentially tests whether the time series has a unit root, which would make it non-stationary. The ADF test is based on the following regression equation:

<!-- formula-not-decoded -->

Where:

- is the change in energy consumption at time t ∆𝑌 𝑡 = 𝑌 𝑡 - 𝑌 𝑡-1
- is the lagged value of the original series, 𝑌 𝑡-1
- is the constant (intercept), α
- is a trend term (if the model includes a trend), β𝑡

- is  the  coefficient  of  the  lagged  value ,  indicating  the  presence  of  a  unit  root γ 𝑌 𝑡-1 (non-stationarity),
- are the coefficients for the lagged differences (to account for serial correlation), δ 1 ,  ...,  δ 𝑝
- ϵ𝑡
- is the random error (white noise).

For Test Statistic, the ADF test statistic is computed as:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Where:

- is the estimated coefficient for γ 𝑌 𝑡-1
- is the standard error of 𝑆𝐸(γ) γ

## Interpretation:

- Null Hypothesis : The series has a unit root 𝐻 0
- Alternative Hypothesis : The series is stationary 𝐻 𝐴

If the p-value from the ADF test is less than 0.05, we reject the null hypothesis, indicating that the series is stationary. Otherwise, if the p-value is greater than 0.05, we fail to reject the null hypothesis,  suggesting  that  the  series  is  non-stationary.  If  the  series  is  non-stationary, we apply differencing to induce stationarity. This could involve:

- First differencing (subtracting each observation from the previous one) or,
- Seasonal differencing (subtracting the observation from the value 24 hours earlier).

For example, for an appliance's hourly series, if the ADF test yields and 𝐴𝐷𝐹 =- 4. 12 ,  we  would  reject  the  null  hypothesis  and  conclude  that  the  series  is  stationary,  no 𝑝 = 0. 01 further  differencing  is  required.  However,  if ,  we  fail  to  reject  the  null hypothesis and 𝑝 = 0. 26 apply differencing to make the series stationary.

## B. Seasonality Detection and Adjustment

After  confirming  stationarity,  the  next  step  is  to  detect  seasonality.  Seasonal  patterns  in energy  consumption  are  often  periodic,  typically  on  a  daily  cycle  (e.g.,  24-hour  periodicity).  To detect  these  seasonal  patterns,  we  use  the  Autocorrelation  Function (ACF), which helps identify

the lag at which the series repeats. If the series exhibits daily seasonality, the ACF will show a peak at lag 24 (representing a 24-hour cycle).

## 1. Initial Seasonality Detection

The SARIMAX model is first applied to detect the seasonal period, which is typically set to 24 hours for  daily  cycles.  The seasonal component is identified based on the observed pattern in the ACF plot,  which  will  show  periodic  peaks  at  the  seasonal  period  (lag  24  for  daily  seasonality).  This serves as the initial estimate for the seasonal period in the SARIMAX model.

## 2. Seasonal Parameter Selection and Refinement

Once  the  initial  seasonality  has  been  detected,  the  seasonal  parameters  (AutoRegressive  (AR) and  Moving  Average  (MA)  components)  and  seasonal  differencing  are  systematically  refined through model identification procedures. This involves analyzing both the Autocorrelation Function (ACF) and Partial Autocorrelation Function (PACF) plots to determine appropriate seasonal orders.

The seasonal parameter selection follows these steps:

- Seasonal Differencing (D):  Applied  to  remove  seasonal  trends.  The number of seasonal differences  is  determined  by  examining  whether  the  seasonal  pattern  persists  after differencing.
- Seasonal AR Order (P): Identified by examining the PACF plot at seasonal lags (multiples of 24). Significant spikes at these lags indicate the appropriate seasonal AR order.
- Seasonal MA Order (Q): Identified by examining the ACF plot at seasonal lags. Significant spikes at these lags indicate the appropriate seasonal MA order.
- Multiple candidate  models  with  different  combinations  of  seasonal  parameters  are estimated  and  compared  using  the  Akaike  Information  Criterion  (AIC)  and  Bayesian Information  Criterion  (BIC).  The  model with the lowest AIC/BIC values, while maintaining statistically  significant  coefficients  and  satisfying  diagnostic  checks,  is  selected  as  the optimal specification.

Performance  is  evaluated  using  forecasting  accuracy  metrics  including  Mean  Absolute Percentage  Error  (MAPE)  and  Root  Mean  Square  Error  (RMSE).  The  selected  seasonal

parameters ensure that the model accurately captures the periodic patterns in energy consumption while maintaining parsimony and interpretability.

## 3.5.2 Model Estimation and Fitting

This subsection describes the formulation and estimation of the forecasting model used to predict  hourly  appliance-level  energy  consumption.  The  model  selected  for  this  study  is  the Seasonal Autoregressive Integrated Moving Average with Exogenous Variables (SARIMAX), which extends the standard ARIMA framework by incorporating both seasonality and external explanatory variables (exogenous regressors).

## A. SARIMAX Model Structure

The  SARIMAX  (Seasonal  AutoRegressive  Integrated  Moving  Average  with  eXogenous factors)  model  is  an  extension  of  the  ARIMA  model,  which  incorporates  both  seasonal  and non-seasonal components. This makes it ideal for time series forecasting, especially when patterns such as seasonality (e.g., daily or weekly cycles) are present in the data.

A SARIMAX model is written as SARIMAX (p, d, q) (P, D, Q)s where:

- p is the order of the AR term.
- d is the order of differencing needed to make the data stationary.
- q is the order of the MA term.
- P is the order of the seasonal AR term.
- D is the order of the seasonal differencing needed to make data stationary.
- Q is the order of the seasonal MA term.
- S is the number of periods in a season.

A SARIMAX (p, d, q) (P, D, Q)s is mathematically represented as:

Equation 3.62

Where

- is the observed energy consumption at time t 𝑌 𝑡

- is  the  autoregressive  (AR)  term,  which  accounts  for  the  relationship  between  the ϕ 1 current value and its previous value 𝑌 𝑡-1
- is the moving average (MA) term, which represents the influence of past forecast errors θ 1 on the current value. ϵ 𝑡-1
- is  the  coefficient  of  the  exogenous  variables  ( ),  such  as  weather  (temperature, β 1 𝑋 𝑡 humidity) and time-related features (hour of day, day of week, weekend flag, holiday flag, etc.), which help to explain variations in energy consumption beyond the historical values of 𝑌 𝑡
- The  seasonal  components  (AR,  MA,  differencing)  are  selected  based  on  the  specific seasonal  patterns  observed  in  the  data  (e.g.,  daily  seasonality)  using  systematic  model identification procedures.

This  formulation  allows  the  SARIMAX  model  to  handle  both  short-term  (non-seasonal) dependencies, as well as long-term seasonal cycles. It also incorporates external factors, making it more flexible  and  suitable  for  forecasting  energy  consumption,  where external variables such as weather conditions and time of day have a significant influence.

## 1. Autoregressive (AR) Component:

The  AR  part  captures  the  serial  correlation  between  the  current  value  and  the  lagged values in the time series. The model's order p indicates how many lagged terms are included. 2. Moving Average (MA) Component:

The MA component models the relationship between the current value and the residual errors  from  the  previous  time  steps.  The  order  q  defines  how  many  past  forecast  errors  are considered in the model.

## 3. Seasonal Components:

The seasonal components allow the model to capture periodic patterns in the data. The seasonal orders (P,D,Q) correspond to the seasonal AR, differencing, and MA terms, respectively. These components are identified through systematic analysis of ACF and PACF plots and refined using the Akaike Information Criterion (AIC) to optimize forecasting performance.

## 4. Exogenous Variables

The exogenous variables are external factors that can influence energy consumption. In the  SARIMAX  model,  these  variables  (such  as  temperature,  humidity,  or  day  of  the  week)  are incorporated to help explain the variations in energy consumption that cannot be explained by the historical values of Y t   alone.

The SARIMAX model, therefore, combines these components to generate forecasts that account for both time-based dependencies (AR, MA), external factors (X\_t), and seasonal patterns (seasonal AR, MA), all of which are essential for accurate energy consumption forecasting.

## B. Model Identification and Parameter Selection

In time series modeling, the AR (AutoRegressive) and MA (Moving Average) orders, along with  the  seasonal  components,  are  critical  for  determining  the  model  structure.  The  process  of selecting  these  orders  involves  using  Autocorrelation  Function  (ACF)  and Partial Autocorrelation Function (PACF) plots to analyze the time series data and determine the appropriate values for p, d, q (non-seasonal components) and P, D, Q (seasonal components).

## 1. ACF and PACF Plots

- ACF  Plot:  Shows  the  correlation  of  the  time  series  with  its  own  lagged  values.  The significant spikes in the ACF indicate the MA (Moving Average) order q.
- PACF Plot: Shows the partial correlation  between  the  series  and  its  lagged values after removing  the  effect  of  earlier  lags.  The  significant  spikes  in  the  PACF  indicate  the  AR (AutoRegressive) order p.

The seasonal period is set to 24 hours (for daily cycles), as determined from the previous seasonality  detection  step.  This  ensures  that  the  model  can  capture  the  periodic  fluctuations  in energy consumption.

## 2. Refining Model Orders Using the Akaike Information Criterion (AIC)

After  identifying  the  initial  AR  and  MA  orders  from  the  ACF  and  PACF  plots,  the model orders (p, d, q) and (P, D, Q) are further refined using the Akaike Information Criterion (AIC). The

Cov (Yt, Yt-k Y4-1»..,Y4-(k-1))

Var(Y+ | Y4-1,..., X4-(k-1)) · Var(Ye-k | Y4-1,..., Yt-(4-1))

AIC helps balance the model's fit (likelihood) and its complexity (number of parameters), selecting the model that best explains the data without overfitting.

The AIC is calculated using the formula:

<!-- formula-not-decoded -->

where:

- 𝑘 is  the  number  of  estimated  parameters  in  the  model  (including  AR  and  MA  terms, seasonal terms, and exogenous variables).
- 𝐿 is the maximized value of the likelihood function, which measures how well the model fits the data.

## 3. Model Selection

The optimal model is chosen by minimizing the AIC value. A lower AIC indicates a better model,  as  it  suggests  a  better  trade-off  between  model  fit  and  complexity.  The  model  with  the lowest AIC is selected as the final model for forecasting energy consumption.

The Partial Autocorrelation Function (PACF)  is used  to identify the order of the AutoRegressive (AR) process in a time series model. Unlike the ACF, which shows the correlation between the time series and its lagged values, the PACF shows the correlation between the time series and its lagged values after removing the effect of intervening lags.

## 4. PACF Formula

The  PACF  is  computed  as  the  correlation  between  the  residuals  of  the  autoregressive process up to a certain lag. The formula for the PACF at lag k is:

Equation 3.64

Where:

- is the partial autocorrelation at lag 𝑘 , ϕ 𝑘𝑘
- is the observed value at time t, 𝑌 𝑡

- Cov  denotes  the  covariance  between  the  current  value  and  the  lagged  value,  after accounting for the influence of all the intermediate lags.
- Var represents the variance of the residuals after removing the effects of intervening lags.

The PACF can be calculated recursively, typically using methods such as the Durbin-Levinson  algorithm,  which  computes  the  coefficients  for  AR  processes.  It  is  interpreted using the following:

- The PACF plot displays the partial autocorrelation coefficients for various lags.
- Significant spikes in the PACF plot indicate the appropriate order of the AR process
- If a spike is observed at lag p and subsequent spikes are not significant, then the AR order p is chosen as p.

## C. Exogenous Variables and Feature Vector

In  the  SARIMAX model, exogenous variables are external factors that can influence the time  series,  but  are  not  part  of  the series itself. These variables can include factors like weather data,  time-related  features,  and  other  external  variables  that  help  explain  variations  in  energy consumption beyond the historical values of the series. For example, the exogenous feature vector Xt  for each record may look like this:

Xt = [temperature t , humidity t , rainfall t , hour\_of\_day t , day\_of\_week t , is\_weekend t , is\_holiday t , lag\_24 t , lag\_168 t , rolling\_mean\_24 t , rolling\_mean\_168 t ] and the target variable is Y t  = kWh t

To  ensure meaningful interpretation and proper model estimation, each of the exogenous variables is standardized to its native units.

Feature Vector Integration with SARIMAX

Once  standardized,  the  exogenous  feature  vector  X t   is  used  in  the  SARIMAX  model formulation  as  part  of  the  model's  inputs.  The  inclusion  of  these  exogenous  variables  helps the model  account  for  external  factors  influencing  the  target  variable  and  provides  more  accurate forecasts.

Equation 3.65

Where:

- represents the exogenous feature vector, 𝑋 𝑡

●

β

is  the  coefficient  for  the  exogenous  variables, showing the impact of each feature on

1

energy consumption.

## D. Forecast Horizon and Rolling-Origin Strategy

The model evaluation is performed using a rolling-origin evaluation strategy. This approach ensures  that  each  forecast  is  based  solely  on  past  data,  mimicking  real-world  forecasting conditions where only historical data is available at the time of making predictions.

At  each  forecast  origin t, the model is retrained using all available data, and it generates 24-hour ahead predictions for the next time step. This is repeated for every time step in the testing set,  ensuring  the  model  forecasts  for  unseen  data  and  maintains  the  integrity  of  temporal dependencies.

Mathematically, the forecast at time t for h-steps ahead is:

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

Where:

- is the forecasted value for time t+h 𝑌 𝑡+ℎ|𝑡
- represents the SARIMAX forecasting function, which is trained on the data up to time 𝑓(·) t.

This rolling-origin strategy means that at each forecast origin t, the model:

- Retrains on the data available up to time t,
- Produces 24-hour-ahead predictions for each subsequent time step.

This  process  ensures  that  the  model  forecasts  using  only  historical  data,  making  the evaluation realistic and suitable for real-world deployment.

## E. Data Splitting and Evaluation Window

To  ensure  that  temporal  dependencies  are  preserved  and  that  model evaluation reflects real forecasting conditions, the dataset was divided using a chronological (time-ordered) split rather

141

than random sampling. This ensures that future information does not influence the model's training process.

A  total  of  continuous  hourly  observations  were  available  for  each  monitored  appliance, representing  the  appliance's  energy  consumption  and corresponding environmental variables. To split the data, we followed the established time-series forecasting practices, which allocate:

- 80% of the earliest observations for the training set
- 20% of the most recent observations for the testing set

This chronological 80-20 split ensures that:

- The  training  segment  covers  at  least  one  full  annual  cycle,  allowing  the  model  to  learn seasonal,  weekly,  and  daily  usage  patterns  effectively  and  captures  multiple  daily  and weekly seasonal cycles (24-hour and 168-hour patterns), enabling the model to learn from these recurring patterns,
- The testing segment provides unseen data for model evaluation, ensuring that the model's performance is assessed on data it has never seen during training.

Mathematically, the split is represented as:

## Where:

- represents the data points (energy consumption and environmental variables) at time t 𝑌 𝑡
- is the total number of data points in the dataset. 𝑛

## 1. Rolling-Origin Evaluation Within the Testing Window

Within  the  testing  window,  a  rolling-origin  evaluation  strategy  was  applied.  The  forecast origin  moves  incrementally  through  time,  producing  sequential  24-hour-ahead  predictions.  For each  new  forecast,  the  model  is  retrained  using  all  available  data  up  to  the  current  origin.  For example:

- First Forecast: The model forecasts 24 hours ahead, starting from the earliest point in the testing set.
- Second Forecast: The forecast origin moves forward by one time step, and the model is retrained to produce a new 24-hour-ahead prediction.

This process is repeated for each time step in the testing set, ensuring that each forecast is based on past data.

<!-- formula-not-decoded -->

<!-- formula-not-decoded -->

## 3.5.3 Model Evaluation and Error Analysis

This  section  explains  how  the  developed  SARIMAX  forecasting  model  is  evaluated  and validated to ensure predictive accuracy, stability, and reliability.

## A. Evaluation Design and Performance Metrics

Model evaluation is crucial for assessing the predictive accuracy and overall performance of  the  SARIMAX model. Several error metrics are used to evaluate the model's performance and quantify how well it forecasts energy consumption. These include:

- Mean Absolute Error (MAE): This metric measures the average magnitude of the errors in the forecast, without considering their direction. It is calculated as:

<!-- formula-not-decoded -->

- Root  Mean  Square  Error  (RMSE):  RMSE gives a relatively  high  weight  to  large  errors, making it sensitive to outliers. It is calculated as:

<!-- formula-not-decoded -->

- Mean Absolute Percentage Error (MAPE): This metric expresses forecast accuracy as a percentage  of  the  difference  between  the  actual  and  predicted  values.  It  is  particularly useful when comparing performance across datasets with different scales. It is calculated as:

<!-- formula-not-decoded -->

- R 2 (Coefficient of Determination): This measures how well the predictions approximate the actual data points. It provides an indication of how much variance in the target variable is explained by the model. It is calculated as:

<!-- formula-not-decoded -->

These  error  metrics  allow  the  model  to  be  compared  with  baseline  models  for  each monitored appliance to quantify  the  improvements  brought  by  dynamic  seasonality  adjustments.

For  example,  if  the  SARIMAX  model  with  dynamic  seasonality  adjustments  outperforms  a Seasonal Naïve model (which assumes the forecast is simply the previous period's value), it would indicate that incorporating seasonal adjustments provides better forecasting performance.

## B. Residual Diagnostics and Model Validation

After fitting each appliance-level SARIMAX model, it is crucial to analyze the residuals (the errors  between  the  predicted  values  and the actual observed values). This step ensures that the model has properly captured the underlying patterns in the data and that no information remains in the residuals that could further improve the model.

The residuals are analyzed to verify that they resemble white noise, meaning:

- They are uncorrelated (no systematic pattern),
- They are normally distributed (errors should have a bell-shaped distribution),
- They have constant variance (homoscedasticity).

The following diagnostic techniques are used to validate the residuals:

1.  Autocorrelation  Function  (ACF):  The  ACF  plot  of  the  residuals  should  show  no  significant correlations at any lags if the model has adequately captured the dependencies in the data. If the residuals  display  significant  autocorrelations,  this  suggests  that  the  model  has  not  captured  all temporal dependencies.
2.  Partial  Autocorrelation  Function  (PACF):  Similar  to  the  ACF,  the  PACF  of  the  residuals  is analyzed to check for any unexplained serial correlations. The absence of significant spikes in the PACF plot indicates that no further AR terms are required in the model.
3.  Ljung-Box  Q-test:  This  statistical  test  checks  whether  the  residuals  are  autocorrelated  over a specified  number  of  lags.  The  null  hypothesis  of  the  test  is  that  there  is  no  autocorrelation.  A p-value  greater  than  0.05  suggests  that  the  residuals  do  not  exhibit  significant  autocorrelation, implying that the model is well-specified.

The Ljung-Box Q-statistic is calculated as:

Where:

- is the sample autocorrelation at lag k, 𝑝 𝑘
- n is the number of observations,
- m is the maximum lag used for the test.

If  the  p-value  from  the  Ljung-Box  Q-test  is  greater  than  0.05,  we  fail  to  reject  the  null hypothesis, indicating that the residuals behave  like  white  noise  and  that  the  model  has appropriately captured the temporal dependencies.

## C. Visualization of Error Patterns

Visual  diagnostics  help  identify  where  and  why  forecast  precision  varies.  These  visuals complement statistical measures and provide intuitive insights into model performance

- Hourly  Heatmap - Reveals clusters of high forecast deviation by plotting residuals across time and hours of day.
- Boxplots  of  Residuals  by  Appliance  -  Compares  the  dispersion  of  residuals  across appliances.
- Temperature  vs.  Residual  Error  Scatter  Plots  -  Investigates  the  relationship  between temperature and forecast errors.

## 3.6 System Implementation

This  section  outlines  the  process  of  transforming  validated  per-appliance  forecasting outputs into user-facing features: hourly cost estimation, budget monitoring, and alerting. It defines the  necessary  data  inputs  and  outputs,  equations,  and  the  execution  flow  for  both  the  web dashboard and mobile notification system.

<!-- formula-not-decoded -->

## 3.6.1 Cost Estimation Methodology

## A. Inputs and Time Base

For  each  monitored  appliance,  hourly  energy  forecasts  are  generated  for  the  next  24 hours, which forms a rolling horizon of predictions. These forecasts are measured in kilowatt-hours (kWh) and provide estimates of energy consumption for each appliance on an hourly basis. The system uses monthly tariff rates for each month in the billing cycle, which are measured in pesos per kilowatt-hour ( ₱ /kWh). Each forecast hour is mapped to the applicable month, ensuring that the tariff rate is aligned with the specific month when the forecast is made.

## B. Hourly Cost Translation

For each appliance and hour, the cost of energy consumption is calculated by multiplying the  forecasted  energy  consumption  for  that  hour  by  the  applicable tariff rate for that month. The formula for the hourly cost of each appliance at each hour is given by:

<!-- formula-not-decoded -->

Once the hourly cost is calculated, the cumulative cost for the appliance is determined by summing the total costs from the previous hours up to the current hour. This provides a running total for the day. The cumulative cost for the day at a specific hour is expressed as:

<!-- formula-not-decoded -->

As new hourly data arrives, the system recalculates the cost for the next hour and updates the  cumulative  cost  for  the  appliance  accordingly.  For  instance,  when  new  data  for  hour t+1   is available,  the  system  computes  the  next-hour  forecast,  then  adds  the  new  hourly  cost  to  the cumulative total, ensuring that the forecast for the next 24 hours is always updated and available.

## C. Top-Consuming Appliances (Forecast Perspective)

To  identify  the  top-consuming  appliance  for  the  next  24  hours,  appliances are sorted by their  projected  cost  (or  energy  consumption)  contribution  over  the  upcoming  hours,  using  the cumulative  cost  calculated  earlier.  The  cumulative  cost  for  each  appliance  over  the  24-hour forecast  horizon  is  computed  by  summing  the  individual  hourly  costs  for  each  appliance,  as

explained  in  the  earlier  section.  This  cumulative  cost  represents  the  total  energy  cost  that each appliance will contribute over the next 24 hours.

Once  the  cumulative  cost  for  each  appliance  is  computed,  the  appliances  are  ranked based on their total forecasted cost contribution for the next 24 hours. The top 1 appliance with the highest cumulative cost is identified and displayed on the dashboard. The system can also display the ranked appliance by the share of total forecasted energy or cost contributed by each appliance over the next 24-hour period, reflecting the sum of the cumulative costs for each appliance.

## D. System Artifacts

The  system  generates  three  components  to  provide  users  with  comprehensive  energy consumption and cost insights: forecast outputs, a web-based dashboard, and mobile alerts.

## 1. Forecast Outputs

The system generates the following forecasting outputs:

- Hourly  Forecasts  -  These  include  energy consumption (in kWh) and cost (in ₱ ) for each appliance in the household.
- Next 24-Hour Totals - The system calculates the total projected energy consumption and cost for the next 24 hours.
- Top Appliances - Based on the forecasted energy consumption or cost, the system ranks the top-consuming appliances for the next 24 hours.

## 2. Web Dashboard

The system's web dashboard prototype displays the following information:

- Historical  vs. Forecasted Data - Users can compare past energy consumption (kWh) and costs ( ₱ ) with forecasts.
- 24-Hour  Forecast  Panels  -  These  panels  show  the  energy  consumption  and  cost projections for the next 24 hours.
- Budget  Status  -  A  budget  status  indicator  (OK,  At-risk,  Exceeded)  shows  whether  the household's energy or cost usage is within set limits.
- Top-Appliance Cards - The dashboard highlights the top appliances contributing to energy consumption and cost.

## 3. Mobile Alerts

The system also provides mobile notifications for daily updates:

- Daily Summary of Forecast - A summary of the forecasted energy consumption and costs for the next day (kWh, ₱ ) is sent to the user.
- Top-Consuming  Appliance  Alert  -  The  system  identifies and  notifies users of the top-consuming appliance for the next 24 hours, included in the daily summary
- Budget Alerts  -  If  the  system  detects  that  energy  consumption  or  costs  are  nearing  the user-defined budget limits, an alert is triggered.

## 3.6.2 Budget Threshold and Alert Engine

## A. Budget Constructs

The  system  supports  two  complementary  budget  views  to  help  users  manage  energy consumption and costs:

- Daily  Per-Appliance  Budget  -  Users  can  assign  a  specific  budget  (in ₱ or  kWh)  to  any monitored appliance based on forecasted and actual consumption.
- Rolling  24-Hour  Budget  -  The  same  budget  values  can  be  applied  to  a  rolling  24-hour period

The budget engine evaluates both the actual-to-date and forecast-to-go costs within the same day (or 24-hour window) to provide timely warnings about potential budget exceedances. For per-appliance  budgets,  the  engine  computes  costs  and  energy  consumption  separately for each appliance, isolating the costs for individual appliances.

## B. Status Logic

At any given forecast origin, the system computes:

- Forecast-to-go cost - This is the projected cost from time to the end of the day (or the next 24  hours).  This  value  is  based  purely  on  the  forecasted  energy  consumption  and applicable tariff rates.

The projected daily total is calculated by summing the forecasted costs for the remaining hours of the day or the next 24 hours:

<!-- formula-not-decoded -->

An optional caution margin can be applied (default is 90%) to trigger early warnings if the projected cost is approaching a predefined threshold:

Equation 58 𝑊𝑎𝑟𝑛𝑖𝑛𝑔 𝑇ℎ𝑟𝑒𝑠ℎ𝑜𝑙𝑑 = 𝑃𝑟𝑜𝑗𝑒𝑐𝑡𝑒𝑑 𝐷𝑎𝑖𝑙𝑦 𝑇𝑜𝑡𝑎𝑙  ×  𝐶𝑎𝑢𝑡𝑖𝑜𝑛 𝑀𝑎𝑟𝑔𝑖𝑛

In the daily summary, the engine surfaces the next-hour forecasted cost and highlights the top-consuming appliance for the upcoming 24-hour period.

## C. Alert Policies

The Alert Policies are designed to notify users about energy consumption thresholds and to ensure they are informed when their energy usage is approaching or exceeding the set limits.

## 1. Threshold Breach (Projected)

- Actual cost exceeds the user-defined daily budget - If the actual cost from the start of the day up to the current time has already surpassed the daily budget.

## 2. Early Warning

- An early warning is triggered when the status changes to At-risk for the first time during the day. This is a proactive alert to warn users that their energy consumption or cost is nearing critical levels, allowing them time to take action.

## 3. Quiet Hours and Summaries

- To respect users' time, notifications are paused during quiet hours. During this period, the system  will  not  send  alerts  unless  it's  urgent.  Instead,  a  daily  summary  is  sent  in  a user-specified time.

## D. Execution Schedule

The  system  operates  on  a  structured  execution  schedule  to  ensure  timely  forecasting, alerts, and updates:

## 1. Batch Cadence

- The system runs a daily batch process once a day, between 23:00 and 23:10 (UTC+8). During  this  time,  the  system  computes  the  forecasts  for the next day, specifically for the

time  range  [00:00,  23:00].  This  allows  the  system  to  project  the  upcoming  day's energy consumption and costs.

## 2. Data Dependencies

The system uses the following inputs for its calculations:

- The most recent, verified data on actual energy consumption.
- The most up-to-date forecasts based on the SARIMAX model
- The most recent tariff rates for accurate cost calculations.

The engine executes hourly for next-hour previews and runs a full daily batch process near 23:00 (UTC+8).

## 3.6.3 System Validation

To ensure the system's forecasting accuracy and reliability, a structured validation process is followed using the following steps:

## 1. Data Split and Protocol

The data is  divided  using  a  80%  training  /  20%  testing  chronological split. This ensures that  the  system  is  trained  on  historical  data  and  tested  on unseen future data. The rolling-origin protocol is applied to ensure that each forecast is tested against progressively newer data.

## 2. Procedure for Each Test Day

- On each test day, the deployed pipeline runs separately for each monitored appliance to generate the system's 24-hour forecasts for both energy consumption (kWh) and cost ( ₱ ).
- The  system's  forecasts  are  then  compared  against  actual  recorded  data  using  the following error metrics:
- ➔ MAE (Mean Absolute Error)
- ➔ RMSE (Root Mean Square Error)
- ➔ MAPE (Mean Absolute Percentage Error)
- ➔ R² (Coefficient of Determination)

## 3. Cost Output Verification

- The  resulting  cost  outputs  are  compared  against  a  re-computed  reference,  such  as  the Meralco  Appliance  Calculator,  with  the  requirement  that  any  differences  must  be  within

machine  precision  (numerical  parity  check),  ensuring  the  model's  cost  predictions  are accurate.

## 4. Alert Verification

- Ground-truth exceedance is defined by comparing actual accumulated cost with forecast-to-go cost values at each forecast origin.
- Alert precision and recall are measured:
- ➔ Precision is the proportion of alerts that correspond to true exceedances.
- ➔ Recall is the proportion of true exceedances that triggered an alert.

## 5. Acceptance Thresholds

The system is considered valid if it meets the following criteria during testing:

- MAPE  -  The  system's  MAPE  should  be  within  +0.2  percentage  points  of  the  validated offline SARIMAX model.
- Cost Parity  -  The  system  must  pass  the  cost  parity  check  for  100% of hours in the test period.
- Alert Precision - The alert precision should be ≥ 0.95.
- Alert Recall - The alert recall should be ≥ 0.90.

## 3.6.4 Prototype

The  system  prototype  consists  of  a  web-based  dashboard  and  a  mobile  notification interface,  both designed to present the forecasting outputs, cost estimation results, budget alerts, and  top-appliance  insights.  Figure  3.4  shows  the  sample  prototype  developed  during  system implementation.

Actual VS Forecast

30

20

11/012504.00

11101250300

12/01/2505.00

11/01/2506:00

Forecast Controls

Forecast Period

Tariff Rate

Budget

Add Appliance

DASHBOARD

&lt; November 1, 2025 &gt;

All-time

Filter

Electric Fan

Rice Cooker

## Previous VS Forecasted

<!-- image -->

1101/2507.00

1201/2508.00

1-hour to 24-hout

Aircon

Figure 3.5 Web-Based Dashboard of the Forecasting System

This  figure  integrates  outputs  from  the  SARIMAX  forecasting  engine,  tariff-based  cost calculator, and budget evaluation logic into a single interactive view. Each component is designed to  support  short-term  household  energy  awareness  and  decision-making  based  on  forecasted usage.

## A. Actual vs. Forecast Visualization Panel

The  dashboard  features  an  overlapping  line  chart  that  displays  appliance-level  energy consumption over time. This chart compares actual historical usage and forecasted values on an hourly  basis  for  the  selected  appliance.  Users may toggle between appliances (e.g., electric fan, rice cooker, television) using a filter control.

This  visualization  allows users to observe how closely the forecasted consumption aligns with observed usage trends and provides a clear view of projected energy behavior over the next 24 hours.

## B. Previous vs. Forecasted Usage Comparison

A bar chart summarizes and compares total energy consumption for two periods:

152

- the previous 24-hour usage, and
- the forecasted energy consumption for the next 24 hours.

This comparison enables users to quickly assess whether their expected energy usage is projected to  increase  or  decrease  relative  to  the  recent  past,  supporting  proactive  energy management.

## C. Forecast Controls Panel

The  dashboard  includes  a  forecast  control  section  that  allows  users  to  adjust  key parameters used in cost estimation and budget evaluation. These controls include:

- Forecast horizon selection (1 hour to 24 hours),
- Input of the applicable electricity tariff rate ( ₱ /kWh),
- User-defined daily or rolling budget value,
- Appliance selection and management.

These controls allow the  system  to  dynamically  update  forecast  summaries,  cost projections, and budget status indicators based on user input.

## D. Appliances Consumption Ranking

The  Appliances  Consumption  Ranking  panel  displays  an  ordered  list  of  monitored appliances  based  on  their  forecasted  energy  contribution  for  the  next  24  hours.  For  each appliance, the dashboard shows:

- Estimated energy consumption (kWh), and
- Corresponding projected cost ( ₱ ).

A total  forecasted  energy  and  cost  value  is  also  shown  at the bottom of the panel. This component  helps  users  identify  which  appliances  are  expected  to  contribute  most  to  upcoming energy usage and expenses.

E. Energy Forecast Summary and Budget Status

n, which is event-driven and generated dynamically when the projected en es or exceeds a predefined percentage of the user-defined daily budget. This r

an early warning to users, allowing them to take corrective action before an actu ce occurs.

The Energy Forecast Summary panel provides a concise overview of key forecast metrics, including:

Budget Warning!

- Total forecasted energy consumption and cost for the next 24 hours,
- Energy usage and cost from the previous 24-hour period,
- Actual recorded usage and cost for the most recent day,
- Identification of the top-consuming appliance,
- Current budget status indicator

This summary allows users to quickly interpret their projected energy situation and budget standing without navigating through detailed charts.

## F. Mobile Notification

The  prototype  includes  two  types  of  mobile  notification  previews  that  demonstrate  how forecast  insights  and  budget-related  alerts are communicated to users. The first type is the Daily Forecast  Summary  Notification,  which  presents  the  same  forecasted  energy  consumption,  cost estimates,  top-consuming  appliance,  and  budget  status  shown  on  the  web  dashboard,  but  in  a simplified  mobile-friendly  format.  Meanwhile,  the  second  type  is  the  Budget  Threshold  Warning Notification,  which  is  event-driven  and  generated  dynamically  when  the  projected  energy  cost approaches or exceeds a predefined percentage of the user-defined daily budget. This notification provides an early warning to users, allowing them to take corrective action before an actual budget exceedance occurs.

Figure 3.6. Budget Threshold Warning Mobile Notification

## CHAPTER IV RESULTS AND DISCUSSION

## 4.1 Dataset Gathering of Real Monitored Data

The following sections present the characteristics of the collected real dataset and the generated synthetic dataset, as well as statistical and visual analyses used to validate the realism of the generated data.

## 4.1.1 Overview of Generated Synthetic Dataset

The  real  appliance-level  electricity  consumption  data  used  in  this  study  were  collected using  smart  plug  devices  installed  on  selected  household  appliances.  Data  collection  began  on January  3,  2026,  and  continued  until  March  7,  2026,  resulting  in  approximately  two  months  of monitored appliance energy data.

The smart plugs recorded measurements at 10-minute intervals, capturing the electrical characteristics of the connected appliances throughout the monitoring period. These measurements were transmitted to the data storage system and later processed to obtain cleaned and structured datasets suitable for analysis.

Three household appliances were monitored in this study:

- Air Conditioner
- Electric Fan
- Refrigerator

Each  appliance  generated  a  continuous  time  series  of  energy-related  measurements throughout the monitoring period.

## CHAPTER V CONCLUSION

## References

- A novel WD-SARIMAX model for temperature forecasting using daily Delhi climate dataset. Applied Sciences, 15(5), 2542. https://doi.org/10.3390/app15052542
- A  systematic  review  of  building  energy  consumption  prediction:  From  perspectives  of  load classification,  data-driven  frameworks,  and  future  directions.  Applied  Sciences,  15(6), 3086. https://doi.org/10.3390/app15063086
- Aguirre-Fraire,  B.,  Beltrán,  J.,  &amp;  Soto-Mendoza,  V.  (2024).  A  comprehensive  dataset  integrating household energy consumption and weather conditions in a north-eastern Mexican urban city. Data in Brief, 54, Article 110234. https://doi.org/10.1016/j.dib.2024.110234
- Ahmed, M. A., Chavez, S. A., Eltamaly, A. M., Garces, H. O., Rojas, A. J., &amp; Kim, Y.-C. (2022). Toward  an  intelligent  campus:  IoT  platform  for  remote  monitoring  and  control  of  smart buildings. Sensors, 22(23), 9045. https://doi.org/10.3390/s22239045
- Ampountolas,  A.  (2021).  Modeling  and  forecasting  daily  hotel  demand:  A  comparison  based  on SARIMAX, neural networks, and GARCH models. Forecasting, 3(3), 479-493. https://doi.org/10.3390/forecast3030037
- Arvanitidis, A. I., &amp; Bargiotas, D. (2022). Improved data preprocessing approach to short-term load forecasting. Proceedings of the International Conference on Energy. https://personales.upv.es/thinkmind/dl/conferences/energy/energy\_2022/energy\_2022\_1\_2 0\_30012.pdf
- Asre,  S.,  &amp;  Anwar,  A.  (2022).  Synthetic  energy  data  generation  using  time  variant  generative adversarial network. Electronics, 11(3), 355. https://doi.org/10.3390/electronics11030355
- Athanasoulias,  S.  (2025). Edge-optimized deep learning and pattern recognition for smart energy management in households. IEEE Access, 13, 76434-76447. https://arxiv.org/pdf/2505.06289
- Athanasoulias,  S.,  Guasselli,  F.,  Doulamis,  N.,  &amp;  others.  (2024).  The  Plegma  dataset:  Domestic appliance-level  and  aggregate  electricity  demand  with  metadata  from  Greece.  Scientific Data, 11, Article 65. Nature Portfolio. https://doi.org/10.1038/s41597-024-03162-3
- Azad, M. I.,  Rajabi,  R.,  &amp;  Estebsari,  A.  (2023). Non-intrusive load monitoring (NILM) using deep neural networks: A review. arXiv Preprint arXiv:2306.05017. https://doi.org/10.48550/arXiv.2306.05017

- Baidoo,  A.  N.  A.,  Danquah,  J.  A.,  Nunoo,  E.  K.,  Mariwah,  S.,  Boampong,  G.  N.,  Twum,  E., Amankwah, E., &amp; Nyametso, J. K. (2023). Households' energy conservation and efficiency awareness practices in the Cape Coast Metropolis of Ghana. Discover Sustainability, 4(1), 1-13. https://doi.org/10.1007/s43621-023-00154-6
- Bertheau,  P.  (2024). Assessing  the  impact  of  renewable  energy  on  local  development  and  the Sustainable  Development Goals: Insights from a small Philippine island. Reiner Lemoine Institute. Retrieved from https://reiner-lemoine-institut.de/wp-content/uploads/2024/09/Assessing-the-impact-of-rene wable-energy-on-local-development-and-the-Sustainable-Development-Goals.pdf
- Botman,  L.,  Lago,  J.,  Fu,  X.,  et  al.  (2024).  Building  plug  load  mode  detection,  forecasting  and scheduling. Energy and Buildings, 302, Article 113971. https://doi.org/10.1016/j.enbuild.2024.113971
- Bramm,  A.,  Eroshenko,  S.,  &amp;  Khalyasmaa,  A.  (2021).  Effect  of  data  preprocessing  on  the forecasting  accuracy  of  solar  power  plant.  2021  International  Conference  on  Industrial Engineering, Applications and Manufacturing (ICIEAM). https://doi.org/10.1109/ICIEAM51299.2021.9462288
- Burg,  L.,  Gürses-Tran,  G.,  Madlener,  R.,  &amp;  Monti,  A.  (2021).  Comparative  analysis  of  load forecasting  models for varying time horizons and load aggregation levels. RWTH Aachen University Publications. https://d-nb.info/1248603192/34
- Cecílio,  J.,  Rodrigues,  T.,  Barros,  M.,  &amp;  de  Sá,  A.  O.  (2025). Leveraging sustainable household energy  and  environment  resources  management  with  time-series  forecasting. Scientific Data, 12, 136. https://doi.org/10.1038/s41597-025-04750-
- Chen,  Z.,  Pang,  Y.,  Jin,  S.,  Qin,  J.,  Li,  S.,  &amp;  Yang,  H.  (2024).  DLT-GAN:  Dual-layer  transfer generative adversarial network-based time series data augmentation method. Electronics, 13(22), 4514. https://doi.org/10.3390/electronics13224514
- Chen, G., Lu, S.,  Zhou,  S.,  Tian,  Z., Kim, M. K., Liu, J., &amp; Liu, X. (2025). A systematic review of building energy consumption prediction: From perspectives of load classification, data-driven frameworks, and future directions. Applied Sciences, 15(6), 3086. https://doi.org/10.3390/app15063086

- Chen, S.,  Zhang,  Y.,  Ma,  X.,  Yang,  X.,  Shi, J., &amp; Ji, H. (2025). A comparative study of electricity sales  forecasting  models  based  on  different  feature  decomposition  methods.  Energies, 18(20), 5352. https://doi.org/10.3390/en18205352
- Chicco,  G.  (2021).  Data  consistency  for data-driven smart energy assessment. Energies, 14(11), 3328. https://pmc.ncbi.nlm.nih.gov/articles/PMC8155608/
- Condon,  F.,  Martínez,  J.  M.,  Eltamaly,  A.  M.,  Kim,  Y.-C.,  &amp;  Ahmed,  M.  A.  (2023).  Design  and implementation of a cloud-IoT-based home energy management system (HEMS). Sensors, 23(1), 176. https://doi.org/10.3390/s23010176
- Dhaou, I. B. (2023). Design and implementation of an Internet-of-Things-enabled smart meter and smart plug for home-energy-management system. Electronics, 12(19), 4041. https://doi.org/10.3390/electronics12194041
- Dutta, P. K., El-kenawy, E. M., Guma, A., &amp; Dhoska, K. (2023). An energy consumption monitoring and control system in buildings using Internet of Things. Babylonian Journal of Internet of Things, 2023(June), 38-47. https://doi.org/10.58496/BJIoT/2023/006
- Eirinaki, M., Varlamis, I., Dahihande, J., Jaiswal, A., Pagar, A. A., &amp; Thakare, A. (2022). Real-time recommendations  for  energy-efficient  appliance  usage  in  households.  Frontiers  in  Big Data, 5, Article 972206. https://doi.org/10.3389/fdata.2022.972206
- GlobalPetrolPrices.com. (2025). Philippines electricity prices, March  2025 . Retrieved from https://www.globalpetrolprices.com/Philippines/electricity\_prices/
- Hadri, S., Najib, M., Bakhouya, M., Fakhri, Y., &amp; El Arroussi, M. (2021). Performance evaluation of forecasting  strategies  for  electricity  consumption  in  buildings.  Energies,  14(18),  5831. https://doi.org/10.3390/en14185831
- Hernandez,  J.  C.,  Sanchez-Sutil,  F.,  Cano-Ortega,  A.,  &amp;  Baier,  C.  R.  (2020).  Influence  of  data sampling  frequency  on  household  consumption  load  profile  features:  A  case  study  in Spain. Sensors, 20(21), 6034. https://doi.org/10.3390/s20216034
- Hernández, Á., Nieto, R., Pizarro, D., Fuentes, D., de Diego-Otón, L., Villadangos-Carrizo, J. M., &amp; Pérez-Rubio, M. C. (2020). Monitoring  daily  activities in households by means of energy consumption measurements from smart meters. Applied Sciences, 10(9), 3070. www.mdpi.com/2224-2708/14/2/25

- Ibrahim,  B.,  Rabelo,  L.,  Gutierrez-Franco,  E.,  &amp;  Clavijo-Buritica,  N.  (2022).  Machine  learning for short-term load forecasting in smart grids. Energy Reports, 8, 897-909. https://doi.org/10.1016/j.egyr.2022.01.043
- Kaselimi,  M.,  Protopapadakis,  E.,  Vouldis,  A.,  Doulamis,  N.,  &amp;  Doulamis,  A.  (2022).  Towards trustworthy  energy  disaggregation: A review of challenges, methods and perspectives for non-intrusive load monitoring. IEEE Access, 10, 16853-16881. https://arxiv.org/pdf/2207.02009
- Kasaraneni, P.  P.,  &amp;  Yellapragada,  V.  P.  K.  (2022).  Analytical  approach  to  exploring  the missing data  behavior  in smart home energy consumption dataset. Journal of Renewable Energy and Environment (JREE). https://www.jree.ir
- Khan, H. R., Kazmi, M., Lubaba, Khalid, M. H. B., Alam, U., Arshad, K., Assaleh, K., &amp; Qazi, S. A. (2024). A  low-cost  energy  monitoring  system  with  universal  compatibility  and  real-time visualization  for  enhanced  accessibility  and  power  savings. Sustainability,  16(10),  4137. https://doi.org/10.3390/su16104137
- Kienhuis, M. A. A. (2023). Partial hierarchy appliance modelling in household energy consumption: Utilizing ARMA-based methods to improve the prediction of household energy consumption  (Bachelor's  thesis, Delft University of Technology).  Delft  University  of Technology. https://resolver.tudelft.nl/uuid:da0e7461-3263-4397-8aa0-30828d5ad65d
- Liu, G., Liu, J., Bai, Y., et al. (2023). EWELD: A large-scale industrial and commercial load dataset in extreme weather events. Scientific Data, 10, Article 735. https://doi.org/10.1038/s41597-023-02409-y
- Ma,  P.,  Cui,  S.,  Chen,  M.,  Zhou,  S.,  &amp;  Wang,  K.  (2023).  Review  of  family-level  short-term  load forecasting  and  its  application  in  household  energy  management  system.  Energies, 16(15), 5809. https://doi.org/10.3390/en16155809
- Magtibay,  O.  B.  M.,  Cabrera, R. H., Roxas, J. P., &amp; De Vera, M. A. (2021). Green switch: An IoT based  energy  monitoring  system  for  Mabini  building  in  De  La  Salle  Lipa. Indonesian Journal of Electrical Engineering and Computer Science, 24(2), 754-761. https://doi.org/10.11591/ijeecs.v24.i2.pp754-761
- Moritz,  W.,  Turowski,  M.,  Çakmak,  H.  K.,  Mikut,  R.,  Kühnapfel,  U.,  &amp;  Hagenmeyer,  V.  (2021). Data-driven copy-paste imputation for energy time series. arXiv preprint arXiv:2101.01423. https://arxiv.org/abs/2101.01423

- Mystakidis, A., Koukaras, P., Tsalikidis, N., Ioannidis, D., &amp; Tjortjis, C. (2024). Energy forecasting: A comprehensive review of techniques and technologies. Energies, 17(7), 1662. https://doi.org/10.3390/en17071662
- Neumann,  O.,  Turowski,  M.,  &amp;  Mikut,  R.  (2023).  Using  weather  data  in  energy  time  series forecasting:  The  benefit  of  input  data  transformations.  Energy  Informatics,  6,  Article  6. https://doi.org/10.1186/s42162-023-00299-8
- Pagaduan,  L.  J.  L.,  Portolazo,  J.  G.,  Delfin,  J.  X.  D.,  Estanda,  M.  B.  O.,  &amp;  Dela  Cruz,  J.  P .  O. (2023). The development of real-time energy consumption monitoring using IoT. Advanced Computational Intelligence: An International Journal, 10(1/2/3), 18-28. https://www.researchgate.net/publication/372104604\_The\_Development\_of\_Real-Time\_E nergy\_Consumption\_Monitoring\_using\_IoT
- Partial  hierarchy  appliance  modelling  in  household  energy  consumption:  Utilizing  ARMA-based methods to improve the prediction of household energy consumption. [Bachelor's thesis, Delft University of Technology]. TU Delft Repository. https://repository.tudelft.nl/
- Performance evaluation of forecasting strategies for electricity consumption in buildings. Energies, 14(18), 5831. https://doi.org/10.3390/en14185831
- Petralia,  A.,  Charpentier,  P.,  Boniol,  P.,  &amp;  Palpanas,  T.  (2023).  Appliance  detection  using  very low-frequency smart meter time series. arXiv preprint arXiv:2305.10352. https://arxiv.org/abs/2305.10352
- Petralia,  A.,  Charpentier,  P.,  Boniol,  P.,  &amp;  Palpanas,  T.  (2023).  Appliance  detection  using  very low-frequency smart meter time series. arXiv preprint arXiv:2305.10352. https://arxiv.org/abs/2305.10352
- Philippine  Statistics  Authority.  (2023).  2020  Census  of  Population  and  Housing  (2020  CPH): Household Population, Number of Households, and Average Household Size. https://psa.gov.ph/statistics/population-and-housing/node/166426
- Respicio  &amp;  Co.  (2023). High charges on submeter usage in the Philippines: Legal concerns and remedies. Lawyer-Philippines.com.

https://www.lawyer-philippines.com/articles/high-charges-on-submeter-usage-in-the-philipp ines-legal-concerns-and-remedies

- Respicio  &amp;  Co.  (2024). Electric  submeter  billing  in the Philippines: Legal framework, issues, and remedies. Lawyer-Philippines.com.

https://www.lawyer-philippines.com/articles/electric-submeter-billing-issues

- Review  of  family-level short-term  load  forecasting  and  its  application  in  household  energy management system. Energies, 16(15), 5809. https://doi.org/10.3390/en16155809
- Richardson,  D.,  Black,  A.  S.,  &amp;  Irving,  D.  (2022).  Global  increase  in  wildfire  potential  from compound fire weather and drought. Nature Communications, 13, Article 3417. https://doi.org/10.1038/s41467-022-34170-4
- Rubattua,  N.,  Maronia,  G.,  &amp;  Corania,  G.  (2023).  Electricity  load  and  peak  forecasting:  Feature engineering, probabilistic LightGBM  and  temporal  hierarchies.  Applied  Energy,  341, 120997. https://doi.org/10.1016/j.apenergy.2023.120997
- Santos,  A.  G.  (2021).Forecasting  residential  electricity  demand  in  the  Philippines  using  an error correction model. Philippine Review of Economics, 58(2), 45-68. https://www.pre.econ.upd.edu.ph/index.php/pre/article/viewFile/996/900
- Santos,  A.,  Duggan,  G.  P.,  Davis,  J.,  &amp;  Zimmerle,  D.  (2023).  A  cautionary  note  on  using  smart plugs for research data acquisition. Energy Reports, 9, 287-296. https://doi.org/10.1016/j.egyr.2023.04.042
- Schaffer, M., Tvedebrink, T., &amp; Marszal-Pomianowska, A. (2022). Three years of hourly data from 3021 smart heat meters installed in Danish residential buildings. Scientific Data, 9, Article 358. https://pmc.ncbi.nlm.nih.gov/articles/PMC9296640/
- Shadkam, A. (2020). Using SARIMAX to forecast electricity demand and consumption in university buildings [Master's thesis, The University of  British  Columbia].  UBC  Theses  and Dissertations.

https://open.library.ubc.ca/soa/cIRcle/collections/ubctheses/24/items/1.0395042

- Tang,  C.,  Li,  Y .,  &amp;  Tan,  X.  (2025).  Time  series  data  augmentation  for  energy  consumption  data based on improved TimeGAN. Sensors, 25(2), 493. https://www.mdpi.com/1424-8220/25/2/493
- Tang,  P.,  Li,  Z.,  Wang,  X.,  Liu,  X.,  &amp;  Mou,  P .  (2025).  Time  series  data  augmentation  for energy consumption data based on improved TimeGAN. Sensors, 25(2), 493. https://doi.org/10.3390/s25020493

- Ünal, F., Almalaq, A., &amp; Ekici, S. (2021). A novel load forecasting approach based on smart meter data  using  advanced  preprocessing  and  hybrid  deep  learning.  Applied  Sciences,  11(6), 2742. https://doi.org/10.3390/app11062742
- Vivar,  D.  V.  (2025). Survey  implementation  of  2023  Household  Energy  Consumption  Survey (HECS): IEA demand side data and energy efficiency indicators workshop for Southeast Asia. Department  of  Energy  -  Philippines,  Policy  Formulation  and  Research  Division (PFRD), Energy Policy and Planning Bureau (EPPB). https://iea.blob.core.windows.net/assets/f0dca78d-a348-49e2-af4a-8213a41eef13/202506 10\_Philippines\_IEAPresentationHECS\_IEAWorkshop\_final.pdf
- Wang, Z.-X., Wang, Z.-W., &amp; Li, Q. (2020). Forecasting the industrial  solar  energy  consumption using a novel seasonal GM(1,1) model with dynamic seasonal adjustment factors. Energy, 200 , 117460. https://doi.org/10.1016/j.energy.2020.117460
- Yilmaz, B., &amp;  Korn, R. (2022).  Synthetic  demand  data  generation  for  individual  electricity consumers: Generative adversarial networks (GANs). Energy and AI, 9,  100161. https://doi.org/10.1016/j.egyai.2022.100161
- Zhang, Y., Wang, J., Yin, Z., Shao, Y., Kang, J., &amp; Ma, Z. (2025). Mitigation imbalance distribution: Data  augmentation  of  local  small  sample  for  building  electricity  load  in  time-series generative adversarial network. Journal of Building Engineering, 99, 115149. https://www.sciencedirect.com/science/article/pii/S2352710224031176