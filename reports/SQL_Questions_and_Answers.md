# SQL Questions and Executed Answers

**Executed:** 55/55 questions passed on the current dataset.

SQL result CSVs are in `reports/sql_results/`. This is simulated portfolio data, so interpret patterns as demonstrations, not real insurer findings.

## Q01. What is the overall claims portfolio?

**Category:** Portfolio overview  
**Business value:** Establish the overall volume and cost baseline.

```sql
SELECT COUNT(*) AS claim_count, COUNT(DISTINCT VehicleID) AS distinct_vehicles, ROUND(SUM(Actual_Repair_Cost_INR), 2) AS total_repair_cost_inr, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS average_repair_cost_inr, MIN(AccidentDate) AS first_accident, MAX(AccidentDate) AS last_accident FROM telematics_claims;
```

**Result:** 1 row(s) returned. Preview:
| claim_count | distinct_vehicles | total_repair_cost_inr | average_repair_cost_inr | first_accident | last_accident |
| --- | --- | --- | --- | --- | --- |
| 3000 | 2885 | 53783500.0 | 17927.83 | 2023-01-03 08:05:00 | 2025-12-31 19:14:00 |

## Q02. How many repeat-incident vehicles are present?

**Category:** Portfolio overview  
**Business value:** Understand repeat vehicle incidents; repeats are not inherently suspicious.

```sql
SELECT COUNT(*) AS vehicles_with_multiple_claims FROM (SELECT VehicleID FROM telematics_claims GROUP BY VehicleID HAVING COUNT(*) > 1);
```

**Result:** 1 row(s) returned. Preview:
| vehicles_with_multiple_claims |
| --- |
| 51 |

## Q03. Which brands account for the most claims?

**Category:** Vehicle brand  
**Business value:** Understand portfolio mix and avoid treating raw volume as risk rate.

```sql
SELECT Vehicle_Brand, COUNT(*) AS claim_count, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM telematics_claims), 2) AS claim_share_pct FROM telematics_claims GROUP BY Vehicle_Brand ORDER BY claim_count DESC;
```

**Result:** 12 row(s) returned. Preview:
| Vehicle_Brand | claim_count | claim_share_pct |
| --- | --- | --- |
| Maruti Suzuki | 804 | 26.8 |
| Hyundai | 588 | 19.6 |
| Tata | 421 | 14.03 |
| Mahindra | 323 | 10.77 |
| Honda | 278 | 9.27 |
| Kia | 203 | 6.77 |
| Toyota | 153 | 5.1 |
| Renault | 79 | 2.63 |

## Q04. Which brands have the highest average repair cost?

**Category:** Vehicle brand  
**Business value:** Compare claim severity across manufacturers.

```sql
SELECT Vehicle_Brand, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr, ROUND(SUM(Actual_Repair_Cost_INR), 2) AS total_cost_inr FROM telematics_claims GROUP BY Vehicle_Brand HAVING COUNT(*) >= 20 ORDER BY avg_cost_inr DESC;
```

**Result:** 12 row(s) returned. Preview:
| Vehicle_Brand | claim_count | avg_cost_inr | total_cost_inr |
| --- | --- | --- | --- |
| Mercedes-Benz | 22 | 54350.0 | 1195700.0 |
| BMW | 23 | 27347.83 | 629000.0 |
| Skoda | 35 | 25648.57 | 897700.0 |
| Volkswagen | 71 | 23945.07 | 1700100.0 |
| Kia | 203 | 20340.39 | 4129100.0 |
| Tata | 421 | 19952.49 | 8400000.0 |
| Mahindra | 323 | 19768.11 | 6385100.0 |
| Hyundai | 588 | 18563.61 | 10915400.0 |

## Q05. What share of total repair spend comes from each brand?

**Category:** Vehicle brand  
**Business value:** Find where the largest absolute financial exposure sits.

```sql
SELECT Vehicle_Brand, ROUND(SUM(Actual_Repair_Cost_INR), 2) AS total_cost_inr, ROUND(100.0 * SUM(Actual_Repair_Cost_INR) / (SELECT SUM(Actual_Repair_Cost_INR) FROM telematics_claims), 2) AS cost_share_pct FROM telematics_claims GROUP BY Vehicle_Brand ORDER BY total_cost_inr DESC;
```

**Result:** 12 row(s) returned. Preview:
| Vehicle_Brand | total_cost_inr | cost_share_pct |
| --- | --- | --- |
| Maruti Suzuki | 11210100.0 | 20.84 |
| Hyundai | 10915400.0 | 20.3 |
| Tata | 8400000.0 | 15.62 |
| Mahindra | 6385100.0 | 11.87 |
| Honda | 4314600.0 | 8.02 |
| Kia | 4129100.0 | 7.68 |
| Toyota | 2784400.0 | 5.18 |
| Volkswagen | 1700100.0 | 3.16 |

## Q06. How does impact point relate to repair cost?

**Category:** Crash severity  
**Business value:** Quantify repair-cost differences by damaged vehicle zone.

```sql
SELECT Impact_Point, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr, ROUND(AVG(Speed_At_Impact_kmh), 2) AS avg_impact_speed_kmh, ROUND(100.0 * AVG(Airbag_Deployed), 2) AS airbag_rate_pct FROM telematics_claims GROUP BY Impact_Point ORDER BY avg_cost_inr DESC;
```

**Result:** 3 row(s) returned. Preview:
| Impact_Point | claim_count | avg_cost_inr | avg_impact_speed_kmh | airbag_rate_pct |
| --- | --- | --- | --- | --- |
| Front | 1446 | 19603.11 | 29.95 | 6.64 |
| Side | 836 | 18836.96 | 31.34 | 5.26 |
| Rear | 718 | 13495.4 | 29.6 | 4.46 |

## Q07. How does airbag deployment relate to repair cost?

**Category:** Crash severity  
**Business value:** Study a severity proxy; airbag deployment is not a causal estimate.

```sql
SELECT Airbag_Deployed, COUNT(*) AS claim_count, ROUND(AVG(Speed_At_Impact_kmh), 2) AS avg_speed_kmh, ROUND(AVG(G_Force_Impact), 2) AS avg_g_force, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY Airbag_Deployed ORDER BY Airbag_Deployed;
```

**Result:** 2 row(s) returned. Preview:
| Airbag_Deployed | claim_count | avg_speed_kmh | avg_g_force | avg_cost_inr |
| --- | --- | --- | --- | --- |
| 0.0 | 2828.0 | 27.38 | 1.26 | 13845.72 |
| 1.0 | 172.0 | 77.42 | 3.55 | 85045.35 |

## Q08. What are repair costs by impact-speed band?

**Category:** Crash severity  
**Business value:** Understand the cost curve over increasing impact speeds.

```sql
SELECT CASE WHEN Speed_At_Impact_kmh < 25 THEN '01 Low (<25)' WHEN Speed_At_Impact_kmh < 50 THEN '02 Moderate (25-49)' WHEN Speed_At_Impact_kmh < 80 THEN '03 High (50-79)' ELSE '04 Very high (80+)' END AS speed_band, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr, ROUND(AVG(G_Force_Impact), 2) AS avg_g_force FROM telematics_claims GROUP BY speed_band ORDER BY speed_band;
```

**Result:** 4 row(s) returned. Preview:
| speed_band | claim_count | avg_cost_inr | avg_g_force |
| --- | --- | --- | --- |
| 01 Low (<25) | 1654 | 4932.83 | 0.71 |
| 02 Moderate (25-49) | 750 | 17160.0 | 1.5 |
| 03 High (50-79) | 399 | 36715.79 | 2.48 |
| 04 Very high (80+) | 197 | 91903.55 | 4.43 |

## Q09. How does G-force band relate to average cost?

**Category:** Crash severity  
**Business value:** Use impact acceleration as another severity indicator.

```sql
SELECT CASE WHEN G_Force_Impact < 2 THEN '01 <2g' WHEN G_Force_Impact < 4 THEN '02 2-4g' WHEN G_Force_Impact < 7 THEN '03 4-7g' ELSE '04 7g+' END AS g_force_band, COUNT(*) AS claim_count, ROUND(AVG(Speed_At_Impact_kmh), 2) AS avg_speed_kmh, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY g_force_band ORDER BY g_force_band;
```

**Result:** 4 row(s) returned. Preview:
| g_force_band | claim_count | avg_speed_kmh | avg_cost_inr |
| --- | --- | --- | --- |
| 01 <2g | 2400 | 19.87 | 9041.13 |
| 02 2-4g | 496 | 64.35 | 40861.29 |
| 03 4-7g | 96 | 104.74 | 106394.79 |
| 04 7g+ | 8 | 136.57 | 200462.5 |

## Q10. Does weather condition correspond to different claim costs?

**Category:** Crash context  
**Business value:** Compare descriptive patterns across weather conditions.

```sql
SELECT Weather_Condition, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr, ROUND(AVG(Speed_At_Impact_kmh), 2) AS avg_speed_kmh FROM telematics_claims GROUP BY Weather_Condition ORDER BY claim_count DESC;
```

**Result:** 4 row(s) returned. Preview:
| Weather_Condition | claim_count | avg_cost_inr | avg_speed_kmh |
| --- | --- | --- | --- |
| Clear | 2172 | 18358.06 | 30.4 |
| Light Rain | 514 | 16092.22 | 29.35 |
| Heavy Rain | 208 | 18067.31 | 31.1 |
| Fog | 106 | 17739.62 | 29.92 |

## Q11. Which road types have the highest average repair cost?

**Category:** Crash context  
**Business value:** Inform road-context segmentation and severity reporting.

```sql
SELECT Road_Type, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr, ROUND(AVG(Speed_At_Impact_kmh), 2) AS avg_speed_kmh FROM telematics_claims GROUP BY Road_Type ORDER BY avg_cost_inr DESC;
```

**Result:** 4 row(s) returned. Preview:
| Road_Type | claim_count | avg_cost_inr | avg_speed_kmh |
| --- | --- | --- | --- |
| Highway | 532 | 19731.02 | 32.14 |
| Service Road | 414 | 18795.41 | 31.53 |
| Residential | 833 | 17763.63 | 29.57 |
| Urban Arterial | 1221 | 16960.03 | 29.46 |

## Q12. Which crash areas carry the largest repair spend?

**Category:** Geography  
**Business value:** Compare volume and financial burden by simulated area.

```sql
SELECT Crash_Area, COUNT(*) AS claim_count, ROUND(SUM(Actual_Repair_Cost_INR), 2) AS total_cost_inr, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY Crash_Area ORDER BY total_cost_inr DESC;
```

**Result:** 5 row(s) returned. Preview:
| Crash_Area | claim_count | total_cost_inr | avg_cost_inr |
| --- | --- | --- | --- |
| Delhi | 1203 | 21495800.0 | 17868.5 |
| Gurugram | 655 | 11290900.0 | 17238.02 |
| Noida | 587 | 10526900.0 | 17933.39 |
| Faridabad | 270 | 5359200.0 | 19848.89 |
| Ghaziabad | 285 | 5110700.0 | 17932.28 |

## Q13. How many claims occur each month?

**Category:** Time trends  
**Business value:** Provide a monthly operational workload baseline.

```sql
SELECT strftime('%Y-%m', AccidentDate) AS accident_month, COUNT(*) AS claim_count, ROUND(SUM(Actual_Repair_Cost_INR), 2) AS total_cost_inr, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY accident_month ORDER BY accident_month;
```

**Result:** 36 row(s) returned. Preview:
| accident_month | claim_count | total_cost_inr | avg_cost_inr |
| --- | --- | --- | --- |
| 2023-01 | 92 | 2211100.0 | 24033.7 |
| 2023-02 | 84 | 1153100.0 | 13727.38 |
| 2023-03 | 95 | 2169900.0 | 22841.05 |
| 2023-04 | 76 | 1360700.0 | 17903.95 |
| 2023-05 | 83 | 1583400.0 | 19077.11 |
| 2023-06 | 95 | 1787500.0 | 18815.79 |
| 2023-07 | 78 | 1525800.0 | 19561.54 |
| 2023-08 | 94 | 1644700.0 | 17496.81 |

## Q14. How does monthly claim count change from the prior month?

**Category:** Time trends  
**Business value:** Spot volume changes with a window function.

```sql
WITH monthly AS (SELECT strftime('%Y-%m', AccidentDate) AS accident_month, COUNT(*) AS claim_count FROM telematics_claims GROUP BY accident_month) SELECT accident_month, claim_count, LAG(claim_count) OVER (ORDER BY accident_month) AS prior_month_claims, claim_count - LAG(claim_count) OVER (ORDER BY accident_month) AS month_over_month_change FROM monthly ORDER BY accident_month;
```

**Result:** 36 row(s) returned. Preview:
| accident_month | claim_count | prior_month_claims | month_over_month_change |
| --- | --- | --- | --- |
| 2023-01 | 92 | nan | nan |
| 2023-02 | 84 | 92.0 | -8.0 |
| 2023-03 | 95 | 84.0 | 11.0 |
| 2023-04 | 76 | 95.0 | -19.0 |
| 2023-05 | 83 | 76.0 | 7.0 |
| 2023-06 | 95 | 83.0 | 12.0 |
| 2023-07 | 78 | 95.0 | -17.0 |
| 2023-08 | 94 | 78.0 | 16.0 |

## Q15. Are claims more common on weekdays or weekends?

**Category:** Time trends  
**Business value:** Support staffing patterns without inferring causation.

```sql
SELECT CASE WHEN CAST(strftime('%w', AccidentDate) AS INTEGER) IN (0,6) THEN 'Weekend' ELSE 'Weekday' END AS day_type, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY day_type;
```

**Result:** 2 row(s) returned. Preview:
| day_type | claim_count | avg_cost_inr |
| --- | --- | --- |
| Weekday | 2239 | 18139.71 |
| Weekend | 761 | 17304.47 |

## Q16. At what hours are incidents most frequent?

**Category:** Time trends  
**Business value:** Understand simulated hour-of-day workload peaks.

```sql
SELECT CAST(strftime('%H', AccidentDate) AS INTEGER) AS accident_hour, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY accident_hour ORDER BY claim_count DESC;
```

**Result:** 24 row(s) returned. Preview:
| accident_hour | claim_count | avg_cost_inr |
| --- | --- | --- |
| 17.0 | 257.0 | 19553.31 |
| 18.0 | 250.0 | 17548.8 |
| 15.0 | 230.0 | 18084.78 |
| 16.0 | 225.0 | 15463.56 |
| 19.0 | 200.0 | 15284.0 |
| 8.0 | 197.0 | 15121.83 |
| 20.0 | 180.0 | 20952.78 |
| 14.0 | 180.0 | 19629.44 |

## Q17. How does vehicle age relate to repair cost?

**Category:** Vehicle age  
**Business value:** Segment cost patterns by vehicle age at incident time.

```sql
SELECT CASE WHEN CAST(strftime('%Y', AccidentDate) AS INTEGER) - Model_Year < 3 THEN '0-2 years' WHEN CAST(strftime('%Y', AccidentDate) AS INTEGER) - Model_Year < 7 THEN '3-6 years' WHEN CAST(strftime('%Y', AccidentDate) AS INTEGER) - Model_Year < 12 THEN '7-11 years' ELSE '12+ years' END AS vehicle_age_band, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY vehicle_age_band ORDER BY vehicle_age_band;
```

**Result:** 4 row(s) returned. Preview:
| vehicle_age_band | claim_count | avg_cost_inr |
| --- | --- | --- |
| 0-2 years | 878 | 17754.33 |
| 12+ years | 83 | 10531.33 |
| 3-6 years | 1536 | 18087.76 |
| 7-11 years | 503 | 18962.82 |

## Q18. What are the 15 most expensive claims?

**Category:** Cost outliers  
**Business value:** Create a review queue of highest-value repair events.

```sql
SELECT ClaimID, AccidentDate, Vehicle_Brand, Crash_Area, Speed_At_Impact_kmh, G_Force_Impact, Airbag_Deployed, Actual_Repair_Cost_INR FROM telematics_claims ORDER BY Actual_Repair_Cost_INR DESC LIMIT 15;
```

**Result:** 15 row(s) returned. Preview:
| ClaimID | AccidentDate | Vehicle_Brand | Crash_Area | Speed_At_Impact_kmh | G_Force_Impact | Airbag_Deployed | Actual_Repair_Cost_INR |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CLM0000754 | 2023-01-09 00:05:00 | Hyundai | Faridabad | 128.2 | 6.7 | 1 | 549000 |
| CLM0000353 | 2023-03-15 12:16:00 | Tata | Delhi | 138.1 | 6.97 | 1 | 356700 |
| CLM0000966 | 2023-10-22 13:02:00 | Hyundai | Delhi | 135.0 | 7.43 | 1 | 273200 |
| CLM0001036 | 2025-03-24 17:33:00 | Mahindra | Noida | 142.0 | 7.36 | 1 | 269000 |
| CLM0001624 | 2023-10-05 13:48:00 | Mercedes-Benz | Gurugram | 118.9 | 5.87 | 1 | 247100 |
| CLM0000304 | 2024-02-23 09:23:00 | Hyundai | Gurugram | 130.2 | 6.59 | 1 | 239000 |
| CLM0001345 | 2023-10-07 15:58:00 | Mahindra | Delhi | 90.8 | 3.98 | 1 | 228800 |
| CLM0000596 | 2023-03-07 10:52:00 | Kia | Noida | 132.9 | 5.89 | 1 | 223700 |

## Q19. Which claims are above average cost by more than two standard deviations?

**Category:** Cost outliers  
**Business value:** Illustrate a transparent statistical outlier rule.

```sql
WITH stats AS (SELECT AVG(Actual_Repair_Cost_INR) AS avg_cost, (AVG(Actual_Repair_Cost_INR * Actual_Repair_Cost_INR) - AVG(Actual_Repair_Cost_INR) * AVG(Actual_Repair_Cost_INR)) AS var_cost FROM telematics_claims) SELECT c.ClaimID, c.Vehicle_Brand, c.Speed_At_Impact_kmh, c.G_Force_Impact, c.Actual_Repair_Cost_INR, ROUND(s.avg_cost, 2) AS portfolio_avg_cost FROM telematics_claims c CROSS JOIN stats s WHERE c.Actual_Repair_Cost_INR > s.avg_cost + 2 * sqrt(MAX(s.var_cost, 0)) ORDER BY c.Actual_Repair_Cost_INR DESC;
```

**Result:** 113 row(s) returned. Preview:
| ClaimID | Vehicle_Brand | Speed_At_Impact_kmh | G_Force_Impact | Actual_Repair_Cost_INR | portfolio_avg_cost |
| --- | --- | --- | --- | --- | --- |
| CLM0000754 | Hyundai | 128.2 | 6.7 | 549000 | 17927.83 |
| CLM0000353 | Tata | 138.1 | 6.97 | 356700 | 17927.83 |
| CLM0000966 | Hyundai | 135.0 | 7.43 | 273200 | 17927.83 |
| CLM0001036 | Mahindra | 142.0 | 7.36 | 269000 | 17927.83 |
| CLM0001624 | Mercedes-Benz | 118.9 | 5.87 | 247100 | 17927.83 |
| CLM0000304 | Hyundai | 130.2 | 6.59 | 239000 | 17927.83 |
| CLM0001345 | Mahindra | 90.8 | 3.98 | 228800 | 17927.83 |
| CLM0000596 | Kia | 132.9 | 5.89 | 223700 | 17927.83 |

## Q20. Which vehicles have the most recorded incidents?

**Category:** Vehicle patterns  
**Business value:** Identify repeated synthetic VehicleID appearances for further context.

```sql
SELECT VehicleID, COUNT(*) AS incident_count, ROUND(SUM(Actual_Repair_Cost_INR), 2) AS total_repair_cost_inr, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_repair_cost_inr FROM telematics_claims GROUP BY VehicleID HAVING COUNT(*) > 1 ORDER BY incident_count DESC, total_repair_cost_inr DESC LIMIT 20;
```

**Result:** 20 row(s) returned. Preview:
| VehicleID | incident_count | total_repair_cost_inr | avg_repair_cost_inr |
| --- | --- | --- | --- |
| VEH000029 | 6 | 142300.0 | 23716.67 |
| VEH000056 | 6 | 41100.0 | 6850.0 |
| VEH000047 | 6 | 38800.0 | 6466.67 |
| VEH000004 | 5 | 176700.0 | 35340.0 |
| VEH000030 | 5 | 71000.0 | 14200.0 |
| VEH000034 | 5 | 69900.0 | 13980.0 |
| VEH000045 | 5 | 64800.0 | 12960.0 |
| VEH000001 | 4 | 113900.0 | 28475.0 |

## Q21. What is the average cost for repeat versus single-incident vehicles?

**Category:** Vehicle patterns  
**Business value:** Compare groups while noting repeat identity is simulated.

```sql
WITH vehicle_counts AS (SELECT VehicleID, COUNT(*) AS claim_count FROM telematics_claims GROUP BY VehicleID) SELECT CASE WHEN v.claim_count > 1 THEN 'Repeat vehicle' ELSE 'Single recorded incident' END AS vehicle_group, COUNT(*) AS claims, ROUND(AVG(c.Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims c JOIN vehicle_counts v ON c.VehicleID = v.VehicleID GROUP BY vehicle_group;
```

**Result:** 2 row(s) returned. Preview:
| vehicle_group | claims | avg_cost_inr |
| --- | --- | --- |
| Repeat vehicle | 166 | 17395.78 |
| Single recorded incident | 2834 | 17959.0 |

## Q22. How is crash severity distributed by brand?

**Category:** Crash severity  
**Business value:** Separate brand volume from severity mix.

```sql
SELECT Vehicle_Brand, CASE WHEN Speed_At_Impact_kmh < 25 THEN 'Low' WHEN Speed_At_Impact_kmh < 50 THEN 'Moderate' WHEN Speed_At_Impact_kmh < 80 THEN 'High' ELSE 'Very high' END AS severity_band, COUNT(*) AS claim_count FROM telematics_claims GROUP BY Vehicle_Brand, severity_band ORDER BY Vehicle_Brand, claim_count DESC;
```

**Result:** 48 row(s) returned. Preview:
| Vehicle_Brand | severity_band | claim_count |
| --- | --- | --- |
| BMW | Low | 15 |
| BMW | Moderate | 5 |
| BMW | Very high | 2 |
| BMW | High | 1 |
| Honda | Low | 166 |
| Honda | Moderate | 64 |
| Honda | High | 38 |
| Honda | Very high | 10 |

## Q23. How does airbag deployment rate vary by speed band?

**Category:** Crash severity  
**Business value:** Check whether the generated safety signal behaves plausibly.

```sql
SELECT CASE WHEN Speed_At_Impact_kmh < 25 THEN 'Low (<25)' WHEN Speed_At_Impact_kmh < 50 THEN 'Moderate (25-49)' WHEN Speed_At_Impact_kmh < 80 THEN 'High (50-79)' ELSE 'Very high (80+)' END AS speed_band, COUNT(*) AS claim_count, ROUND(100.0 * AVG(Airbag_Deployed), 2) AS airbag_deployment_pct FROM telematics_claims GROUP BY speed_band ORDER BY speed_band;
```

**Result:** 4 row(s) returned. Preview:
| speed_band | claim_count | airbag_deployment_pct |
| --- | --- | --- |
| High (50-79) | 399 | 11.53 |
| Low (<25) | 1654 | 0.85 |
| Moderate (25-49) | 750 | 3.6 |
| Very high (80+) | 197 | 43.15 |

## Q24. What are average speed and costs by impact point?

**Category:** Crash severity  
**Business value:** Compare the mix of impact zones and associated loss amounts.

```sql
SELECT Impact_Point, COUNT(*) AS claim_count, ROUND(AVG(Speed_At_Impact_kmh), 2) AS avg_speed_kmh, ROUND(AVG(G_Force_Impact), 2) AS avg_g_force, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY Impact_Point ORDER BY avg_speed_kmh DESC;
```

**Result:** 3 row(s) returned. Preview:
| Impact_Point | claim_count | avg_speed_kmh | avg_g_force | avg_cost_inr |
| --- | --- | --- | --- | --- |
| Side | 836 | 31.34 | 1.44 | 18836.96 |
| Front | 1446 | 29.95 | 1.37 | 19603.11 |
| Rear | 718 | 29.6 | 1.35 | 13495.4 |

## Q25. How do costs vary across speed quartiles?

**Category:** Crash severity  
**Business value:** Compare relative cost progression using NTILE windowing.

```sql
WITH bands AS (SELECT *, NTILE(4) OVER (ORDER BY Speed_At_Impact_kmh) AS speed_quartile FROM telematics_claims) SELECT speed_quartile, COUNT(*) AS claim_count, ROUND(MIN(Speed_At_Impact_kmh), 2) AS min_speed, ROUND(MAX(Speed_At_Impact_kmh), 2) AS max_speed, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM bands GROUP BY speed_quartile ORDER BY speed_quartile;
```

**Result:** 4 row(s) returned. Preview:
| speed_quartile | claim_count | min_speed | max_speed | avg_cost_inr |
| --- | --- | --- | --- | --- |
| 1.0 | 750.0 | 1.1 | 9.6 | 3747.2 |
| 2.0 | 750.0 | 9.6 | 18.6 | 5456.0 |
| 3.0 | 750.0 | 18.6 | 45.0 | 13990.13 |
| 4.0 | 750.0 | 45.1 | 142.0 | 48518.0 |

## Q26. Which features accompany the highest repair costs?

**Category:** Crash severity  
**Business value:** Summarize severity indicators alongside claim cost.

```sql
SELECT CASE WHEN Airbag_Deployed = 1 THEN 'Airbag deployed' ELSE 'No airbag deployment' END AS airbag_status, Impact_Point, COUNT(*) AS claim_count, ROUND(AVG(Speed_At_Impact_kmh), 2) AS avg_speed_kmh, ROUND(AVG(G_Force_Impact), 2) AS avg_g_force, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY airbag_status, Impact_Point ORDER BY avg_cost_inr DESC;
```

**Result:** 6 row(s) returned. Preview:
| airbag_status | Impact_Point | claim_count | avg_speed_kmh | avg_g_force | avg_cost_inr |
| --- | --- | --- | --- | --- | --- |
| Airbag deployed | Front | 96 | 74.97 | 3.43 | 89394.79 |
| Airbag deployed | Side | 44 | 82.28 | 3.82 | 88352.27 |
| Airbag deployed | Rear | 32 | 78.07 | 3.53 | 67450.0 |
| No airbag deployment | Side | 792 | 28.51 | 1.31 | 14975.0 |
| No airbag deployment | Front | 1350 | 26.75 | 1.23 | 14640.15 |
| No airbag deployment | Rear | 686 | 27.34 | 1.25 | 10978.57 |

## Q27. What is the repair-cost distribution by percentile group?

**Category:** Cost distribution  
**Business value:** Expose long-tail cost behavior rather than relying only on averages.

```sql
WITH ranked AS (SELECT Actual_Repair_Cost_INR, NTILE(10) OVER (ORDER BY Actual_Repair_Cost_INR) AS cost_decile FROM telematics_claims) SELECT cost_decile, COUNT(*) AS claim_count, ROUND(MIN(Actual_Repair_Cost_INR), 2) AS min_cost_inr, ROUND(MAX(Actual_Repair_Cost_INR), 2) AS max_cost_inr, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM ranked GROUP BY cost_decile ORDER BY cost_decile;
```

**Result:** 10 row(s) returned. Preview:
| cost_decile | claim_count | min_cost_inr | max_cost_inr | avg_cost_inr |
| --- | --- | --- | --- | --- |
| 1.0 | 300.0 | 1800.0 | 2800.0 | 2254.0 |
| 2.0 | 300.0 | 2800.0 | 3600.0 | 3197.67 |
| 3.0 | 300.0 | 3600.0 | 4400.0 | 3972.0 |
| 4.0 | 300.0 | 4400.0 | 5700.0 | 5047.0 |
| 5.0 | 300.0 | 5700.0 | 7600.0 | 6594.33 |
| 6.0 | 300.0 | 7600.0 | 11300.0 | 9215.33 |
| 7.0 | 300.0 | 11300.0 | 16500.0 | 13744.33 |
| 8.0 | 300.0 | 16500.0 | 24900.0 | 20388.0 |

## Q28. How do claim volume and average cost change by quarter?

**Category:** Time trends  
**Business value:** Provide a quarterly view for staffing and trend discussion.

```sql
SELECT strftime('%Y', AccidentDate) AS accident_year, CAST((CAST(strftime('%m', AccidentDate) AS INTEGER) + 2) / 3 AS INTEGER) AS accident_quarter, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr, ROUND(SUM(Actual_Repair_Cost_INR), 2) AS total_cost_inr FROM telematics_claims GROUP BY accident_year, accident_quarter ORDER BY accident_year, accident_quarter;
```

**Result:** 12 row(s) returned. Preview:
| accident_year | accident_quarter | claim_count | avg_cost_inr | total_cost_inr |
| --- | --- | --- | --- | --- |
| 2023 | 1 | 271 | 20421.03 | 5534100.0 |
| 2023 | 2 | 254 | 18628.35 | 4731600.0 |
| 2023 | 3 | 251 | 18299.6 | 4593200.0 |
| 2023 | 4 | 235 | 20808.94 | 4890100.0 |
| 2024 | 1 | 267 | 18889.51 | 5043500.0 |
| 2024 | 2 | 262 | 16707.63 | 4377400.0 |
| 2024 | 3 | 257 | 17131.91 | 4402900.0 |
| 2024 | 4 | 228 | 19782.46 | 4510400.0 |

## Q29. Are weekend incidents more expensive after grouping by impact point?

**Category:** Time trends  
**Business value:** Check whether a simple aggregate is being driven by crash mix.

```sql
SELECT CASE WHEN CAST(strftime('%w', AccidentDate) AS INTEGER) IN (0,6) THEN 'Weekend' ELSE 'Weekday' END AS day_type, Impact_Point, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY day_type, Impact_Point ORDER BY day_type, avg_cost_inr DESC;
```

**Result:** 6 row(s) returned. Preview:
| day_type | Impact_Point | claim_count | avg_cost_inr |
| --- | --- | --- | --- |
| Weekday | Front | 1076 | 19873.61 |
| Weekday | Side | 633 | 18473.93 |
| Weekday | Rear | 530 | 14220.38 |
| Weekend | Side | 203 | 19968.97 |
| Weekend | Front | 370 | 18816.49 |
| Weekend | Rear | 188 | 11451.6 |

## Q30. What are claim counts and costs by vehicle-age band and brand?

**Category:** Vehicle age  
**Business value:** Support segment-specific repair-cost benchmarking.

```sql
SELECT Vehicle_Brand, CASE WHEN CAST(strftime('%Y', AccidentDate) AS INTEGER) - Model_Year < 3 THEN '0-2 years' WHEN CAST(strftime('%Y', AccidentDate) AS INTEGER) - Model_Year < 7 THEN '3-6 years' WHEN CAST(strftime('%Y', AccidentDate) AS INTEGER) - Model_Year < 12 THEN '7-11 years' ELSE '12+ years' END AS vehicle_age_band, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY Vehicle_Brand, vehicle_age_band HAVING COUNT(*) >= 5 ORDER BY Vehicle_Brand, avg_cost_inr DESC;
```

**Result:** 42 row(s) returned. Preview:
| Vehicle_Brand | vehicle_age_band | claim_count | avg_cost_inr |
| --- | --- | --- | --- |
| BMW | 7-11 years | 5 | 49400.0 |
| BMW | 0-2 years | 10 | 21260.0 |
| BMW | 3-6 years | 8 | 21175.0 |
| Honda | 3-6 years | 144 | 17172.22 |
| Honda | 7-11 years | 42 | 15245.24 |
| Honda | 0-2 years | 86 | 13594.19 |
| Honda | 12+ years | 6 | 5400.0 |
| Hyundai | 7-11 years | 97 | 23921.65 |

## Q31. How many garages specialize in each vehicle brand?

**Category:** Garage network  
**Business value:** Measure supply depth by make.

```sql
SELECT Brand_Specialization AS Vehicle_Brand, COUNT(*) AS garage_count, SUM(CASE WHEN Parts_Available = 1 THEN 1 ELSE 0 END) AS in_stock_garages, SUM(CASE WHEN Preferred_Partner = 1 THEN 1 ELSE 0 END) AS preferred_garages FROM partner_garages GROUP BY Brand_Specialization ORDER BY garage_count DESC;
```

**Result:** 12 row(s) returned. Preview:
| Vehicle_Brand | garage_count | in_stock_garages | preferred_garages |
| --- | --- | --- | --- |
| Hyundai | 20 | 15 | 12 |
| Maruti Suzuki | 20 | 20 | 15 |
| Honda | 10 | 8 | 6 |
| Kia | 10 | 10 | 4 |
| Mahindra | 8 | 7 | 7 |
| Tata | 7 | 7 | 7 |
| Toyota | 7 | 5 | 7 |
| Renault | 5 | 2 | 2 |

## Q32. What is parts availability by brand?

**Category:** Garage network  
**Business value:** Identify makes where routing choices may be constrained.

```sql
SELECT Brand_Specialization AS Vehicle_Brand, COUNT(*) AS garage_count, ROUND(100.0 * AVG(CASE WHEN Parts_Available = 1 THEN 1.0 ELSE 0.0 END), 2) AS in_stock_pct, SUM(CASE WHEN Parts_Available = 0 THEN 1 ELSE 0 END) AS out_of_stock_garages FROM partner_garages GROUP BY Brand_Specialization ORDER BY in_stock_pct;
```

**Result:** 12 row(s) returned. Preview:
| Vehicle_Brand | garage_count | in_stock_pct | out_of_stock_garages |
| --- | --- | --- | --- |
| Renault | 5 | 40.0 | 3 |
| Skoda | 4 | 50.0 | 2 |
| BMW | 3 | 66.67 | 1 |
| Volkswagen | 3 | 66.67 | 1 |
| Toyota | 7 | 71.43 | 2 |
| Hyundai | 20 | 75.0 | 5 |
| Honda | 10 | 80.0 | 2 |
| Mahindra | 8 | 87.5 | 1 |

## Q33. Which areas have the largest preferred-partner share?

**Category:** Garage network  
**Business value:** Review network composition by area.

```sql
SELECT Area, COUNT(*) AS garage_count, SUM(CASE WHEN Preferred_Partner = 1 THEN 1 ELSE 0 END) AS preferred_count, ROUND(100.0 * AVG(CASE WHEN Preferred_Partner = 1 THEN 1.0 ELSE 0.0 END), 2) AS preferred_share_pct FROM partner_garages GROUP BY Area ORDER BY preferred_share_pct DESC;
```

**Result:** 5 row(s) returned. Preview:
| Area | garage_count | preferred_count | preferred_share_pct |
| --- | --- | --- | --- |
| Gurugram | 30 | 22 | 73.33 |
| Noida | 22 | 16 | 72.73 |
| Delhi | 32 | 23 | 71.88 |
| Ghaziabad | 9 | 4 | 44.44 |
| Faridabad | 7 | 3 | 42.86 |

## Q34. Which areas have the greatest daily service capacity?

**Category:** Garage network  
**Business value:** Compare total intake capacity across simulated service areas.

```sql
SELECT Area, COUNT(*) AS garage_count, SUM(Daily_Service_Capacity) AS total_daily_capacity, ROUND(AVG(Daily_Service_Capacity), 1) AS avg_capacity_per_garage FROM partner_garages GROUP BY Area ORDER BY total_daily_capacity DESC;
```

**Result:** 5 row(s) returned. Preview:
| Area | garage_count | total_daily_capacity | avg_capacity_per_garage |
| --- | --- | --- | --- |
| Gurugram | 30 | 513 | 17.1 |
| Delhi | 32 | 473 | 14.8 |
| Noida | 22 | 404 | 18.4 |
| Ghaziabad | 9 | 140 | 15.6 |
| Faridabad | 7 | 83 | 11.9 |

## Q35. Which garage-specialization groups have longer turnaround?

**Category:** Garage network  
**Business value:** Find potential cycle-time bottlenecks in the simulated network.

```sql
SELECT Brand_Specialization AS Vehicle_Brand, COUNT(*) AS garage_count, ROUND(AVG(Avg_Repair_Turnaround_Days), 2) AS avg_turnaround_days, ROUND(MIN(Avg_Repair_Turnaround_Days), 2) AS min_turnaround_days, ROUND(MAX(Avg_Repair_Turnaround_Days), 2) AS max_turnaround_days FROM partner_garages GROUP BY Brand_Specialization ORDER BY avg_turnaround_days DESC;
```

**Result:** 12 row(s) returned. Preview:
| Vehicle_Brand | garage_count | avg_turnaround_days | min_turnaround_days | max_turnaround_days |
| --- | --- | --- | --- | --- |
| Renault | 5 | 4.76 | 1.8 | 8.6 |
| Mahindra | 8 | 3.56 | 1.4 | 5.9 |
| Tata | 7 | 3.39 | 1.2 | 5.3 |
| Hyundai | 20 | 3.36 | 0.5 | 9.0 |
| Volkswagen | 3 | 3.33 | 1.9 | 6.2 |
| Skoda | 4 | 3.27 | 1.5 | 5.5 |
| Mercedes-Benz | 3 | 3.0 | 1.1 | 5.7 |
| Honda | 10 | 2.89 | 1.6 | 6.3 |

## Q36. How do simulated labor rates vary by area?

**Category:** Garage network  
**Business value:** Review cost-of-service differences in the garage network.

```sql
SELECT Area, COUNT(*) AS garage_count, ROUND(AVG(Labor_Rate_INR_Per_Hour), 2) AS avg_labor_rate_inr_hour, MIN(Labor_Rate_INR_Per_Hour) AS min_labor_rate, MAX(Labor_Rate_INR_Per_Hour) AS max_labor_rate FROM partner_garages GROUP BY Area ORDER BY avg_labor_rate_inr_hour DESC;
```

**Result:** 5 row(s) returned. Preview:
| Area | garage_count | avg_labor_rate_inr_hour | min_labor_rate | max_labor_rate |
| --- | --- | --- | --- | --- |
| Gurugram | 30 | 1046.93 | 825 | 1287 |
| Delhi | 32 | 933.31 | 689 | 1288 |
| Noida | 22 | 924.5 | 715 | 1318 |
| Ghaziabad | 9 | 773.89 | 675 | 963 |
| Faridabad | 7 | 755.43 | 723 | 785 |

## Q37. Which vehicle brands have out-of-stock garages?

**Category:** Garage network  
**Business value:** Plan spare-parts availability improvements.

```sql
SELECT Brand_Specialization AS Vehicle_Brand, COUNT(*) AS garage_count, SUM(CASE WHEN Parts_Available = 0 THEN 1 ELSE 0 END) AS out_of_stock_count, ROUND(100.0 * AVG(CASE WHEN Parts_Available = 0 THEN 1.0 ELSE 0.0 END), 2) AS out_of_stock_pct FROM partner_garages GROUP BY Brand_Specialization HAVING out_of_stock_count > 0 ORDER BY out_of_stock_pct DESC;
```

**Result:** 8 row(s) returned. Preview:
| Vehicle_Brand | garage_count | out_of_stock_count | out_of_stock_pct |
| --- | --- | --- | --- |
| Renault | 5 | 3 | 60.0 |
| Skoda | 4 | 2 | 50.0 |
| BMW | 3 | 1 | 33.33 |
| Volkswagen | 3 | 1 | 33.33 |
| Toyota | 7 | 2 | 28.57 |
| Hyundai | 20 | 5 | 25.0 |
| Honda | 10 | 2 | 20.0 |
| Mahindra | 8 | 1 | 12.5 |

## Q38. Is garage supply proportional to the claim mix by brand?

**Category:** Garage coverage  
**Business value:** Compare demand share with eligible garage supply share.

```sql
WITH demand AS (SELECT Vehicle_Brand, COUNT(*) AS claim_count FROM telematics_claims GROUP BY Vehicle_Brand), supply AS (SELECT Brand_Specialization AS Vehicle_Brand, SUM(CASE WHEN Parts_Available = 1 THEN 1 ELSE 0 END) AS eligible_garages FROM partner_garages GROUP BY Brand_Specialization), totals AS (SELECT SUM(claim_count) AS total_claims FROM demand), total_supply AS (SELECT SUM(eligible_garages) AS total_garages FROM supply) SELECT d.Vehicle_Brand, d.claim_count, s.eligible_garages, ROUND(100.0 * d.claim_count / t.total_claims, 2) AS demand_share_pct, ROUND(100.0 * s.eligible_garages / ts.total_garages, 2) AS eligible_supply_share_pct, ROUND(1.0 * d.claim_count / NULLIF(s.eligible_garages, 0), 2) AS claims_per_eligible_garage FROM demand d JOIN supply s ON d.Vehicle_Brand = s.Vehicle_Brand CROSS JOIN totals t CROSS JOIN total_supply ts ORDER BY claims_per_eligible_garage DESC;
```

**Result:** 12 row(s) returned. Preview:
| Vehicle_Brand | claim_count | eligible_garages | demand_share_pct | eligible_supply_share_pct | claims_per_eligible_garage |
| --- | --- | --- | --- | --- | --- |
| Tata | 421 | 7 | 14.03 | 8.43 | 60.14 |
| Mahindra | 323 | 7 | 10.77 | 8.43 | 46.14 |
| Maruti Suzuki | 804 | 20 | 26.8 | 24.1 | 40.2 |
| Renault | 79 | 2 | 2.63 | 2.41 | 39.5 |
| Hyundai | 588 | 15 | 19.6 | 18.07 | 39.2 |
| Volkswagen | 71 | 2 | 2.37 | 2.41 | 35.5 |
| Honda | 278 | 8 | 9.27 | 9.64 | 34.75 |
| Toyota | 153 | 5 | 5.1 | 6.02 | 30.6 |

## Q39. Which brands have the fewest in-stock preferred garages?

**Category:** Garage coverage  
**Business value:** Locate potential preferred-network coverage gaps.

```sql
SELECT Brand_Specialization AS Vehicle_Brand, SUM(CASE WHEN Parts_Available = 1 AND Preferred_Partner = 1 THEN 1 ELSE 0 END) AS preferred_in_stock_garages, SUM(CASE WHEN Parts_Available = 1 THEN 1 ELSE 0 END) AS all_in_stock_garages FROM partner_garages GROUP BY Brand_Specialization ORDER BY preferred_in_stock_garages ASC, all_in_stock_garages ASC;
```

**Result:** 12 row(s) returned. Preview:
| Vehicle_Brand | preferred_in_stock_garages | all_in_stock_garages |
| --- | --- | --- |
| Skoda | 0 | 2 |
| Renault | 1 | 2 |
| BMW | 2 | 2 |
| Volkswagen | 2 | 2 |
| Mercedes-Benz | 2 | 3 |
| Kia | 4 | 10 |
| Toyota | 5 | 5 |
| Honda | 5 | 8 |

## Q40. What is the average capacity-to-turnaround profile by area?

**Category:** Garage coverage  
**Business value:** Compare network capacity with simulated repair duration.

```sql
SELECT Area, COUNT(*) AS garage_count, ROUND(AVG(Daily_Service_Capacity), 2) AS avg_daily_capacity, ROUND(AVG(Avg_Repair_Turnaround_Days), 2) AS avg_turnaround_days, ROUND(AVG(Daily_Service_Capacity / NULLIF(Avg_Repair_Turnaround_Days, 0)), 2) AS capacity_per_turnaround_day FROM partner_garages GROUP BY Area ORDER BY capacity_per_turnaround_day DESC;
```

**Result:** 5 row(s) returned. Preview:
| Area | garage_count | avg_daily_capacity | avg_turnaround_days | capacity_per_turnaround_day |
| --- | --- | --- | --- | --- |
| Faridabad | 7 | 11.86 | 2.9 | 12.69 |
| Gurugram | 30 | 17.1 | 2.93 | 10.18 |
| Noida | 22 | 18.36 | 3.1 | 9.42 |
| Delhi | 32 | 14.78 | 2.93 | 9.0 |
| Ghaziabad | 9 | 15.56 | 3.26 | 6.3 |

## Q41. How many routes used the preferred-partner fallback?

**Category:** Routing operations  
**Business value:** Show whether routing had to relax the preferred-partner condition.

```sql
SELECT Preferred_Fallback_Used, COUNT(*) AS claim_count, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM garage_routing), 2) AS share_pct FROM garage_routing GROUP BY Preferred_Fallback_Used;
```

**Result:** 2 row(s) returned. Preview:
| Preferred_Fallback_Used | claim_count | share_pct |
| --- | --- | --- |
| 0.0 | 2965.0 | 98.83 |
| 1.0 | 35.0 | 1.17 |

## Q42. What are average route distance and cycle time by brand?

**Category:** Routing operations  
**Business value:** Compare routing effort across vehicle makes.

```sql
SELECT Vehicle_Brand, COUNT(*) AS routed_claims, ROUND(AVG(Recommended_Garage_Distance_km), 2) AS avg_distance_km, ROUND(AVG(Recommended_Garage_Travel_Minutes), 1) AS avg_travel_minutes, ROUND(AVG(Recommended_Garage_Turnaround_Days), 2) AS avg_turnaround_days, ROUND(AVG(Recommended_Garage_Est_Cycle_Hours), 2) AS avg_estimated_cycle_hours FROM garage_routing GROUP BY Vehicle_Brand ORDER BY avg_estimated_cycle_hours DESC;
```

**Result:** 12 row(s) returned. Preview:
| Vehicle_Brand | routed_claims | avg_distance_km | avg_travel_minutes | avg_turnaround_days | avg_estimated_cycle_hours |
| --- | --- | --- | --- | --- | --- |
| Renault | 79 | 19.7 | 47.3 | 8.6 | 207.19 |
| Skoda | 35 | 10.97 | 26.3 | 5.0 | 120.44 |
| Kia | 203 | 6.31 | 15.1 | 3.14 | 75.54 |
| Tata | 421 | 6.1 | 14.6 | 2.89 | 69.55 |
| Mahindra | 323 | 6.93 | 16.6 | 2.6 | 62.66 |
| BMW | 23 | 13.09 | 31.4 | 2.53 | 61.36 |
| Volkswagen | 71 | 18.25 | 43.8 | 2.2 | 53.6 |
| Hyundai | 588 | 5.19 | 12.5 | 2.02 | 48.8 |

## Q43. Which garages receive the most routing recommendations?

**Category:** Routing operations  
**Business value:** Show how the routing heuristic distributes simulated work.

```sql
SELECT r.Recommended_GarageID, g.Garage_Name, g.Area, g.Brand_Specialization, COUNT(*) AS recommended_claims, g.Daily_Service_Capacity, ROUND(1.0 * COUNT(*) / g.Daily_Service_Capacity, 2) AS claims_per_capacity_unit_proxy FROM garage_routing r JOIN partner_garages g ON r.Recommended_GarageID = g.GarageID GROUP BY r.Recommended_GarageID, g.Garage_Name, g.Area, g.Brand_Specialization, g.Daily_Service_Capacity ORDER BY recommended_claims DESC LIMIT 20;
```

**Result:** 20 row(s) returned. Preview:
| Recommended_GarageID | Garage_Name | Area | Brand_Specialization | recommended_claims | Daily_Service_Capacity | claims_per_capacity_unit_proxy |
| --- | --- | --- | --- | --- | --- | --- |
| GAR0075 | Delhi Auto Service Centre 075 | Delhi | Maruti Suzuki | 303 | 25 | 12.12 |
| GAR0065 | Delhi Auto Service Centre 065 | Delhi | Hyundai | 206 | 22 | 9.36 |
| GAR0079 | Delhi Auto Service Centre 079 | Delhi | Honda | 199 | 8 | 24.88 |
| GAR0061 | Noida Auto Service Centre 061 | Noida | Maruti Suzuki | 176 | 23 | 7.65 |
| GAR0097 | Noida Auto Service Centre 097 | Noida | Hyundai | 171 | 33 | 5.18 |
| GAR0032 | Delhi Auto Service Centre 032 | Delhi | Tata | 149 | 24 | 6.21 |
| GAR0057 | Noida Auto Service Centre 057 | Noida | Mahindra | 132 | 12 | 11.0 |
| GAR0099 | Gurugram Auto Service Centre 099 | Gurugram | Maruti Suzuki | 131 | 33 | 3.97 |

## Q44. Which crash areas have the longest average garage route?

**Category:** Routing operations  
**Business value:** Identify simulated geography with more travel burden.

```sql
SELECT Crash_Area, COUNT(*) AS routed_claims, ROUND(AVG(Recommended_Garage_Distance_km), 2) AS avg_distance_km, ROUND(MAX(Recommended_Garage_Distance_km), 2) AS max_distance_km, ROUND(AVG(Recommended_Garage_Travel_Minutes), 1) AS avg_travel_minutes FROM garage_routing GROUP BY Crash_Area ORDER BY avg_distance_km DESC;
```

**Result:** 5 row(s) returned. Preview:
| Crash_Area | routed_claims | avg_distance_km | max_distance_km | avg_travel_minutes |
| --- | --- | --- | --- | --- |
| Ghaziabad | 285 | 11.89 | 33.4 | 28.5 |
| Faridabad | 270 | 9.96 | 29.65 | 23.9 |
| Gurugram | 655 | 7.14 | 43.72 | 17.1 |
| Noida | 587 | 6.17 | 32.67 | 14.8 |
| Delhi | 1203 | 5.73 | 28.64 | 13.8 |

## Q45. How often is the balanced recommendation farther than the nearest eligible garage?

**Category:** Routing operations  
**Business value:** Quantify the distance-versus-turnaround/capacity trade-off.

```sql
SELECT COUNT(*) AS claims_routed, SUM(CASE WHEN Recommended_GarageID <> Nearest_Eligible_GarageID THEN 1 ELSE 0 END) AS recommendation_differs_from_nearest, ROUND(100.0 * AVG(CASE WHEN Recommended_GarageID <> Nearest_Eligible_GarageID THEN 1.0 ELSE 0.0 END), 2) AS changed_recommendation_pct, ROUND(AVG(Recommended_Garage_Distance_km - Nearest_Eligible_Garage_Distance_km), 3) AS avg_extra_distance_km FROM garage_routing;
```

**Result:** 1 row(s) returned. Preview:
| claims_routed | recommendation_differs_from_nearest | changed_recommendation_pct | avg_extra_distance_km |
| --- | --- | --- | --- |
| 3000.0 | 1106.0 | 36.87 | 0.748 |

## Q46. How many claims are routed beyond 10 kilometres?

**Category:** Routing operations  
**Business value:** Find longer-distance routing cases for manual review.

```sql
SELECT COUNT(*) AS claims_over_10km, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM garage_routing), 2) AS share_pct, ROUND(AVG(Recommended_Garage_Distance_km), 2) AS avg_distance_over_10km FROM garage_routing WHERE Recommended_Garage_Distance_km > 10;
```

**Result:** 1 row(s) returned. Preview:
| claims_over_10km | share_pct | avg_distance_over_10km |
| --- | --- | --- |
| 649.0 | 21.63 | 17.75 |

## Q47. What is routing distance by garage policy?

**Category:** Routing operations  
**Business value:** Compare preferred-only routing with fallback scenarios.

```sql
SELECT Candidate_Policy, COUNT(*) AS claims, ROUND(AVG(Recommended_Garage_Distance_km), 2) AS avg_distance_km, ROUND(AVG(Recommended_Garage_Turnaround_Days), 2) AS avg_turnaround_days, ROUND(AVG(Recommended_Garage_Est_Cycle_Hours), 2) AS avg_cycle_hours FROM garage_routing GROUP BY Candidate_Policy ORDER BY claims DESC;
```

**Result:** 2 row(s) returned. Preview:
| Candidate_Policy | claims | avg_distance_km | avg_turnaround_days | avg_cycle_hours |
| --- | --- | --- | --- | --- |
| Preferred partner + brand match + parts in stock | 2965 | 7.05 | 2.12 | 51.1 |
| Fallback: any brand-matched in-stock partner | 35 | 10.97 | 5.0 | 120.44 |

## Q48. Where are route recommendation counts concentrated?

**Category:** Routing operations  
**Business value:** Examine routing allocations by area and garage specialization.

```sql
SELECT Crash_Area, Recommended_Garage_Area, COUNT(*) AS route_count, ROUND(AVG(Recommended_Garage_Distance_km), 2) AS avg_distance_km FROM garage_routing GROUP BY Crash_Area, Recommended_Garage_Area ORDER BY route_count DESC LIMIT 25;
```

**Result:** 20 row(s) returned. Preview:
| Crash_Area | Recommended_Garage_Area | route_count | avg_distance_km |
| --- | --- | --- | --- |
| Delhi | Delhi | 1111 | 4.87 |
| Gurugram | Gurugram | 581 | 4.4 |
| Noida | Noida | 478 | 3.83 |
| Ghaziabad | Noida | 146 | 14.44 |
| Faridabad | Faridabad | 126 | 3.26 |
| Faridabad | Noida | 121 | 14.04 |
| Ghaziabad | Ghaziabad | 99 | 4.09 |
| Delhi | Noida | 76 | 17.5 |

## Q49. What is holdout prediction error by impact-speed band?

**Category:** Repair model  
**Business value:** Check where model performance varies with crash severity.

```sql
SELECT CASE WHEN Speed_At_Impact_kmh < 25 THEN 'Low (<25)' WHEN Speed_At_Impact_kmh < 50 THEN 'Moderate (25-49)' WHEN Speed_At_Impact_kmh < 80 THEN 'High (50-79)' ELSE 'Very high (80+)' END AS speed_band, COUNT(*) AS holdout_claims, ROUND(AVG(Absolute_Error_INR), 2) AS mae_inr, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_actual_cost_inr, ROUND(AVG(Predicted_Repair_Cost_INR), 2) AS avg_predicted_cost_inr FROM holdout_predictions GROUP BY speed_band ORDER BY speed_band;
```

**Result:** 4 row(s) returned. Preview:
| speed_band | holdout_claims | mae_inr | avg_actual_cost_inr | avg_predicted_cost_inr |
| --- | --- | --- | --- | --- |
| High (50-79) | 76 | 9804.04 | 33425.0 | 35470.83 |
| Low (<25) | 337 | 1409.35 | 4812.76 | 4907.0 |
| Moderate (25-49) | 160 | 5064.15 | 17205.63 | 17852.35 |
| Very high (80+) | 27 | 25184.04 | 72411.11 | 85411.64 |

## Q50. Which brands have the largest holdout prediction errors?

**Category:** Repair model  
**Business value:** Identify vehicle makes where repair-cost estimates need caution.

```sql
SELECT Vehicle_Brand, COUNT(*) AS holdout_claims, ROUND(AVG(Absolute_Error_INR), 2) AS mae_inr, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_actual_cost_inr, ROUND(AVG(Predicted_Repair_Cost_INR), 2) AS avg_predicted_cost_inr FROM holdout_predictions GROUP BY Vehicle_Brand HAVING COUNT(*) >= 5 ORDER BY mae_inr DESC;
```

**Result:** 9 row(s) returned. Preview:
| Vehicle_Brand | holdout_claims | mae_inr | avg_actual_cost_inr | avg_predicted_cost_inr |
| --- | --- | --- | --- | --- |
| Tata | 88 | 5560.37 | 13669.32 | 16260.36 |
| Maruti Suzuki | 151 | 4946.74 | 13796.03 | 16555.56 |
| Toyota | 34 | 4570.14 | 17661.76 | 14214.47 |
| Volkswagen | 14 | 4154.76 | 21985.71 | 20932.39 |
| Kia | 42 | 4114.54 | 14490.48 | 12667.54 |
| Hyundai | 120 | 4021.87 | 14598.33 | 16444.81 |
| Honda | 58 | 4016.48 | 11931.03 | 12366.3 |
| Mahindra | 64 | 3789.75 | 16539.06 | 17013.95 |

## Q51. What are the most poorly predicted holdout claims?

**Category:** Repair model  
**Business value:** Create examples for error analysis, not automatic claim denials.

```sql
SELECT ClaimID, AccidentDate, Vehicle_Brand, Speed_At_Impact_kmh, G_Force_Impact, Airbag_Deployed, Actual_Repair_Cost_INR, Predicted_Repair_Cost_INR, Absolute_Error_INR FROM holdout_predictions ORDER BY Absolute_Error_INR DESC LIMIT 20;
```

**Result:** 20 row(s) returned. Preview:
| ClaimID | AccidentDate | Vehicle_Brand | Speed_At_Impact_kmh | G_Force_Impact | Airbag_Deployed | Actual_Repair_Cost_INR | Predicted_Repair_Cost_INR | Absolute_Error_INR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CLM0002451 | 2025-11-11 06:19:00 | Tata | 90.7 | 3.99 | 0 | 22400 | 110173.46 | 87773.46 |
| CLM0002529 | 2025-11-19 17:51:00 | Maruti Suzuki | 126.8 | 6.5 | 1 | 102600 | 162353.56 | 59753.56 |
| CLM0002943 | 2025-08-16 18:12:00 | Maruti Suzuki | 116.5 | 6.13 | 1 | 80000 | 134338.2 | 54338.2 |
| CLM0000072 | 2025-06-10 07:53:00 | Maruti Suzuki | 96.0 | 4.54 | 0 | 53800 | 105720.18 | 51920.18 |
| CLM0000435 | 2025-07-18 04:08:00 | Hyundai | 87.5 | 3.1 | 1 | 76800 | 124460.63 | 47660.63 |
| CLM0000031 | 2025-10-02 07:43:00 | Tata | 85.4 | 3.75 | 0 | 21600 | 68081.56 | 46481.56 |
| CLM0000618 | 2025-11-19 17:42:00 | Toyota | 86.6 | 3.87 | 0 | 110000 | 64061.0 | 45939.0 |
| CLM0002763 | 2025-12-05 20:08:00 | Honda | 75.0 | 3.66 | 1 | 45200 | 85051.65 | 39851.65 |

## Q52. Does prediction bias differ across vehicle makes?

**Category:** Repair model  
**Business value:** Inspect signed errors for systematic over- or underprediction.

```sql
SELECT Vehicle_Brand, COUNT(*) AS holdout_claims, ROUND(AVG(Signed_Error_INR), 2) AS mean_signed_error_inr, ROUND(AVG(Absolute_Error_INR), 2) AS mean_absolute_error_inr FROM holdout_predictions GROUP BY Vehicle_Brand HAVING COUNT(*) >= 5 ORDER BY ABS(AVG(Signed_Error_INR)) DESC;
```

**Result:** 9 row(s) returned. Preview:
| Vehicle_Brand | holdout_claims | mean_signed_error_inr | mean_absolute_error_inr |
| --- | --- | --- | --- |
| Toyota | 34 | -3447.3 | 4570.14 |
| Maruti Suzuki | 151 | 2759.54 | 4946.74 |
| Tata | 88 | 2591.04 | 5560.37 |
| Hyundai | 120 | 1846.48 | 4021.87 |
| Kia | 42 | -1822.94 | 4114.54 |
| Volkswagen | 14 | -1053.32 | 4154.76 |
| Mahindra | 64 | 474.88 | 3789.75 |
| Honda | 58 | 435.27 | 4016.48 |

## Q53. How close are actual and predicted costs by impact point?

**Category:** Repair model  
**Business value:** Compare error patterns across collision zones.

```sql
SELECT Impact_Point, COUNT(*) AS holdout_claims, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_actual_cost_inr, ROUND(AVG(Predicted_Repair_Cost_INR), 2) AS avg_predicted_cost_inr, ROUND(AVG(Absolute_Error_INR), 2) AS mae_inr FROM holdout_predictions GROUP BY Impact_Point ORDER BY mae_inr DESC;
```

**Result:** 3 row(s) returned. Preview:
| Impact_Point | holdout_claims | avg_actual_cost_inr | avg_predicted_cost_inr | mae_inr |
| --- | --- | --- | --- | --- |
| Front | 280 | 15832.86 | 16373.74 | 4751.7 |
| Side | 176 | 15981.25 | 16762.79 | 4598.92 |
| Rear | 144 | 11279.86 | 13729.39 | 3961.14 |

## Q54. How does model MAE compare to a training-period mean baseline by brand?

**Category:** Repair model  
**Business value:** Compare predictions relative to the mean cost in the training period.

```sql
SELECT Vehicle_Brand, COUNT(*) AS holdout_claims, ROUND(AVG(Absolute_Error_INR), 2) AS model_mae_inr, ROUND(AVG(ABS(Actual_Repair_Cost_INR - (SELECT AVG(Actual_Repair_Cost_INR) FROM telematics_claims WHERE AccidentDate < (SELECT MIN(AccidentDate) FROM holdout_predictions)))), 2) AS benchmark_mae_inr FROM holdout_predictions GROUP BY Vehicle_Brand HAVING COUNT(*) >= 5 ORDER BY model_mae_inr DESC;
```

**Result:** 9 row(s) returned. Preview:
| Vehicle_Brand | holdout_claims | model_mae_inr | benchmark_mae_inr |
| --- | --- | --- | --- |
| Tata | 88 | 5560.37 | 14416.15 |
| Maruti Suzuki | 151 | 4946.74 | 14778.74 |
| Toyota | 34 | 4570.14 | 12826.3 |
| Volkswagen | 14 | 4154.76 | 13183.73 |
| Kia | 42 | 4114.54 | 15527.64 |
| Hyundai | 120 | 4021.87 | 12975.04 |
| Honda | 58 | 4016.48 | 14953.44 |
| Mahindra | 64 | 3789.75 | 12918.4 |

## Q55. Which brands combine high demand with low preferred in-stock coverage?

**Category:** Executive decisions  
**Business value:** Create a prioritized network improvement view.

```sql
WITH demand AS (SELECT Vehicle_Brand, COUNT(*) AS claim_count, AVG(Actual_Repair_Cost_INR) AS avg_cost FROM telematics_claims GROUP BY Vehicle_Brand), network AS (SELECT Brand_Specialization AS Vehicle_Brand, SUM(CASE WHEN Parts_Available = 1 AND Preferred_Partner = 1 THEN 1 ELSE 0 END) AS preferred_stock_garages, SUM(CASE WHEN Parts_Available = 1 THEN 1 ELSE 0 END) AS all_stock_garages FROM partner_garages GROUP BY Brand_Specialization) SELECT d.Vehicle_Brand, d.claim_count, ROUND(d.avg_cost, 2) AS avg_cost_inr, n.preferred_stock_garages, n.all_stock_garages, ROUND(1.0 * d.claim_count / NULLIF(n.preferred_stock_garages, 0), 2) AS claims_per_preferred_stock_garage FROM demand d JOIN network n ON d.Vehicle_Brand = n.Vehicle_Brand ORDER BY claims_per_preferred_stock_garage DESC;
```

**Result:** 12 row(s) returned. Preview:
| Vehicle_Brand | claim_count | avg_cost_inr | preferred_stock_garages | all_stock_garages | claims_per_preferred_stock_garage |
| --- | --- | --- | --- | --- | --- |
| Renault | 79 | 15472.15 | 1 | 2 | 79.0 |
| Hyundai | 588 | 18563.61 | 9 | 15 | 65.33 |
| Tata | 421 | 19952.49 | 7 | 7 | 60.14 |
| Honda | 278 | 15520.14 | 5 | 8 | 55.6 |
| Mahindra | 323 | 19768.11 | 6 | 7 | 53.83 |
| Maruti Suzuki | 804 | 13942.91 | 15 | 20 | 53.6 |
| Kia | 203 | 20340.39 | 4 | 10 | 50.75 |
| Volkswagen | 71 | 23945.07 | 2 | 2 | 35.5 |
