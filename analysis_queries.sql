CREATE DATABASE IF NOT EXISTS netflix_db;
USE netflix_db;

CREATE TABLE netflix_titles (
    show_id      VARCHAR(10)  PRIMARY KEY,
    type         VARCHAR(10),
    title        VARCHAR(200),
    director     VARCHAR(300),
    cast         TEXT,
    country      VARCHAR(200),
    date_added   VARCHAR(50),
    release_year INT,
    rating       VARCHAR(20),
    duration     VARCHAR(20),
    listed_in    VARCHAR(300),
    description  TEXT
);

-- Movie vs TV Show 비율
SELECT
    type,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM netflix_titles), 1) AS percentage
FROM netflix_titles
GROUP BY type;

-- 연도별 콘텐츠 추가 추이
SELECT
    YEAR(date_added) AS year_added,
    type,
    COUNT(*) AS count
FROM netflix_titles
WHERE date_added IS NOT NULL AND date_added != ''
GROUP BY year_added, type
ORDER BY year_added;

-- 나라별 콘텐츠 추가 추이
SELECT
    country,
    COUNT(*) AS count
FROM netflix_titles
WHERE country IS NOT NULL AND country != ''
GROUP BY country
ORDER BY count DESC
LIMIT 10;

-- 월별 콘텐츠 추가 패턴
SELECT
    MONTH(date_added) AS month_num,
    COUNT(*) AS count
FROM netflix_titles
WHERE date_added IS NOT NULL AND date_added != ''
GROUP BY month_num
ORDER BY month_num;


-- 시청 등급 분포
SELECT
    rating,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM netflix_titles WHERE rating IS NOT NULL AND rating NOT LIKE '%min%'), 1) AS percentage
FROM netflix_titles
WHERE rating IS NOT NULL 
  AND rating != ''
  AND rating NOT LIKE '%min%'
GROUP BY rating
ORDER BY count DESC;

-- 장르Top10
SELECT
    listed_in,
    COUNT(*) AS count
FROM netflix_titles
WHERE listed_in IS NOT NULL AND listed_in != ''
GROUP BY listed_in
ORDER BY count DESC
LIMIT 10;

-- 감독별 작품수
SELECT
    director,
    COUNT(*) AS count
FROM netflix_titles
WHERE director IS NOT NULL 
  AND director != ''
  AND type = 'Movie'
GROUP BY director
ORDER BY count DESC
LIMIT 10;

