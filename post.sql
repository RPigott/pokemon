-- Update hanging species
WITH alts AS (select id AS sp, alt_id AS alt FROM species WHERE id < 808),
bases AS (select sp.id, alts.sp, sn.name_en, sn.name_jp, sn.name_fr, sn.name_gr FROM species AS sp JOIN alts ON sp.alt_id = alts.alt JOIN species AS sn ON alts.sp = sn.id WHERE sp.id > 807)
UPDATE species SET name_en = bases.name_en, name_jp = bases.name_jp, name_fr = bases.name_fr, name_gr = bases.name_gr FROM bases WHERE species.id = bases.id;

-- Cluster species table
cluster species using species_pkey;
