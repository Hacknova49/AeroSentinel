-- A2: PostgreSQL + PostGIS + TimescaleDB. Owner: member 1.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS regions (
  region_id TEXT PRIMARY KEY,
  name      TEXT NOT NULL,
  boundary  GEOGRAPHY(POLYGON, 4326)
);

CREATE TABLE IF NOT EXISTS zones (
  zone_id   TEXT PRIMARY KEY,
  region_id TEXT NOT NULL REFERENCES regions(region_id),
  boundary  GEOGRAPHY(POLYGON, 4326)
);

CREATE TABLE IF NOT EXISTS observations (
  id         TEXT NOT NULL,
  region_id  TEXT NOT NULL,
  zone_id    TEXT NOT NULL,
  patrol_id  TEXT NOT NULL,
  sensor     TEXT NOT NULL,
  ts         TIMESTAMPTZ NOT NULL,
  position   GEOGRAPHY(POINTZ, 4326) NOT NULL,
  image_uri  TEXT,
  readings   JSONB NOT NULL DEFAULT '{}',
  PRIMARY KEY (id, ts)
);
SELECT create_hypertable('observations', 'ts', if_not_exists => TRUE);
CREATE INDEX IF NOT EXISTS observations_zone_ts ON observations (zone_id, ts DESC);

CREATE TABLE IF NOT EXISTS detections (id TEXT PRIMARY KEY, observation_id TEXT NOT NULL, payload JSONB NOT NULL);
CREATE TABLE IF NOT EXISTS measurements (id TEXT PRIMARY KEY, detection_id TEXT NOT NULL, payload JSONB NOT NULL);
CREATE TABLE IF NOT EXISTS risk_scores (
  zone_id TEXT NOT NULL, hazard TEXT NOT NULL, ts TIMESTAMPTZ NOT NULL, payload JSONB NOT NULL,
  PRIMARY KEY (zone_id, hazard, ts)
);
SELECT create_hypertable('risk_scores', 'ts', if_not_exists => TRUE);
CREATE TABLE IF NOT EXISTS alerts (
  id TEXT PRIMARY KEY, dedupe_key TEXT NOT NULL, status TEXT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL, payload JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS alerts_dedupe ON alerts (dedupe_key, status);
