# Data dictionary and design notes

**Dataset status:** All rows are synthetic and generated for learning. The distribution shapes are designed to be realistic-style, not to represent measured real-world frequencies. Do not describe them as actual insurer data.

## Telematics claims

| Column | Type | Meaning | Notes |
|---|---|---|---|
| ClaimID | string | Unique synthetic claim identifier | Unique; primary key |
| AccidentDate | datetime | Simulated incident timestamp, 2023-2025 | Varies across weekdays/hours |
| VehicleID | string | Synthetic vehicle identifier; a small subset repeats across claims | Not unique by design |
| Vehicle_Brand | category | Vehicle manufacturer / make | Uneven make distribution |
| Model_Year | integer | Vehicle model year, no later than incident year | Older vehicles are less common |
| Speed_At_Impact_kmh | float | Simulated impact speed in km/h | Most incidents lower-speed; severe impacts rarer |
| G_Force_Impact | float | Simulated peak impact acceleration, expressed in g | Positively related to speed with noise |
| Airbag_Deployed | integer | 1 if simulated airbag deployment, else 0 | Probability increases with impact severity |
| Braking_Duration_Seconds | float | Simulated pre-impact braking duration | Many zero/short values; right-skewed positive values |
| Impact_Point | category | Primary impact zone: Front, Rear or Side | Uneven category frequencies |
| Weather_Condition | category | Simulated weather at incident | Clear dominates; rain/fog less common |
| Road_Type | category | Simulated road class | Uneven category frequencies |
| Crash_Area | category | Simulated Delhi NCR city cluster | Uneven city distribution |
| Vehicle_Latitude | float | Generated latitude for simulated crash location | Approximate cluster around city center |
| Vehicle_Longitude | float | Generated longitude for simulated crash location | Approximate cluster around city center |
| Actual_Repair_Cost_INR | integer | Simulated repair cost used as regression target | Right-skewed and correlated with impact, airbag and make |

## Partner garages

| Column | Type | Meaning | Notes |
|---|---|---|---|
| GarageID | string | Unique synthetic garage identifier | Primary key |
| Garage_Name | string | Fictional garage name | Not a real business |
| Area | category | Simulated Delhi NCR area cluster | Uneven city distribution |
| Latitude | float | Generated garage latitude | Synthetic coordinates |
| Longitude | float | Generated garage longitude | Synthetic coordinates |
| Brand_Specialization | category | Primary brand specialization | Uneven by brand; at least three facilities per make |
| Parts_Available | boolean | Simulated snapshot flag for relevant parts in stock | Availability probability varies by make |
| Preferred_Partner | boolean | Simulated preferred-network indicator | Not equally distributed |
| Daily_Service_Capacity | integer | Approximate simulated repair intake capacity/day | Skewed, bounded |
| Avg_Repair_Turnaround_Days | float | Simulated average repair turnaround estimate | Variable across facilities |
| Labor_Rate_INR_Per_Hour | integer | Simulated labor charge per hour | Varies by area and facility |

## Design choices to avoid artificial balance

- Vehicle make share is weighted toward common mass-market brands; premium brands are rare.
- Crash severities are imbalanced: lower-impact collisions are common and very severe impacts are rare.
- Airbag deployment probability increases with speed, g-force, and collision zone, with stochastic variation.
- Repair costs use a heavy-tailed multiplicative-noise model and respond to impact speed, g-force, airbag deployment, impact zone, vehicle age, weather, and brand cost multiplier.
- Crash and garage locations cluster unevenly around Delhi NCR area centroids; coordinates are simulated.
- Garage part availability depends on specialization and is not 50/50 for all brands. At least one eligible garage is retained for each brand to support routing exercises.
- No fixed 50/50 target labels are provided because this dataset is for cost regression and routing, not fraud classification.
