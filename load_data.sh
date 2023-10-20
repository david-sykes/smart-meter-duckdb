#!/bin/bash

echo "Downloading csv"

wget https://data.london.gov.uk/download/smartmeter-energy-use-data-in-london-households/3527bf39-d93e-4071-8451-df2ade1ea4f2/LCL-FullData.zip

echo "Unzipping"

unzip LCL-FullData.zip

rm LCL-FullData.zip

duckdb $1 <<EOF
CREATE TABLE readings AS SELECT * FROM read_csv_auto('CC_LCL-FullData.csv', HEADER=TRUE);
ALTER TABLE readings RENAME COLUMN "KWH/hh (per half hour)" TO "reading_value";
DELETE FROM readings WHERE reading_value = 'Null';
ALTER TABLE readings ALTER reading_value TYPE DECIMAL;
COPY readings TO 'readings.parquet' (FORMAT PARQUET);
-- Any other commands you'd like to run
EOF
