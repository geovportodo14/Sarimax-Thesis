# **1\. Overall visual workflow**

```
Historical Appliance Data
        │
        ▼
SARIMAX Forecasting
(24-hour appliance energy prediction)
        │
        ▼
Forecasted Hourly Energy
Aircon / Fan / Refrigerator
        │
        ▼
Convert Energy → Cost
        │
        ▼
User Inputs Budget
        │
        ▼
MILP Optimization
        │
        ▼
Recommended Appliance Schedule
```

Example output:

```
Hour     Aircon   Fan   Refrigerator
-------------------------------------
12 AM      ON     OFF        ON
1 AM       ON     OFF        ON
2 AM       OFF    OFF        ON
3 AM       OFF    OFF        ON
...
8 PM       ON     ON         ON
```

The optimizer determines **when appliances should run**.

---

# **2\. What MILP is doing internally (visual idea)**

MILP is basically **trying many possible appliance schedules and choosing the best one.**

Example schedule possibilities:

### **Schedule A (normal forecast)**

```
Aircon hours:        8
Fan hours:           10
Refrigerator:        always

Total cost = 185 PHP
Budget = 150 PHP
❌ exceeds budget
```

---

### **Schedule B (slightly adjusted)**

```
Aircon hours:        6
Fan hours:           10
Refrigerator:        always

Total cost = 160 PHP
Budget = 150 PHP
❌ still exceeds
```

---

### **Schedule C (optimized)**

```
Aircon hours:        5
Fan hours:           9
Refrigerator:        always

Total cost = 148 PHP
Budget = 150 PHP
✅ within budget
```

MILP finds **the schedule closest to normal usage while staying under budget.**

---

# **3\. Hourly scheduling visualization**

Imagine a **24-hour timeline**.

### **Forecasted usage**

```
Hour →  0 1 2 3 4 5 6 7 8 9 10 11 12 ... 23

Aircon:
      █ █ █ █ █ █ █ █

Fan:
            █ █ █ █ █ █ █ █+

Refrigerator:
      █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █
```

That gives the **forecasted cost**.

---

### **After MILP optimization**

The system **removes or shifts some appliance hours**.

```
Aircon:
      █ █ █ █ █

Fan:
          █ █ █ █ █ █

Refrigerator:
      █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █
```

Now the total cost fits the **budget constraint**.

---

# **4\. MILP mathematical idea (simple)**

The optimizer controls **binary decisions**.

Example variable:

```
x_aircon,t = 1 if aircon is ON at hour t
x_aircon,t = 0 if OFF
```

Same for fan.

Example for hour 3:

```
x_aircon,3 = 1
x_fan,3 = 0
```

---

## **Energy used per hour**

```
Energy_aircon,t = forecast_energy_aircon,t × x_aircon,t
```

If aircon is OFF → energy becomes **0**.

---

## **Total cost**

```
Total Cost =
Σ (energy_aircon × rate)
+ Σ (energy_fan × rate)
+ Σ (energy_refrigerator × rate)
```

---

## **Budget constraint**

```
Total Cost ≤ User Budget
```

The optimizer searches for values of:

```
x_aircon,t
x_fan,t
```

that satisfy the constraint.

---

# **5\. Visual optimization idea**

Imagine a **cost meter**.

### **Before optimization**

```
Forecasted Cost
185 PHP

Budget
150 PHP

Over budget
+35 PHP
```

---

### **Optimization adjustment**

```
Reduce Aircon usage
Reduce Fan usage
Keep Refrigerator constant
```

---

### **After optimization**

```
Optimized Cost
148 PHP

Budget
150 PHP

Within budget
```

---

# **6\. Visual algorithm intuition**

MILP explores **combinations of appliance schedules**.

Example:

```
Try schedule 1 → cost too high
Try schedule 2 → cost too high
Try schedule 3 → within budget
Try schedule 4 → lower comfort
Try schedule 5 → best feasible
```

Then it selects the **optimal schedule**.

---

# **7\. What your system finally shows to the user**

Example output:

```
Forecasted cost: 185 PHP
User budget: 150 PHP

Recommended schedule:

Aircon
1 PM – 4 PM
9 PM – 11 PM

Electric Fan
10 AM – 6 PM

Refrigerator
Continuous operation
```

Expected cost:

```
148 PHP
```

Savings:

```
37 PHP
```

---

# **8\. Diagram you can put in your thesis**

```
              Historical Appliance Data
                        │
                        ▼
                 SARIMAX Forecast
                (24-hour energy)
                        │
                        ▼
                Energy → Cost Model
                        │
                        ▼
                 User Budget Input
                        │
                        ▼
            MILP Appliance Scheduler
                        │
                        ▼
        Optimized Appliance Usage Plan
```

---

