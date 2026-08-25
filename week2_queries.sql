-- ============================================================
-- Flight Delay Analytics — Week 2 SQL Queries
-- Author: Sabhasachi Saha (Showmo)
-- Dataset: BTS 2024 Flight Delay Data (Kaggle), table: flights_raw
-- ============================================================


-- Query 1: Average arrival delay by carrier
-- Ranks airlines from worst to best average delay.
SELECT op_unique_carrier,
       ROUND(AVG(arr_delay), 2) AS avg_arr_delay,
       COUNT(*) AS num_flights
FROM flights_raw
WHERE arr_delay IS NOT NULL
GROUP BY op_unique_carrier
ORDER BY avg_arr_delay DESC;


-- Query 2: Average arrival delay by origin airport
-- Top 20 worst-performing airports by average delay.
SELECT origin,
       ROUND(AVG(arr_delay), 2) AS avg_arr_delay,
       COUNT(*) AS num_flights
FROM flights_raw
WHERE arr_delay IS NOT NULL
GROUP BY origin
ORDER BY avg_arr_delay DESC
LIMIT 20;


-- Query 3: Average arrival delay by month (seasonality)
-- Shows which months have the worst/best on-time performance.
SELECT month,
       ROUND(AVG(arr_delay), 2) AS avg_arr_delay,
       COUNT(*) AS num_flights
FROM flights_raw
WHERE arr_delay IS NOT NULL
GROUP BY month
ORDER BY month;


-- Query 4: On-time rate trend by month
-- "On-time" = arrival within 15 minutes of scheduled time (industry standard).
SELECT month,
       COUNT(*) AS total_flights,
       SUM(CASE WHEN arr_delay <= 15 THEN 1 ELSE 0 END) AS on_time_flights,
       ROUND(100.0 * SUM(CASE WHEN arr_delay <= 15 THEN 1 ELSE 0 END) / COUNT(*), 2) AS on_time_pct
FROM flights_raw
WHERE arr_delay IS NOT NULL
GROUP BY month
ORDER BY month;


-- Query 5: Top delay causes (totals across all flights)
-- Compares total minutes attributed to each delay cause category.
SELECT
    SUM(carrier_delay)       AS total_carrier_delay,
    SUM(weather_delay)       AS total_weather_delay,
    SUM(nas_delay)           AS total_nas_delay,
    SUM(security_delay)      AS total_security_delay,
    SUM(late_aircraft_delay) AS total_late_aircraft_delay
FROM flights_raw;
