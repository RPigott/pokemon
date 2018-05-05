CREATE OR REPLACE FUNCTION hp_at(base integer, level integer, ev integer, iv integer) RETURNS integer AS $$
	BEGIN
		RETURN ((2 * base + iv + (ev / 4)) * level)/100 + level + 10;
	END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION hp_min(base integer) RETURNS integer AS $$
	BEGIN
		CASE
			WHEN base = 0 THEN
				RETURN 0;
			WHEN base = 1 THEN
				RETURN 1;
			ELSE
				RETURN hp_at(base, 100, 0, 0);
		END CASE;
	END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION hp_max(base integer) RETURNS integer AS $$
	BEGIN
		CASE
			WHEN base = 0 THEN
				RETURN 0;
			WHEN base = 1 THEN
				RETURN 1;
			ELSE
				RETURN hp_at(base, 100, 252, 31);
		END CASE;
	END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION stat_nil_at(base integer, level integer, ev integer, iv integer) RETURNS integer AS $$
	BEGIN
		RETURN (((2 * base + iv + (ev / 4)) * level)/100 + 5);
	END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION stat_neg_at(base integer, level integer, ev integer, iv integer) RETURNS integer AS $$
	BEGIN
		RETURN ((((2 * base + iv + (ev / 4)) * level)/100 + 5) * 9) / 10;
	END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION stat_pos_at(base integer, level integer, ev integer, iv integer) RETURNS integer AS $$
	BEGIN
		RETURN ((((2 * base + iv + (ev / 4)) * level)/100 + 5) * 11) / 10;
	END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION stat_max(base integer) RETURNS integer AS $$
	BEGIN
		RETURN stat_pos_at(base, 100, 252, 31);
	END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION stat_min(base integer) RETURNS integer AS $$
	BEGIN
		RETURN stat_neg_at(base, 100, 0, 0);
	END;
$$ LANGUAGE plpgsql;
