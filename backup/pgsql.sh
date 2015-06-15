#!/bin/bash

pg_dump -h localhost -U point point | gzip - > "$2/pqsql-$1.sql.gz"
