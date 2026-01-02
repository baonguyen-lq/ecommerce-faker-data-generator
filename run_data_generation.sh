#!/bin/bash
set -e

echo " Starting ecommerce fake data generation..."

echo " Step 1: Creating database tables..."
poetry run python src/create_tables.py

if [ $? -eq 0 ]; then
    echo " Tables created successfully!"
else
    echo " Failed to create tables. Aborting."
    exit 1
fi

echo " Step 2: Generating and inserting fake data..."
poetry run python src/create_objects.py

if [ $? -eq 0 ]; then
    echo "Fake data inserted successfully!"
    echo "All done! Your database is now populated."
else
    echo "Failed to insert fake data."
    exit 1
fi