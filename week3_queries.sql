-- Week 3 — Flight Delay Analytics
-- Queries 6-10: Window Functions + Final Analysis

-- Query 6: Rank carriers by average arrival delay
SELECT
    op_unique_carrier,
    ROUND(AVG(arr_delay), 2) AS avg_arr_delay,
    RANK() OVER (ORDER BY AVG(arr_delay) DESC) AS delay_rank
FROM flights_raw
GROUP BY op_unique_carrier
ORDER BY delay_rank;

-- Query 7: Month-over-month change in average delay
SELECT
    month,
    ROUND(AVG(arr_delay), 2) AS avg_arr_delay,
    ROUND(AVG(arr_delay) - LAG(AVG(arr_delay)) OVER (ORDER BY month), 2) AS change_from_prev_month
FROM flights_raw
GROUP BY month
ORDER BY month;

-- Query 8: Delay cause breakdown (carrier vs weather vs NAS)
SELECT
    ROUND(SUM(carrier_delay), 0) AS total_carrier_delay,
    ROUND(SUM(weather_delay), 0) AS total_weather_delay,
    ROUND(SUM(nas_delay), 0) AS total_nas_delay,
    ROUND(100.0 * SUM(carrier_delay) / (SUM(carrier_delay) + SUM(weather_delay) + SUM(nas_delay)), 1) AS pct_carrier,
    ROUND(100.0 * SUM(weather_delay) / (SUM(carrier_delay) + SUM(weather_delay) + SUM(nas_delay)), 1) AS pct_weather,
    ROUND(100.0 * SUM(nas_delay) / (SUM(carrier_delay) + SUM(weather_delay) + SUM(nas_delay)), 1) AS pct_nas
FROM flights_raw;

-- Query 9: Worst routes by average delay (min. 30 flights)
SELECT
    origin,
    dest,
    ROUND(AVG(arr_delay), 2) AS avg_arr_delay,
    COUNT(*) AS num_flights
FROM flights_raw
GROUP BY origin, dest
HAVING num_flights >= 30
ORDER BY avg_arr_delay DESC
LIMIT 15;

-- Query 10: On-time rate by day of week
SELECT
    day_of_week,
    ROUND(100.0 * SUM(CASE WHEN arr_delay <= 15 THEN 1 ELSE 0 END) / COUNT(*), 1) AS on_time_pct
FROM flights_raw
GROUP BY day_of_week
ORDER BY day_of_week;
