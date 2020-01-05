ALTER TABLE class
  ADD COLUMN detail jsonb,
  ADD COLUMN fix jsonb,
  ADD COLUMN trap jsonb,
  ADD COLUMN example jsonb,
  ADD COLUMN source text,
  ADD COLUMN resource text
;
