CREATE TABLE abilities (
	id INTEGER PRIMARY KEY,
	name_en VARCHAR,
	name_jp VARCHAR,
	name_fr VARCHAR,
	name_gr VARCHAR
);

CREATE TABLE items (
	id INTEGER PRIMARY KEY,
	name_en VARCHAR,
	name_jp VARCHAR,
	name_fr VARCHAR,
	name_gr VARCHAR
);

CREATE TABLE types (
	id INTEGER PRIMARY KEY,
	name_en VARCHAR,
	name_jp VARCHAR,
	name_fr VARCHAR,
	name_gr VARCHAR
);

CREATE TABLE egg_groups (
	id INTEGER PRIMARY KEY,
	name_en VARCHAR
	-- name_jp VARCHAR,
	-- name_fr VARCHAR,
	-- name_gr VARCHAR
);

CREATE TABLE species (
	id INTEGER PRIMARY KEY,
	name_en VARCHAR,
	name_jp VARCHAR,
	name_fr VARCHAR,
	name_gr VARCHAR,
	hp SMALLINT,
	atk SMALLINT,
	def SMALLINT,
	spa SMALLINT,
	spd SMALLINT,
	spe SMALLINT,
	type1 SMALLINT REFERENCES types,
	type2 SMALLINT REFERENCES types,
	capture_rate SMALLINT,
	stage SMALLINT,
	ev_hp SMALLINT,
	ev_atk SMALLINT,
	ev_def SMALLINT,
	ev_spa SMALLINT,
	ev_spd SMALLINT,
	ev_spe SMALLINT,
	item1 SMALLINT REFERENCES items,
	item2 SMALLINT REFERENCES items,
	item3 SMALLINT REFERENCES items,
	gender_rate SMALLINT,
	hatch_cycles SMALLINT,
	base_happiness SMALLINT,
	exp_group VARCHAR,
	egg_group1 SMALLINT REFERENCES egg_groups,
	egg_group2 SMALLINT REFERENCES egg_groups,
	ability1 SMALLINT,
	ability2 SMALLINT,
	ability_hidden SMALLINT,
	escape_rate SMALLINT,
	alt_id SMALLINT,
	multiplicity SMALLINT,
	color VARCHAR,
	base_exp INTEGER,
	height FLOAT,
	weight FLOAT,
	local_variant BOOLEAN
);

CREATE TABLE forms (
	id INTEGER PRIMARY KEY,
	species INTEGER REFERENCES species,
	name_en VARCHAR,
	name_jp VARCHAR,
	name_fr VARCHAR,
	name_gr VARCHAR
);

CREATE TABLE evolution (
	id INTEGER PRIMARY KEY,
	species INTEGER REFERENCES species,
	method INTEGER,
	auxiliary INTEGER,
	target INTEGER REFERENCES species,
	target_form SMALLINT,
	level SMALLINT
);

CREATE TABLE moves (
	id INTEGER PRIMARY KEY,
	name_en VARCHAR,
	name_jp VARCHAR,
	name_fr VARCHAR,
	name_gr VARCHAR,
	type SMALLINT REFERENCES types,
	category VARCHAR,
	power SMALLINT,
	accuracy SMALLINT,
	pp SMALLINT,
	priority SMALLINT,
	min_hits SMALLINT,
	max_hits SMALLINT,
	effect INTEGER,
	effect_chance SMALLINT,
	effect_min_turns SMALLINT,
	effect_max_turns SMALLINT,
	crit_chance SMALLINT,
	flinch_chance SMALLINT,
	recoil SMALLINT,
	drain SMALLINT,
	heal SMALLINT,
	damage SMALLINT,
	stat1 SMALLINT,
	stat2 SMALLINT,
	stat3 SMALLINT,
	stat1_num SMALLINT,
	stat2_num SMALLINT,
	stat3_num SMALLINT,
	stat1_chance SMALLINT,
	stat2_chance SMALLINT,
	stat3_chance SMALLINT,
	dance BOOLEAN
);

CREATE TABLE levelup (
	species INTEGER REFERENCES species,
	move INTEGER REFERENCES moves,
	level SMALLINT
);

CREATE TABLE egg_moves (
	species INTEGER,
	move INTEGER REFERENCES moves
);
