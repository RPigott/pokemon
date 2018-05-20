-- Update hanging species
WITH alts AS (select id AS sp, alt_id AS alt FROM species WHERE id < 808),
bases AS (select sp.id, alts.sp, sn.name_en, sn.name_jp, sn.name_fr, sn.name_gr FROM species AS sp JOIN alts ON sp.alt_id = alts.alt JOIN species AS sn ON alts.sp = sn.id WHERE sp.id > 807)
UPDATE species SET name_en = bases.name_en, name_jp = bases.name_jp, name_fr = bases.name_fr, name_gr = bases.name_gr FROM bases WHERE species.id = bases.id;

-- Cluster species table
cluster species using species_pkey;

-- Make convenient species table
CREATE MATERIALIZED VIEW species_en AS
  SELECT DISTINCT sp.id,                                                 +
     sp.name_en AS name,                                                 +
     fm.name_en AS form,                                                 +
     t1.name_en AS type1,                                                +
     t2.name_en AS type2,                                                +
     sp.hp,                                                              +
     sp.atk,                                                             +
     sp.def,                                                             +
     sp.spa,                                                             +
     sp.spd,                                                             +
     sp.spe,                                                             +
     (((((sp.hp + sp.atk) + sp.def) + sp.spa) + sp.spd) + sp.spe) AS bst,+
     ab1.name_en AS ability1,                                            +
     ab2.name_en AS ability2,                                            +
     ah.name_en AS hidden_ability,                                       +
     eg1.name_en AS egg_group1,                                          +
     eg2.name_en AS egg_group2                                           +
    FROM ((((((((species sp                                              +
      JOIN forms fm ON ((sp.id = fm.species)))                           +
      JOIN types t1 ON ((sp.type1 = t1.id)))                             +
      FULL JOIN types t2 ON ((sp.type2 = t2.id)))                        +
      JOIN egg_groups eg1 ON ((sp.egg_group1 = eg1.id)))                 +
      FULL JOIN egg_groups eg2 ON ((sp.egg_group2 = eg2.id)))            +
      JOIN abilities ab1 ON ((sp.ability1 = ab1.id)))                    +
      JOIN abilities ab2 ON ((sp.ability2 = ab2.id)))                    +
      JOIN abilities ah ON ((sp.ability_hidden = ah.id)))                +
   ORDER BY sp.id;
