-- MySQL 8 query bank. Import the source CSVs and routing/model output tables first.
-- Q01 [Portfolio overview]: What is the overall claims portfolio?
SELECT COUNT(*) AS claim_count, COUNT(DISTINCT VehicleID) AS distinct_vehicles, ROUND(SUM(Actual_Repair_Cost_INR), 2) AS total_repair_cost_inr, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS average_repair_cost_inr, MIN(AccidentDate) AS first_accident, MAX(AccidentDate) AS last_accident FROM telematics_claims;

-- Q02 [Portfolio overview]: How many repeat-incident vehicles are present?
SELECT COUNT(*) AS vehicles_with_multiple_claims FROM (SELECT VehicleID FROM telematics_claims GROUP BY VehicleID HAVING COUNT(*) > 1);

-- Q03 [Vehicle brand]: Which brands account for the most claims?
SELECT Vehicle_Brand, COUNT(*) AS claim_count, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM telematics_claims), 2) AS claim_share_pct FROM telematics_claims GROUP BY Vehicle_Brand ORDER BY claim_count DESC;

-- Q04 [Vehicle brand]: Which brands have the highest average repair cost?
SELECT Vehicle_Brand, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr, ROUND(SUM(Actual_Repair_Cost_INR), 2) AS total_cost_inr FROM telematics_claims GROUP BY Vehicle_Brand HAVING COUNT(*) >= 20 ORDER BY avg_cost_inr DESC;

-- Q05 [Vehicle brand]: What share of total repair spend comes from each brand?
SELECT Vehicle_Brand, ROUND(SUM(Actual_Repair_Cost_INR), 2) AS total_cost_inr, ROUND(100.0 * SUM(Actual_Repair_Cost_INR) / (SELECT SUM(Actual_Repair_Cost_INR) FROM telematics_claims), 2) AS cost_share_pct FROM telematics_claims GROUP BY Vehicle_Brand ORDER BY total_cost_inr DESC;

-- Q06 [Crash severity]: How does impact point relate to repair cost?
SELECT Impact_Point, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr, ROUND(AVG(Speed_At_Impact_kmh), 2) AS avg_impact_speed_kmh, ROUND(100.0 * AVG(Airbag_Deployed), 2) AS airbag_rate_pct FROM telematics_claims GROUP BY Impact_Point ORDER BY avg_cost_inr DESC;

-- Q07 [Crash severity]: How does airbag deployment relate to repair cost?
SELECT Airbag_Deployed, COUNT(*) AS claim_count, ROUND(AVG(Speed_At_Impact_kmh), 2) AS avg_speed_kmh, ROUND(AVG(G_Force_Impact), 2) AS avg_g_force, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY Airbag_Deployed ORDER BY Airbag_Deployed;

-- Q08 [Crash severity]: What are repair costs by impact-speed band?
SELECT CASE WHEN Speed_At_Impact_kmh < 25 THEN '01 Low (<25)' WHEN Speed_At_Impact_kmh < 50 THEN '02 Moderate (25-49)' WHEN Speed_At_Impact_kmh < 80 THEN '03 High (50-79)' ELSE '04 Very high (80+)' END AS speed_band, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr, ROUND(AVG(G_Force_Impact), 2) AS avg_g_force FROM telematics_claims GROUP BY speed_band ORDER BY speed_band;

-- Q09 [Crash severity]: How does G-force band relate to average cost?
SELECT CASE WHEN G_Force_Impact < 2 THEN '01 <2g' WHEN G_Force_Impact < 4 THEN '02 2-4g' WHEN G_Force_Impact < 7 THEN '03 4-7g' ELSE '04 7g+' END AS g_force_band, COUNT(*) AS claim_count, ROUND(AVG(Speed_At_Impact_kmh), 2) AS avg_speed_kmh, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY g_force_band ORDER BY g_force_band;

-- Q10 [Crash context]: Does weather condition correspond to different claim costs?
SELECT Weather_Condition, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr, ROUND(AVG(Speed_At_Impact_kmh), 2) AS avg_speed_kmh FROM telematics_claims GROUP BY Weather_Condition ORDER BY claim_count DESC;

-- Q11 [Crash context]: Which road types have the highest average repair cost?
SELECT Road_Type, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr, ROUND(AVG(Speed_At_Impact_kmh), 2) AS avg_speed_kmh FROM telematics_claims GROUP BY Road_Type ORDER BY avg_cost_inr DESC;

-- Q12 [Geography]: Which crash areas carry the largest repair spend?
SELECT Crash_Area, COUNT(*) AS claim_count, ROUND(SUM(Actual_Repair_Cost_INR), 2) AS total_cost_inr, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY Crash_Area ORDER BY total_cost_inr DESC;

-- Q13 [Time trends]: How many claims occur each month?
SELECT DATE_FORMAT(AccidentDate, '%Y-%m') AS accident_month, COUNT(*) AS claim_count, ROUND(SUM(Actual_Repair_Cost_INR), 2) AS total_cost_inr, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY accident_month ORDER BY accident_month;

-- Q14 [Time trends]: How does monthly claim count change from the prior month?
WITH monthly AS (SELECT DATE_FORMAT(AccidentDate, '%Y-%m') AS accident_month, COUNT(*) AS claim_count FROM telematics_claims GROUP BY accident_month) SELECT accident_month, claim_count, LAG(claim_count) OVER (ORDER BY accident_month) AS prior_month_claims, claim_count - LAG(claim_count) OVER (ORDER BY accident_month) AS month_over_month_change FROM monthly ORDER BY accident_month;

-- Q15 [Time trends]: Are claims more common on weekdays or weekends?
SELECT CASE WHEN (DAYOFWEEK(AccidentDate) - 1) IN (0,6) THEN 'Weekend' ELSE 'Weekday' END AS day_type, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY day_type;

-- Q16 [Time trends]: At what hours are incidents most frequent?
SELECT HOUR(AccidentDate) AS accident_hour, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY accident_hour ORDER BY claim_count DESC;

-- Q17 [Vehicle age]: How does vehicle age relate to repair cost?
SELECT CASE WHEN YEAR(AccidentDate) - Model_Year < 3 THEN '0-2 years' WHEN YEAR(AccidentDate) - Model_Year < 7 THEN '3-6 years' WHEN YEAR(AccidentDate) - Model_Year < 12 THEN '7-11 years' ELSE '12+ years' END AS vehicle_age_band, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY vehicle_age_band ORDER BY vehicle_age_band;

-- Q18 [Cost outliers]: What are the 15 most expensive claims?
SELECT ClaimID, AccidentDate, Vehicle_Brand, Crash_Area, Speed_At_Impact_kmh, G_Force_Impact, Airbag_Deployed, Actual_Repair_Cost_INR FROM telematics_claims ORDER BY Actual_Repair_Cost_INR DESC LIMIT 15;

-- Q19 [Cost outliers]: Which claims are above average cost by more than two standard deviations?
WITH stats AS (SELECT AVG(Actual_Repair_Cost_INR) AS avg_cost, (AVG(Actual_Repair_Cost_INR * Actual_Repair_Cost_INR) - AVG(Actual_Repair_Cost_INR) * AVG(Actual_Repair_Cost_INR)) AS var_cost FROM telematics_claims) SELECT c.ClaimID, c.Vehicle_Brand, c.Speed_At_Impact_kmh, c.G_Force_Impact, c.Actual_Repair_Cost_INR, ROUND(s.avg_cost, 2) AS portfolio_avg_cost FROM telematics_claims c CROSS JOIN stats s WHERE c.Actual_Repair_Cost_INR > s.avg_cost + 2 * SQRT(GREATEST(s.var_cost, 0)) ORDER BY c.Actual_Repair_Cost_INR DESC;

-- Q20 [Vehicle patterns]: Which vehicles have the most recorded incidents?
SELECT VehicleID, COUNT(*) AS incident_count, ROUND(SUM(Actual_Repair_Cost_INR), 2) AS total_repair_cost_inr, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_repair_cost_inr FROM telematics_claims GROUP BY VehicleID HAVING COUNT(*) > 1 ORDER BY incident_count DESC, total_repair_cost_inr DESC LIMIT 20;

-- Q21 [Vehicle patterns]: What is the average cost for repeat versus single-incident vehicles?
WITH vehicle_counts AS (SELECT VehicleID, COUNT(*) AS claim_count FROM telematics_claims GROUP BY VehicleID) SELECT CASE WHEN v.claim_count > 1 THEN 'Repeat vehicle' ELSE 'Single recorded incident' END AS vehicle_group, COUNT(*) AS claims, ROUND(AVG(c.Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims c JOIN vehicle_counts v ON c.VehicleID = v.VehicleID GROUP BY vehicle_group;

-- Q22 [Crash severity]: How is crash severity distributed by brand?
SELECT Vehicle_Brand, CASE WHEN Speed_At_Impact_kmh < 25 THEN 'Low' WHEN Speed_At_Impact_kmh < 50 THEN 'Moderate' WHEN Speed_At_Impact_kmh < 80 THEN 'High' ELSE 'Very high' END AS severity_band, COUNT(*) AS claim_count FROM telematics_claims GROUP BY Vehicle_Brand, severity_band ORDER BY Vehicle_Brand, claim_count DESC;

-- Q23 [Crash severity]: How does airbag deployment rate vary by speed band?
SELECT CASE WHEN Speed_At_Impact_kmh < 25 THEN 'Low (<25)' WHEN Speed_At_Impact_kmh < 50 THEN 'Moderate (25-49)' WHEN Speed_At_Impact_kmh < 80 THEN 'High (50-79)' ELSE 'Very high (80+)' END AS speed_band, COUNT(*) AS claim_count, ROUND(100.0 * AVG(Airbag_Deployed), 2) AS airbag_deployment_pct FROM telematics_claims GROUP BY speed_band ORDER BY speed_band;

-- Q24 [Crash severity]: What are average speed and costs by impact point?
SELECT Impact_Point, COUNT(*) AS claim_count, ROUND(AVG(Speed_At_Impact_kmh), 2) AS avg_speed_kmh, ROUND(AVG(G_Force_Impact), 2) AS avg_g_force, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY Impact_Point ORDER BY avg_speed_kmh DESC;

-- Q25 [Crash severity]: How do costs vary across speed quartiles?
WITH bands AS (SELECT *, NTILE(4) OVER (ORDER BY Speed_At_Impact_kmh) AS speed_quartile FROM telematics_claims) SELECT speed_quartile, COUNT(*) AS claim_count, ROUND(MIN(Speed_At_Impact_kmh), 2) AS min_speed, ROUND(MAX(Speed_At_Impact_kmh), 2) AS max_speed, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM bands GROUP BY speed_quartile ORDER BY speed_quartile;

-- Q26 [Crash severity]: Which features accompany the highest repair costs?
SELECT CASE WHEN Airbag_Deployed = 1 THEN 'Airbag deployed' ELSE 'No airbag deployment' END AS airbag_status, Impact_Point, COUNT(*) AS claim_count, ROUND(AVG(Speed_At_Impact_kmh), 2) AS avg_speed_kmh, ROUND(AVG(G_Force_Impact), 2) AS avg_g_force, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY airbag_status, Impact_Point ORDER BY avg_cost_inr DESC;

-- Q27 [Cost distribution]: What is the repair-cost distribution by percentile group?
WITH ranked AS (SELECT Actual_Repair_Cost_INR, NTILE(10) OVER (ORDER BY Actual_Repair_Cost_INR) AS cost_decile FROM telematics_claims) SELECT cost_decile, COUNT(*) AS claim_count, ROUND(MIN(Actual_Repair_Cost_INR), 2) AS min_cost_inr, ROUND(MAX(Actual_Repair_Cost_INR), 2) AS max_cost_inr, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM ranked GROUP BY cost_decile ORDER BY cost_decile;

-- Q28 [Time trends]: How do claim volume and average cost change by quarter?
SELECT CAST(YEAR(AccidentDate) AS CHAR) AS accident_year, CAST((CAST(LPAD(MONTH(AccidentDate), 2, '0') AS INTEGER) + 2) / 3 AS INTEGER) AS accident_quarter, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr, ROUND(SUM(Actual_Repair_Cost_INR), 2) AS total_cost_inr FROM telematics_claims GROUP BY accident_year, accident_quarter ORDER BY accident_year, accident_quarter;

-- Q29 [Time trends]: Are weekend incidents more expensive after grouping by impact point?
SELECT CASE WHEN (DAYOFWEEK(AccidentDate) - 1) IN (0,6) THEN 'Weekend' ELSE 'Weekday' END AS day_type, Impact_Point, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY day_type, Impact_Point ORDER BY day_type, avg_cost_inr DESC;

-- Q30 [Vehicle age]: What are claim counts and costs by vehicle-age band and brand?
SELECT Vehicle_Brand, CASE WHEN YEAR(AccidentDate) - Model_Year < 3 THEN '0-2 years' WHEN YEAR(AccidentDate) - Model_Year < 7 THEN '3-6 years' WHEN YEAR(AccidentDate) - Model_Year < 12 THEN '7-11 years' ELSE '12+ years' END AS vehicle_age_band, COUNT(*) AS claim_count, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_cost_inr FROM telematics_claims GROUP BY Vehicle_Brand, vehicle_age_band HAVING COUNT(*) >= 5 ORDER BY Vehicle_Brand, avg_cost_inr DESC;

-- Q31 [Garage network]: How many garages specialize in each vehicle brand?
SELECT Brand_Specialization AS Vehicle_Brand, COUNT(*) AS garage_count, SUM(CASE WHEN Parts_Available = 1 THEN 1 ELSE 0 END) AS in_stock_garages, SUM(CASE WHEN Preferred_Partner = 1 THEN 1 ELSE 0 END) AS preferred_garages FROM partner_garages GROUP BY Brand_Specialization ORDER BY garage_count DESC;

-- Q32 [Garage network]: What is parts availability by brand?
SELECT Brand_Specialization AS Vehicle_Brand, COUNT(*) AS garage_count, ROUND(100.0 * AVG(CASE WHEN Parts_Available = 1 THEN 1.0 ELSE 0.0 END), 2) AS in_stock_pct, SUM(CASE WHEN Parts_Available = 0 THEN 1 ELSE 0 END) AS out_of_stock_garages FROM partner_garages GROUP BY Brand_Specialization ORDER BY in_stock_pct;

-- Q33 [Garage network]: Which areas have the largest preferred-partner share?
SELECT Area, COUNT(*) AS garage_count, SUM(CASE WHEN Preferred_Partner = 1 THEN 1 ELSE 0 END) AS preferred_count, ROUND(100.0 * AVG(CASE WHEN Preferred_Partner = 1 THEN 1.0 ELSE 0.0 END), 2) AS preferred_share_pct FROM partner_garages GROUP BY Area ORDER BY preferred_share_pct DESC;

-- Q34 [Garage network]: Which areas have the greatest daily service capacity?
SELECT Area, COUNT(*) AS garage_count, SUM(Daily_Service_Capacity) AS total_daily_capacity, ROUND(AVG(Daily_Service_Capacity), 1) AS avg_capacity_per_garage FROM partner_garages GROUP BY Area ORDER BY total_daily_capacity DESC;

-- Q35 [Garage network]: Which garage-specialization groups have longer turnaround?
SELECT Brand_Specialization AS Vehicle_Brand, COUNT(*) AS garage_count, ROUND(AVG(Avg_Repair_Turnaround_Days), 2) AS avg_turnaround_days, ROUND(MIN(Avg_Repair_Turnaround_Days), 2) AS min_turnaround_days, ROUND(MAX(Avg_Repair_Turnaround_Days), 2) AS max_turnaround_days FROM partner_garages GROUP BY Brand_Specialization ORDER BY avg_turnaround_days DESC;

-- Q36 [Garage network]: How do simulated labor rates vary by area?
SELECT Area, COUNT(*) AS garage_count, ROUND(AVG(Labor_Rate_INR_Per_Hour), 2) AS avg_labor_rate_inr_hour, MIN(Labor_Rate_INR_Per_Hour) AS min_labor_rate, MAX(Labor_Rate_INR_Per_Hour) AS max_labor_rate FROM partner_garages GROUP BY Area ORDER BY avg_labor_rate_inr_hour DESC;

-- Q37 [Garage network]: Which vehicle brands have out-of-stock garages?
SELECT Brand_Specialization AS Vehicle_Brand, COUNT(*) AS garage_count, SUM(CASE WHEN Parts_Available = 0 THEN 1 ELSE 0 END) AS out_of_stock_count, ROUND(100.0 * AVG(CASE WHEN Parts_Available = 0 THEN 1.0 ELSE 0.0 END), 2) AS out_of_stock_pct FROM partner_garages GROUP BY Brand_Specialization HAVING out_of_stock_count > 0 ORDER BY out_of_stock_pct DESC;

-- Q38 [Garage coverage]: Is garage supply proportional to the claim mix by brand?
WITH demand AS (SELECT Vehicle_Brand, COUNT(*) AS claim_count FROM telematics_claims GROUP BY Vehicle_Brand), supply AS (SELECT Brand_Specialization AS Vehicle_Brand, SUM(CASE WHEN Parts_Available = 1 THEN 1 ELSE 0 END) AS eligible_garages FROM partner_garages GROUP BY Brand_Specialization), totals AS (SELECT SUM(claim_count) AS total_claims FROM demand), total_supply AS (SELECT SUM(eligible_garages) AS total_garages FROM supply) SELECT d.Vehicle_Brand, d.claim_count, s.eligible_garages, ROUND(100.0 * d.claim_count / t.total_claims, 2) AS demand_share_pct, ROUND(100.0 * s.eligible_garages / ts.total_garages, 2) AS eligible_supply_share_pct, ROUND(1.0 * d.claim_count / NULLIF(s.eligible_garages, 0), 2) AS claims_per_eligible_garage FROM demand d JOIN supply s ON d.Vehicle_Brand = s.Vehicle_Brand CROSS JOIN totals t CROSS JOIN total_supply ts ORDER BY claims_per_eligible_garage DESC;

-- Q39 [Garage coverage]: Which brands have the fewest in-stock preferred garages?
SELECT Brand_Specialization AS Vehicle_Brand, SUM(CASE WHEN Parts_Available = 1 AND Preferred_Partner = 1 THEN 1 ELSE 0 END) AS preferred_in_stock_garages, SUM(CASE WHEN Parts_Available = 1 THEN 1 ELSE 0 END) AS all_in_stock_garages FROM partner_garages GROUP BY Brand_Specialization ORDER BY preferred_in_stock_garages ASC, all_in_stock_garages ASC;

-- Q40 [Garage coverage]: What is the average capacity-to-turnaround profile by area?
SELECT Area, COUNT(*) AS garage_count, ROUND(AVG(Daily_Service_Capacity), 2) AS avg_daily_capacity, ROUND(AVG(Avg_Repair_Turnaround_Days), 2) AS avg_turnaround_days, ROUND(AVG(Daily_Service_Capacity / NULLIF(Avg_Repair_Turnaround_Days, 0)), 2) AS capacity_per_turnaround_day FROM partner_garages GROUP BY Area ORDER BY capacity_per_turnaround_day DESC;

-- Q41 [Routing operations]: How many routes used the preferred-partner fallback?
SELECT Preferred_Fallback_Used, COUNT(*) AS claim_count, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM garage_routing), 2) AS share_pct FROM garage_routing GROUP BY Preferred_Fallback_Used;

-- Q42 [Routing operations]: What are average route distance and cycle time by brand?
SELECT Vehicle_Brand, COUNT(*) AS routed_claims, ROUND(AVG(Recommended_Garage_Distance_km), 2) AS avg_distance_km, ROUND(AVG(Recommended_Garage_Travel_Minutes), 1) AS avg_travel_minutes, ROUND(AVG(Recommended_Garage_Turnaround_Days), 2) AS avg_turnaround_days, ROUND(AVG(Recommended_Garage_Est_Cycle_Hours), 2) AS avg_estimated_cycle_hours FROM garage_routing GROUP BY Vehicle_Brand ORDER BY avg_estimated_cycle_hours DESC;

-- Q43 [Routing operations]: Which garages receive the most routing recommendations?
SELECT r.Recommended_GarageID, g.Garage_Name, g.Area, g.Brand_Specialization, COUNT(*) AS recommended_claims, g.Daily_Service_Capacity, ROUND(1.0 * COUNT(*) / g.Daily_Service_Capacity, 2) AS claims_per_capacity_unit_proxy FROM garage_routing r JOIN partner_garages g ON r.Recommended_GarageID = g.GarageID GROUP BY r.Recommended_GarageID, g.Garage_Name, g.Area, g.Brand_Specialization, g.Daily_Service_Capacity ORDER BY recommended_claims DESC LIMIT 20;

-- Q44 [Routing operations]: Which crash areas have the longest average garage route?
SELECT Crash_Area, COUNT(*) AS routed_claims, ROUND(AVG(Recommended_Garage_Distance_km), 2) AS avg_distance_km, ROUND(MAX(Recommended_Garage_Distance_km), 2) AS max_distance_km, ROUND(AVG(Recommended_Garage_Travel_Minutes), 1) AS avg_travel_minutes FROM garage_routing GROUP BY Crash_Area ORDER BY avg_distance_km DESC;

-- Q45 [Routing operations]: How often is the balanced recommendation farther than the nearest eligible garage?
SELECT COUNT(*) AS claims_routed, SUM(CASE WHEN Recommended_GarageID <> Nearest_Eligible_GarageID THEN 1 ELSE 0 END) AS recommendation_differs_from_nearest, ROUND(100.0 * AVG(CASE WHEN Recommended_GarageID <> Nearest_Eligible_GarageID THEN 1.0 ELSE 0.0 END), 2) AS changed_recommendation_pct, ROUND(AVG(Recommended_Garage_Distance_km - Nearest_Eligible_Garage_Distance_km), 3) AS avg_extra_distance_km FROM garage_routing;

-- Q46 [Routing operations]: How many claims are routed beyond 10 kilometres?
SELECT COUNT(*) AS claims_over_10km, ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM garage_routing), 2) AS share_pct, ROUND(AVG(Recommended_Garage_Distance_km), 2) AS avg_distance_over_10km FROM garage_routing WHERE Recommended_Garage_Distance_km > 10;

-- Q47 [Routing operations]: What is routing distance by garage policy?
SELECT Candidate_Policy, COUNT(*) AS claims, ROUND(AVG(Recommended_Garage_Distance_km), 2) AS avg_distance_km, ROUND(AVG(Recommended_Garage_Turnaround_Days), 2) AS avg_turnaround_days, ROUND(AVG(Recommended_Garage_Est_Cycle_Hours), 2) AS avg_cycle_hours FROM garage_routing GROUP BY Candidate_Policy ORDER BY claims DESC;

-- Q48 [Routing operations]: Where are route recommendation counts concentrated?
SELECT Crash_Area, Recommended_Garage_Area, COUNT(*) AS route_count, ROUND(AVG(Recommended_Garage_Distance_km), 2) AS avg_distance_km FROM garage_routing GROUP BY Crash_Area, Recommended_Garage_Area ORDER BY route_count DESC LIMIT 25;

-- Q49 [Repair model]: What is holdout prediction error by impact-speed band?
SELECT CASE WHEN Speed_At_Impact_kmh < 25 THEN 'Low (<25)' WHEN Speed_At_Impact_kmh < 50 THEN 'Moderate (25-49)' WHEN Speed_At_Impact_kmh < 80 THEN 'High (50-79)' ELSE 'Very high (80+)' END AS speed_band, COUNT(*) AS holdout_claims, ROUND(AVG(Absolute_Error_INR), 2) AS mae_inr, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_actual_cost_inr, ROUND(AVG(Predicted_Repair_Cost_INR), 2) AS avg_predicted_cost_inr FROM holdout_predictions GROUP BY speed_band ORDER BY speed_band;

-- Q50 [Repair model]: Which brands have the largest holdout prediction errors?
SELECT Vehicle_Brand, COUNT(*) AS holdout_claims, ROUND(AVG(Absolute_Error_INR), 2) AS mae_inr, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_actual_cost_inr, ROUND(AVG(Predicted_Repair_Cost_INR), 2) AS avg_predicted_cost_inr FROM holdout_predictions GROUP BY Vehicle_Brand HAVING COUNT(*) >= 5 ORDER BY mae_inr DESC;

-- Q51 [Repair model]: What are the most poorly predicted holdout claims?
SELECT ClaimID, AccidentDate, Vehicle_Brand, Speed_At_Impact_kmh, G_Force_Impact, Airbag_Deployed, Actual_Repair_Cost_INR, Predicted_Repair_Cost_INR, Absolute_Error_INR FROM holdout_predictions ORDER BY Absolute_Error_INR DESC LIMIT 20;

-- Q52 [Repair model]: Does prediction bias differ across vehicle makes?
SELECT Vehicle_Brand, COUNT(*) AS holdout_claims, ROUND(AVG(Signed_Error_INR), 2) AS mean_signed_error_inr, ROUND(AVG(Absolute_Error_INR), 2) AS mean_absolute_error_inr FROM holdout_predictions GROUP BY Vehicle_Brand HAVING COUNT(*) >= 5 ORDER BY ABS(AVG(Signed_Error_INR)) DESC;

-- Q53 [Repair model]: How close are actual and predicted costs by impact point?
SELECT Impact_Point, COUNT(*) AS holdout_claims, ROUND(AVG(Actual_Repair_Cost_INR), 2) AS avg_actual_cost_inr, ROUND(AVG(Predicted_Repair_Cost_INR), 2) AS avg_predicted_cost_inr, ROUND(AVG(Absolute_Error_INR), 2) AS mae_inr FROM holdout_predictions GROUP BY Impact_Point ORDER BY mae_inr DESC;

-- Q54 [Repair model]: How does model MAE compare to a training-period mean baseline by brand?
SELECT Vehicle_Brand, COUNT(*) AS holdout_claims, ROUND(AVG(Absolute_Error_INR), 2) AS model_mae_inr, ROUND(AVG(ABS(Actual_Repair_Cost_INR - (SELECT AVG(Actual_Repair_Cost_INR) FROM telematics_claims WHERE AccidentDate < (SELECT MIN(AccidentDate) FROM holdout_predictions)))), 2) AS benchmark_mae_inr FROM holdout_predictions GROUP BY Vehicle_Brand HAVING COUNT(*) >= 5 ORDER BY model_mae_inr DESC;

-- Q55 [Executive decisions]: Which brands combine high demand with low preferred in-stock coverage?
WITH demand AS (SELECT Vehicle_Brand, COUNT(*) AS claim_count, AVG(Actual_Repair_Cost_INR) AS avg_cost FROM telematics_claims GROUP BY Vehicle_Brand), network AS (SELECT Brand_Specialization AS Vehicle_Brand, SUM(CASE WHEN Parts_Available = 1 AND Preferred_Partner = 1 THEN 1 ELSE 0 END) AS preferred_stock_garages, SUM(CASE WHEN Parts_Available = 1 THEN 1 ELSE 0 END) AS all_stock_garages FROM partner_garages GROUP BY Brand_Specialization) SELECT d.Vehicle_Brand, d.claim_count, ROUND(d.avg_cost, 2) AS avg_cost_inr, n.preferred_stock_garages, n.all_stock_garages, ROUND(1.0 * d.claim_count / NULLIF(n.preferred_stock_garages, 0), 2) AS claims_per_preferred_stock_garage FROM demand d JOIN network n ON d.Vehicle_Brand = n.Vehicle_Brand ORDER BY claims_per_preferred_stock_garage DESC;

