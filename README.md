# smart-meter-duckdb
Repo to test duckdb plus Streamlit on EC2


## EC2 setup instructions


Install DuckDB

`wget https://github.com/duckdb/duckdb/releases/download/v0.9.1/duckdb_cli-linux-amd64.zip`

`unzip duckdb_cli-linux-amd64.zip`

`chmod +x duckdb`

`sudo mv duckdb /usr/local/bin/`

`rm duckdb_cli-linux-amd64.zip`


Create SSH key and setup git

`ssh-keygen -t ed25519 -C "david.sykes70@gmail.com" -f ~/.ssh/duck_db_deploy_key`

- Create a deploy key in EC2 and copy contents of `~/.ssh/duck_db_deploy_key.pub` to the key

`sudo yum update`

`sudo yum install git`

`touch ~/.ssh/config`

- Add the below to the config

```
Host github.com
  IdentityFile ~/.ssh/duck_db_deploy_key

```

Download project
`mkdir projects`

`mkdir projects/smart_data`

`cd projects/smart_data`

`git clone git@github.com:david-sykes/smart-meter-duckdb.git`


Install pyenv and pipenv
[https://gist.github.com/norsec0de/b863e2d99e251b848b5e9fece1c45f1a]

`pyenv install 3.10`

`pyenv global 3.10.13`

`pip install --upgrade pip`

`pip install --user pipenv`


Prep raw data

`cd /home/ec2-user/projects/smart_data/`

`wget https://data.london.gov.uk/download/smartmeter-energy-use-data-in-london-households/3527bf39-d93e-4071-8451-df2ade1ea4f2/LCL-FullData.zip`

`unzip LCL-FullData.zip`

`rm  LCL-FullData.zip`

`duckdb`

`CREATE TABLE readings AS SELECT * FROM read_csv_auto('CC_LCL-FullData.csv', HEADER=TRUE);`

`ALTER TABLE readings RENAME COLUMN "KWH/hh (per half hour)" TO "reading_value";`

`DELETE FROM readings WHERE reading_value = 'Null';`

`COPY readings TO 'readings.parquet' (FORMAT 'parquet', COMPRESSION 'ZSTD');`

- Exit duckdb and re-enter duckdb `duckdb`

`CREATE TABLE readings AS SELECT * FROM 'readings.parquet';`

`ALTER TABLE readings ALTER reading_value TYPE DECIMAL;`

`EXPORT DATABASE 'readings' (FORMAT 'parquet', COMPRESSION 'ZSTD');`

`rm readings.parquet`

`rm CC_LCL-FullData.csv`

Make port available

`cd smart-meter-duckdb`

`pipenv run streamlit run app.py`

- Find the port it is running on (mine is `8501`)
- Make sure that port is accepting TCP traffic in your security group using a custom TCP rule
