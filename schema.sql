--
-- PostgreSQL database dump
--

-- Dumped from database version 9.3.6
-- Dumped by pg_dump version 9.5.5

--
-- Name: attendance_records; Type: TABLE; Schema: public; Owner: cwuepekp
--

CREATE TABLE attendance_records (
    sid integer NOT NULL,
    seid integer NOT NULL
);

--
-- Name: courses; Type: TABLE; Schema: public; Owner: cwuepekp
--

CREATE TABLE courses (
    cid integer NOT NULL,
    name text,
    start_time time without time zone,
    end_time time without time zone,
    start_date date,
    end_date date,
    day integer,
    active integer
);

--
-- Name: courses_cid_seq; Type: SEQUENCE; Schema: public; Owner: cwuepekp
--

CREATE SEQUENCE courses_cid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

--
-- Name: courses_cid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cwuepekp
--


--
-- Name: enrolled_in; Type: TABLE; Schema: public; Owner: cwuepekp
--

CREATE TABLE enrolled_in (
    sid integer NOT NULL,
    cid integer NOT NULL
);


--
-- Name: foo; Type: TABLE; Schema: public; Owner: cwuepekp
--

CREATE TABLE foo (
    email text
);


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: cwuepekp
--

CREATE TABLE sessions (
    seid integer NOT NULL,
    cid integer,
    secret text,
    expires time without time zone,
    day date
);


--
-- Name: sessions_seid_seq; Type: SEQUENCE; Schema: public; Owner: cwuepekp
--

CREATE SEQUENCE sessions_seid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sessions_seid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cwuepekp
--

ALTER SEQUENCE sessions_seid_seq OWNED BY sessions.seid;


--
-- Name: students; Type: TABLE; Schema: public; Owner: cwuepekp
--

CREATE TABLE students (
    sid integer NOT NULL,
    name text,
    email text,
    uni text
);


--
-- Name: teachers; Type: TABLE; Schema: public; Owner: cwuepekp
--

CREATE TABLE teachers (
    tid integer NOT NULL,
    name text,
    email text
);


--
-- Name: teaches; Type: TABLE; Schema: public; Owner: cwuepekp
--

CREATE TABLE teaches (
    tid integer NOT NULL,
    cid integer NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: cwuepekp
--

CREATE TABLE users (
    uid integer NOT NULL,
    name text,
    family_name text,
    email text
);


--
-- Name: users_uid_seq; Type: SEQUENCE; Schema: public; Owner: cwuepekp
--

CREATE SEQUENCE users_uid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_uid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cwuepekp
--

ALTER SEQUENCE users_uid_seq OWNED BY users.uid;


--
-- Name: cid; Type: DEFAULT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY courses ALTER COLUMN cid SET DEFAULT nextval('courses_cid_seq'::regclass);


--
-- Name: seid; Type: DEFAULT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY sessions ALTER COLUMN seid SET DEFAULT nextval('sessions_seid_seq'::regclass);


--
-- Name: uid; Type: DEFAULT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY users ALTER COLUMN uid SET DEFAULT nextval('users_uid_seq'::regclass);


--
-- Name: attendance_records_pkey; Type: CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY attendance_records
    ADD CONSTRAINT attendance_records_pkey PRIMARY KEY (sid, seid);


--
-- Name: courses_pkey; Type: CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY courses
    ADD CONSTRAINT courses_pkey PRIMARY KEY (cid);


--
-- Name: enrolled_in_pkey; Type: CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY enrolled_in
    ADD CONSTRAINT enrolled_in_pkey PRIMARY KEY (sid, cid);


--
-- Name: foo_email_key; Type: CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY foo
    ADD CONSTRAINT foo_email_key UNIQUE (email);


--
-- Name: sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (seid);


--
-- Name: students_pkey; Type: CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY students
    ADD CONSTRAINT students_pkey PRIMARY KEY (sid);


--
-- Name: students_uni_key; Type: CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY students
    ADD CONSTRAINT students_uni_key UNIQUE (uni);


--
-- Name: teachers_pkey; Type: CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY teachers
    ADD CONSTRAINT teachers_pkey PRIMARY KEY (tid);


--
-- Name: teaches_pkey; Type: CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY teaches
    ADD CONSTRAINT teaches_pkey PRIMARY KEY (tid, cid);


--
-- Name: users_email_key; Type: CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users_pkey; Type: CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (uid);


--
-- Name: attendance_records_seid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY attendance_records
    ADD CONSTRAINT attendance_records_seid_fkey FOREIGN KEY (seid) REFERENCES sessions(seid) ON DELETE CASCADE;


--
-- Name: attendance_records_sid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY attendance_records
    ADD CONSTRAINT attendance_records_sid_fkey FOREIGN KEY (sid) REFERENCES students(sid) ON DELETE CASCADE;


--
-- Name: enrolled_in_cid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY enrolled_in
    ADD CONSTRAINT enrolled_in_cid_fkey FOREIGN KEY (cid) REFERENCES courses(cid) ON DELETE CASCADE;


--
-- Name: enrolled_in_sid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY enrolled_in
    ADD CONSTRAINT enrolled_in_sid_fkey FOREIGN KEY (sid) REFERENCES students(sid) ON DELETE CASCADE;


--
-- Name: sessions_cid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY sessions
    ADD CONSTRAINT sessions_cid_fkey FOREIGN KEY (cid) REFERENCES courses(cid) ON DELETE CASCADE;


--
-- Name: students_sid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY students
    ADD CONSTRAINT students_sid_fkey FOREIGN KEY (sid) REFERENCES users(uid);


--
-- Name: teachers_tid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY teachers
    ADD CONSTRAINT teachers_tid_fkey FOREIGN KEY (tid) REFERENCES users(uid);


--
-- Name: teaches_cid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY teaches
    ADD CONSTRAINT teaches_cid_fkey FOREIGN KEY (cid) REFERENCES courses(cid) ON DELETE CASCADE;


--
-- Name: teaches_tid_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cwuepekp
--

ALTER TABLE ONLY teaches
    ADD CONSTRAINT teaches_tid_fkey FOREIGN KEY (tid) REFERENCES teachers(tid) ON DELETE CASCADE;


CREATE TABLE change_requests (
  sid integer NOT NULL,
  seid integer NOT NULL,
  message text
);
ALTER TABLE change_requests ADD CONSTRAINT change_requests_sid_fkey FOREIGN KEY (sid) REFERENCES students(sid) ON DELETE CASCADE;
ALTER TABLE change_requests ADD CONSTRAINT change_requests_seid_fkey FOREIGN KEY (seid) REFERENCES sessions(seid) ON DELETE CASCADE;
ALTER TABLE change_requests ADD CONSTRAINT change_requests_pkey PRIMARY KEY (sid, seid);
alter table change_requests add column status int default 0;

--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

--
-- PostgreSQL database dump complete
--
