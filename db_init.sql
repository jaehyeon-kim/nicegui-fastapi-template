-- Create schema
CREATE SCHEMA IF NOT EXISTS demo;

-- Grant privileges on schema to the application user
GRANT ALL ON SCHEMA demo TO postgres;

-- Set search_path at the DB level
ALTER DATABASE dashboard SET search_path TO demo, public;
