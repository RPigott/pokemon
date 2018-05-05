createdb pokemon
psql -d pokemon < init.sql
psql -d pokemon < func.sql
python make_tables.py
psql -d pokemon < post.sql
