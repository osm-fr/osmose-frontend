ALTER TABLE source RENAME TO sources;
ALTER TABLE sources RENAME CONSTRAINT source_pkey TO sources_pkey;
ALTER INDEX source_country_analyser RENAME TO sources_country_analyser;

ALTER TABLE source_password RENAME TO sources_password;
ALTER TABLE sources_password RENAME CONSTRAINT source_password_pkey TO sources_password_pkey;
ALTER TABLE sources_password RENAME CONSTRAINT source_password_source_fkey TO sources_password_source_id_fkey;
