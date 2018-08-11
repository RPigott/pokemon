-- Update hanging species
WITH alts AS (select id AS sp, alt_id AS alt FROM species WHERE id < 808),
bases AS (select sp.id, alts.sp, sn.name_en, sn.name_jp, sn.name_fr, sn.name_gr, sn.name_kr FROM species AS sp JOIN alts ON sp.alt_id = alts.alt JOIN species AS sn ON alts.sp = sn.id WHERE sp.id > 807)
UPDATE species SET name_en = bases.name_en, name_jp = bases.name_jp, name_fr = bases.name_fr, name_gr = bases.name_gr, name_kr = bases.name_kr FROM bases WHERE species.id = bases.id;

-- Cluster species table
cluster species using species_pkey;

-- Make convenient species table
CREATE MATERIALIZED VIEW species_en AS
  SELECT DISTINCT sp.id,                                                 
     sp.name_en AS name,                                                 
     fm.name_en AS form,                                                 
     t1.name_en AS type1,                                                
     t2.name_en AS type2,                                                
     sp.hp,                                                              
     sp.atk,                                                             
     sp.def,                                                             
     sp.spa,                                                             
     sp.spd,                                                             
     sp.spe,                                                             
     (sp.hp + sp.atk + sp.def + sp.spa + sp.spd + sp.spe) AS bst,
     ab1.name_en AS ability1,                                            
     ab2.name_en AS ability2,                                            
     ah.name_en AS hidden_ability,                                       
     eg1.name_en AS egg_group1,                                          
     eg2.name_en AS egg_group2                                           
    FROM ((((((((species sp                                              
      JOIN forms fm ON ((sp.id = fm.species)))                           
      JOIN types t1 ON ((sp.type1 = t1.id)))                             
      FULL JOIN types t2 ON ((sp.type2 = t2.id)))                        
      JOIN egg_groups eg1 ON ((sp.egg_group1 = eg1.id)))                 
      FULL JOIN egg_groups eg2 ON ((sp.egg_group2 = eg2.id)))            
      JOIN abilities ab1 ON ((sp.ability1 = ab1.id)))                    
      JOIN abilities ab2 ON ((sp.ability2 = ab2.id)))                    
      JOIN abilities ah ON ((sp.ability_hidden = ah.id)))                
   ORDER BY sp.id;

-- Make convenient egg moves table
CREATE MATERIALIZED VIEW egg_learnset AS
WITH recursive eml AS (
	SELECT sp.id, sp.name, sp.form, mv.id AS mvid, mv.name_en AS move FROM species_en AS sp join egg_moves AS el on sp.id = el.species join moves AS mv on el.move = mv.id
	UNION
	SELECT ta.id, ta.name, ta.form, mv.id AS mvid, mv.name_en AS move FROM eml join evolution AS ev on eml.id = ev.species join species_en AS ta on ta.id = ev.target join moves AS mv on eml.mvid = mv.id
) SELECT * FROM eml ORDER BY id, mvid;

-- Make convenient learnset table
CREATE MATERIALIZED VIEW learnset AS
SELECT id, name, form, method, mvid, move from (
	SELECT sp.id, sp.name, sp.form, concat('TM ', tms.id) as method, tms.id + 100 as aux, mv.id as mvid, mv.name_en as move from species_en as sp join tm_learnset as tml on sp.id = tml.species join tm_moves as tms on tml.tm = tms.id join moves as mv on tms.move = mv.id
	UNION
	SELECT sp.id, sp.name, sp.form, concat('Level ', level) as method, level as aux, mv.id as mvid, mv.name_en as move from species_en as sp join levelup as lvl on sp.id = lvl.species join moves as mv on lvl.move = mv.id
	UNION
	SELECT sp.id, sp.name, sp.form, 'Tutor' as method, null as aux, mv.id as mvid, mv.name_en as move from species_en as sp join tutor_learnset as ttl on sp.id = ttl.species join tutor_moves as ttm on ttl.tutor = ttm.id join moves as mv on ttm.move = mv.id
	UNION
	SELECT id, name, form, 'Egg' as method, null as aux, mvid, move from egg_learnset order by id, aux, method, mvid
) as tbl;
