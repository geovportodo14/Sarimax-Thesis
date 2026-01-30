# System Analysis & Design Evaluation

## 1. User Workflow Analysis
The system follows a linear yet cyclic workflow designed to empower users with actionable energy insights.

### 1.1 Onboarding & Configuration
- **Initial Setup**: User defines household baseline (current budget, tariff rates).
- **Tour**: A minimal, obscure-capable guided tour introduces key UI elements without blocking the verified workflow.

### 1.2 Monitoring Loop
- **Data Ingestion**: System receives real-time consumption data (kWh) from sensors.
- **Visualization**: Data is presented in the "Actual vs Forecast" chart. Red indicators trigger immediately if actual consumption deviates significantly from the model's safe range.

### 1.3 Forecasting & analysis
- **SARIMAX Model**: The core engine processes historical data to predict future usage.
- **Insight Generation**: The dashboard translates raw numbers into semantic status:
    - *Efficient Usage (<80% of budget)*
    - *Approaching Limit (80-100%)*
    - *Budget Exceeded (>100%)*
- **Drill-down**: Users observe "Risk Drivers" to see which appliances (e.g., Air Conditioner) are contributing most to the variance.

### 1.4 Action & Feedback
- User adjusts usage behaviors based on "Critical" alerts.
- System reflects these changes in the next update cycle, completing the feedback loop.

## 2. Data Validation & Integrity
To ensure academic rigor and system reliability, the following safeguards are implemented:

### 2.1 Input Validation (Client-Side)
- **Type Checking**: Numeric inputs (Budget, Tariff) are strictly validated to prevent `NaN` propagation into the SARIMAX model.
- **Range Constraints**: Settings prevent negative values for costs or consumption.

### 2.2 Data Integrity (Storage & Transmission)
- **Firestore Schema**: Data is structured in a strict `deviceId -> timestamp -> metrics` hierarchy.
- **Normalization**: Raw sensor data passes through a normalization layer (e.g., `solis_normalizer.py`) to standardize units (Watts to kW) and handle missing packets before storage.

## 3. Use Case Scenarios

### Scenario A: The "Summer Peak"
*Context*: High temperatures leading to increased AC usage.
- **User Action**: Checks dashboard mid-month.
- **System Response**: Status badge reads "Approaching Limit" (Amber). Forecast chart shows a steep upward trend.
- **Insight**: "Top: Air Conditioner" is highlighted.
- **Result**: User adjusts thermostat, bringing the projected end-of-month cost back within budget.

### Scenario B: Anomalous Drain
*Context*: A faulty refrigerator compressor running 24/7.
- **User Action**: Receives a notification or checks summary.
- **System Response**: "Forecast Usage" is abnormally high despite normal behavior.
- **Insight**: "35% increase vs previous period".
- **Result**: User detects the anomaly early, preventing a massive bill shock.

## 4. Marketability & Academic Significance

### 4.1 Value Proposition
Unlike traditional "dumb" meters that only show current usage, this system provides **predictive financial control**. It shifts the mental model from *reactive* ("How much did I spend?") to *proactive* ("How much *will* I spend?").

### 4.2 Academic Contribution
The integration of a SARIMAX statistical model into a consumer-friendly React interface demonstrates a practical application of complex time-series forecasting. The logical color system and contextual status indicators bridge the gap between academic data science and accessible UX design.

### 4.3 Target Market
- **Residential**: Homeowners with solar installations or tight budgets.
- **Small Business**: Cafes/Offices needing to manage overheads.
