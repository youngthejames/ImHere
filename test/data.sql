insert into users (name, family_name, email) values ('Leeroy', 'Jenkins', 'lj1337@columbia.edu');
insert into users (name, family_name, email) values ('Matt', 'Mallett', 'mm4673@columbia.edu');

/* student 1, uid = 3 */
insert into users (name, family_name, email) values ('Dave', 'Student', 'ds9876@columbia.edu');
insert into students (sid, uni) values (3, 'ds9876');

/* teacher 1, uid = 4 */
insert into users (name, family_name, email) values ('Douglas', 'Teacher', 'dougs@cs.columbia.edu');
insert into teachers (tid) values (4);

/* student 2, uid = 5 */
insert into users (name, family_name, email) values ('Grommash', 'Hellscream', 'gh1234@columbia.edu');
insert into students (sid, uni) values (5, 'gh1234');

/* student 3, uid = 6 */
insert into users (name, family_name, email) values ('Jaina', 'Proudmoore', 'jp9122@columbia.edu');
insert into students (sid, uni) values (6, 'jp9122');

/* teacher 2 uid 7 */
insert into users (name, family_name, email) values ('New', 'Teacher', 'newt@cs.columbia.edu');
insert into teachers (tid) values (7);

/* student 4, uid 8 */
insert into users (name, family_name, email) values ('Sylvanas', 'Windrunner', 'sw1234@columbia.edu');
insert into students (sid, uni) values (8, 'sw1234');

/* uid 9 */
insert into users (name, family_name, email) values ('Unregistered', 'User', 'uu0000@columbia.edu');

/* uid 10, 11 */
insert into users (name, family_name, email) values ('nota', 'teacher', 'nota@teacher.com');
/* 11 is a teacher */
insert into users (name, family_name, email) values ('isa', 'teacher', 'isa@teacher.com');
insert into teachers (tid) values (11);
/* 12 is a teacher, teaches the class to test adding teachers */
insert into users (name, family_name, email) values ('add_teacher', 'teacher', 'add@teacher.com');
insert into teachers (tid) values (12);

/* uid 13 */
insert into users (name, family_name, email) values ('ui_add_teacher', 'test', 'new@teacher.ui.com');
insert into teachers (tid) values (13);

/* uid 14 */
insert into users (name, family_name, email) values ('view_sessions', 'test', 'sessions@teacher.com');
insert into teachers (tid) values (14);

/* 15 */
insert into users (name, family_name, email) values ('view_sessions', 'student', 'sessions@student.com');
insert into students (sid, uni) values (15, 'sessions');


/* insert courses here */
insert into courses (name, active) values ('Running', 0); /* cid=1 */
insert into courses (name, active) values ('Writing', 0); /* cid=2 */
insert into courses (name, active) values ('German 3', 0); /* cid=3 */
insert into courses (name, active) values ('Art History', 0); /* cid=4 */
insert into courses (name, active) values ('Newts big blunder', 0); /* cid=5 , newt will delete during tests*/
insert into courses (name, active) values ('test_add_teacher', 0); /* cid=6 */
insert into courses (name, active) values ('test_view_sessions', 0); /* 7 */

/* insert teaches here */
insert into teaches (tid, cid) values (4, 4); /* douglas teaches art history */
insert into teaches (tid, cid) values (7, 2); /* newt teaches writing */
insert into teaches (tid, cid) values (7, 5); /* newt teaches his blunder */


insert into teaches (tid, cid) values (12, 6);

insert into teaches (tid, cid) values (14, 7);

/* Dave and Grommash enrolled in Art History */
insert into enrolled_in (sid, cid) values (3, 4);
insert into enrolled_in (sid, cid) values (5, 4);

insert into enrolled_in (sid, cid) values (15, 7);

/* add session for art history */
insert into sessions (cid, secret, expires, day) values (4, '7878', '23:59:59', '2016-11-01'); /* seid = 1 */
insert into sessions (cid, secret, expires, day) values (4, '0000', '23:59:59', '2020-01-01'); /* seid = 2 */
/* update art history for the active session we just inserted */
update courses set active = 1 where cid = 4;

/* add attendance records */
/* add Dave into old and new sessions */
insert into attendance_records (sid, seid) values (3, 1);
insert into attendance_records (sid, seid) values (3, 2);
