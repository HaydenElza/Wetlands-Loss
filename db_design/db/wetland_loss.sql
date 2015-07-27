-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler  version: 0.8.1-alpha1
-- PostgreSQL version: 9.4
-- Project Site: pgmodeler.com.br
-- Model Author: ---


-- Database creation must be done outside an multicommand file.
-- These commands were put in this file only for convenience.
-- -- object: new_database | type: DATABASE --
-- -- DROP DATABASE IF EXISTS new_database;
-- CREATE DATABASE new_database
-- ;
-- -- ddl-end --
-- 

-- object: public.results | type: TABLE --
-- DROP TABLE IF EXISTS public.results CASCADE;
CREATE TABLE public.results(
	corn_id char(11) NOT NULL,
	lost bit NOT NULL,
	iter varchar(10) NOT NULL,
	CONSTRAINT pkey_cornid_iter PRIMARY KEY (corn_id,iter)

);
-- ddl-end --
ALTER TABLE public.results OWNER TO postgres;
-- ddl-end --

-- object: public.desc | type: TABLE --
-- DROP TABLE IF EXISTS public.desc CASCADE;
CREATE TABLE public.desc(
	corn_id char(11) NOT NULL,
	eco bit NOT NULL,
	county varchar(3) NOT NULL,
	veg char NOT NULL,
	nlcd char(2) NOT NULL,
	CONSTRAINT pkey_cornid PRIMARY KEY (corn_id)

);
-- ddl-end --
ALTER TABLE public.desc OWNER TO postgres;
-- ddl-end --

-- object: public.eco | type: TABLE --
-- DROP TABLE IF EXISTS public.eco CASCADE;
CREATE TABLE public.eco(
	eco_code bit NOT NULL,
	eco_desc char(5) NOT NULL,
	CONSTRAINT pkey_eco PRIMARY KEY (eco_code)

);
-- ddl-end --
ALTER TABLE public.eco OWNER TO postgres;
-- ddl-end --

-- object: public.county | type: TABLE --
-- DROP TABLE IF EXISTS public.county CASCADE;
CREATE TABLE public.county(
	county_code char(3) NOT NULL,
	county_desc varchar(11) NOT NULL,
	CONSTRAINT pkey_county PRIMARY KEY (county_code)

);
-- ddl-end --
ALTER TABLE public.county OWNER TO postgres;
-- ddl-end --

-- object: public.vegtype | type: TABLE --
-- DROP TABLE IF EXISTS public.vegtype CASCADE;
CREATE TABLE public.vegtype(
	vegtype_code char NOT NULL,
	vegtype_desc varchar(22) NOT NULL,
	CONSTRAINT pkey_vegtype PRIMARY KEY (vegtype_code)

);
-- ddl-end --
ALTER TABLE public.vegtype OWNER TO postgres;
-- ddl-end --

-- object: public.nlcd | type: TABLE --
-- DROP TABLE IF EXISTS public.nlcd CASCADE;
CREATE TABLE public.nlcd(
	nlcd_code char(2) NOT NULL,
	nlcd_desc varchar(28) NOT NULL,
	CONSTRAINT pkey_nlcd PRIMARY KEY (nlcd_code)

);
-- ddl-end --
ALTER TABLE public.nlcd OWNER TO postgres;
-- ddl-end --

-- object: public.lost | type: TABLE --
-- DROP TABLE IF EXISTS public.lost CASCADE;
CREATE TABLE public.lost(
	lost_code bit NOT NULL,
	lost_desc varchar(8) NOT NULL,
	CONSTRAINT pkey_lost PRIMARY KEY (lost_code)

);
-- ddl-end --
ALTER TABLE public.lost OWNER TO postgres;
-- ddl-end --

-- object: fkey_cornid | type: CONSTRAINT --
-- ALTER TABLE public.results DROP CONSTRAINT IF EXISTS fkey_cornid CASCADE;
ALTER TABLE public.results ADD CONSTRAINT fkey_cornid FOREIGN KEY (corn_id)
REFERENCES public.desc (corn_id) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: fkey_lost | type: CONSTRAINT --
-- ALTER TABLE public.results DROP CONSTRAINT IF EXISTS fkey_lost CASCADE;
ALTER TABLE public.results ADD CONSTRAINT fkey_lost FOREIGN KEY (lost)
REFERENCES public.lost (lost_code) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: fkey_eco | type: CONSTRAINT --
-- ALTER TABLE public.desc DROP CONSTRAINT IF EXISTS fkey_eco CASCADE;
ALTER TABLE public.desc ADD CONSTRAINT fkey_eco FOREIGN KEY (eco)
REFERENCES public.eco (eco_code) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: fkey_county | type: CONSTRAINT --
-- ALTER TABLE public.desc DROP CONSTRAINT IF EXISTS fkey_county CASCADE;
ALTER TABLE public.desc ADD CONSTRAINT fkey_county FOREIGN KEY (county)
REFERENCES public.county (county_code) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: fkey_vegtype | type: CONSTRAINT --
-- ALTER TABLE public.desc DROP CONSTRAINT IF EXISTS fkey_vegtype CASCADE;
ALTER TABLE public.desc ADD CONSTRAINT fkey_vegtype FOREIGN KEY (veg)
REFERENCES public.vegtype (vegtype_code) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --

-- object: fkey_nlcd | type: CONSTRAINT --
-- ALTER TABLE public.desc DROP CONSTRAINT IF EXISTS fkey_nlcd CASCADE;
ALTER TABLE public.desc ADD CONSTRAINT fkey_nlcd FOREIGN KEY (nlcd)
REFERENCES public.nlcd (nlcd_code) MATCH FULL
ON DELETE NO ACTION ON UPDATE NO ACTION;
-- ddl-end --


