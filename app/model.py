#!/usr/bin/python

import sys
import psycopg2
import psycopg2.extras
import time

class Model:
    def __init__(self):
        self.connection = psycopg2.connect("dbname=max user=max")
        self.connection.autocommit = True
        self.cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if (self.connection):
            self.connection.close()

##############################################
######     Queries for tab STUDENTS     ######
##############################################

    # TODO 01 - Easy
    # Create a new student and associated account.
    def createStudent(self, lastname, firstname, phone):
        self.cursor.execute(f"""
        INSERT INTO Student (first_name, last_name, tel, balance) VALUES
            ('{firstname}', '{lastname}', '{phone}', 0.00);
        """)

    # TODO 02 - Easy
    # Return a list of (id, lastname, firstname, phone,
    # number of curriculums) corresponding to all students,
    # ordered by their last names.
    def listStudents(self):
        self.cursor.execute(f"""
        SELECT s_id, last_name, first_name, tel, Count(p_id) as nb
        FROM Student
        NATURAL LEFT JOIN Attends
        GROUP BY s_id
        ORDER BY last_name;
        """)
        return self.cursor.fetchall()

    # TODO 03 - Easy
    # Delete a student given its ID (beware of the foreign constraints!).
    def deleteStudent(self, idStudent):
        self.cursor.execute(f"""
        DELETE FROM Student
        WHERE s_id = {idStudent};
        """)

##############################################
######     Queries for tab ACCOUNTS     ######
##############################################

    # TODO 04 - Easy
    # Return a list of (id, full name, account balance)
    # corresponding to all student accounts.
    def listAccounts(self):
        self.cursor.execute(f"""
        SELECT s_id, first_name || ' ' || last_name, balance
        FROM Student
        ORDER BY last_name;
        """)
        return self.cursor.fetchall()

    # TODO 05 - Medium
    # Update the database to take into account a deposit.
    def deposit(self, account, amount):
        self.cursor.execute(f"""
        UPDATE Student
        SET balance = balance + {amount}
        WHERE s_id = {account};
        INSERT INTO Deposit (recipient, amount) VALUES
            ({account}, {amount});
        """)

    # TODO 06 - Medium
    # Return the amount of money transfered by a given student
    # over the last 24 hours, plus some given additional amount.
    # Do not forget to handle the case where there is no transfers
    # in the last 24 hours.
    def getTransferedAmountOver24Hours(self, id, additional):
        self.cursor.execute(f"""
        SELECT COALESCE(SUM(amount) + {additional}, 0)
        FROM Transfer
        WHERE issuer = {id}
            AND time + interval '1 day' >= NOW();
        """)
        res = self.cursor.fetchone()
        assert (res is not None), "Issue with amount retrieval"
        s = res[0]
        return s

    # TODO 07 - Medium
    # Updates the database to take into account a transfer from
    # a given issuer account to a given recipient account, ensuring that:
    # - The issuer account has enough money;
    # - After exercise 5: the total amount transfered from
    #   the issuer account over 24 hours is not greater than 1000€.
    def transfer(self, issuer, recipient, amount):
        if issuer == recipient:
            raise Exception("Transfer must be between different accounts")

        self.cursor.execute(f"""
        BEGIN TRANSACTION;
        LOCK TABLE Transfer;
        SELECT balance FROM Student WHERE s_id = {issuer};
        """)
        res = self.cursor.fetchone()
        assert (res is not None), "Issue with student balance retrieval"
        balance = res[0]

        transfer_amount_24 = self.getTransferedAmountOver24Hours(issuer, amount)

        if (balance < amount):
            raise Exception("Impossible transfer : requires more balance")
        elif (transfer_amount_24 > 1000):
            raise Exception("Total transfered amount cannot excede 1000€ over 24 hours")
        else:
            self.cursor.execute(f"""
            UPDATE Student
            SET balance = balance - {amount}
            WHERE s_id = {issuer};
            UPDATE Student
            SET balance = balance + {amount}
            WHERE s_id = {recipient};
            INSERT INTO Transfer(issuer, recipient, amount) VALUES
                ({issuer}, {recipient}, {amount});
            COMMIT;
            """)


##############################################
######   Queries for tab ACCOUNTS/<ID>  ######
##############################################

    # TODO 08 - Medium
    # Return a list of (id, date, operation type, from/to, amount)
    # of all operations on the account of a given student, sorted by
    # decreasing date.
    # Operation type is either "Deposit", "Received transfer" or
    # "Sent transfer", and from/to is the full name of the other
    # person involved if the operation is a transfer, and a NULL
    # otherwise.
    def listTransOfStudent(self, id):
        self.cursor.execute(f"""
        SELECT dep_id, time, 'Deposit', NULL, amount
        FROM Deposit
        WHERE recipient = {id}

        UNION

        SELECT tr_id, time, 'Recieved transfer',
            first_name || ' ' || last_name, amount
        FROM Transfer
        JOIN Student
            ON issuer = s_id

        UNION

        SELECT tr_id, time, 'Sent transfer',
            first_name || ' ' || last_name, amount
        FROM Transfer
        JOIN Student
            ON recipient = s_id

        ORDER BY time DESC;
        """)
        return self.cursor.fetchall()


##############################################
######     Queries for tab TEACHERS     ######
##############################################

    # TODO 09 - Easy
    # Create a new teacher.
    def createTeacher(self, lastname, firstname, phone):
        self.cursor.execute(f"""
        INSERT INTO Teacher (first_name, last_name, tel) VALUES
            ('{firstname}', '{lastname}', '{phone}');
        """)

    # TODO 10 - Easy
    # Return a list of (id, lastname, firstname, phone,
    # number of curriculums) corresponding to all teachers.
    def listTeachers(self):
        self.cursor.execute(f"""
        SELECT t_id, last_name, first_name, tel, COUNT(p_id)
        FROM Teacher
        NATURAL LEFT JOIN Program
        GROUP BY t_id;
        """)
        return self.cursor.fetchall()

    # TODO 11 - Easy
    # Delete a teacher given its ID (beware of the foreign constraints!).
    def deleteTeacher(self, idTeacher):
        self.cursor.execute(f"""
        DELETE FROM Teacher
        WHERE t_id = {idTeacher};
        """)

##############################################
######     Queries for CURRICULUMS      ######
##############################################

    # TODO 12 - Easy
    # Create a curriculum.
    def createCurriculum(self, name, director):
        self.cursor.execute(f"""
        INSERT INTO Program(t_id, name) VALUES
            ({director}, '{name}');
        """)

    # TODO 13 - Easy
    # Return a list of (id,name of curriculum,director lastname,
    # director firstname) corresponding to all curriculums.
    def listCurriculums(self):
        self.cursor.execute(f"""
        SELECT p_id, name, last_name, first_name
        FROM Program
        NATURAL JOIN Teacher;
        """)
        return self.cursor.fetchall()

    # TODO 14 - Easy
    # Delete a curriculum given its ID (beware of the foreign constraints!).
    def deleteCurriculum(self, idCurriculum):
        self.cursor.execute(f"""
        DELETE FROM Program
        WHERE p_id = {idCurriculum};
        """)

##############################################
######     Queries for  COURSES         ######
##############################################

    # TODO 15 - Easy
    # Create a course.
    def createCourse(self, name, idProfessor):
        self.cursor.execute(f"""
        INSERT INTO Course(t_id, name) VALUES
            ({idProfessor}, '{name}');
        """)

    # TODO 16 - Easy
    # Return a list of (course id, course name, teacher id,
    # teacher last name, teacher first name) corresponding
    # to all the courses.
    def listCourses(self):
        self.cursor.execute(f"""
        SELECT c_id, name, t_id, last_name, first_name
        FROM Course
        NATURAL JOIN Teacher;
        """)
        return self.cursor.fetchall()

    # TODO 17 - Easy
    # Delete a given course (beware that the course might be registered to
    # curriculum, and have grades that should also be deleted).
    def deleteCourse(self, idCourse):
        self.cursor.execute(f"""
        DELET FROM Course
        WHERE c_id = {idCourse};
        """)


##############################################
###### Queries for tab  CURRICULUM/<ID> ######
##############################################

    # TODO 18 - Easy
    # Get the name of a given curriculum.
    def getNameOfCurriculum(self, id):
        self.cursor.execute(f"""
        SELECT name
        FROM Program
        WHERE p_id = {id};
        """)
        # suppose that there is a solution
        return self.cursor.fetchall()[0][0]

    # TODO 19 - Easy
    # Return the list (course id, course name, teacher full name, ECTS)
    # corresponding to the courses, registered to a given curriculum.
    def listCoursesOfCurriculum(self, idCurriculum):
        self.cursor.execute(f"""
        SELECT c_id, name, first_name || ' ' || last_name, ects
        FROM Course
        NATURAL JOIN Teacher
        NATURAL JOIN Contains
        WHERE p_id = {idCurriculum};
        """)
        return self.cursor.fetchall()

    # TODO 20 - Hard
    # Return a list (full name, average grade) of students
    # registered to a given curriculum. The
    # average grade is computed as described in the document, but
    # beware that if a student does not have a grade for a validation
    # or is not registered to a course, he should have 0.
    def averageGradesOfStudentsInCurriculum(self, idCurriculum):
        self.cursor.execute(f"""
        WITH 
        SELECT first_name || ' ' || last_name, 0
        FROM Student;
        """)
        return self.cursor.fetchall()

    # TODO 21 - Easy
    # Register a student to a curriculum.
    def registerStudentToCurriculum(self, idStudent, idCurriculum):
        self.cursor.execute(f"""
        INSERT INTO Attends(s_id, p_id) VALUES
            ({idStudent}, {idCurriculum});
        """)

    # TODO 22 - Easy
    # Register a course to a curriculum.
    def registerCourseToCurriculum(self, idCourse, idCurriculum, ects):
        self.cursor.execute(f"""
        INSERT INTO Contains(p_id, c_id, ects) VALUES
            ({idCurriculum}, {idCourse}, {ects});
        """)

    # TODO 23 - Easy
    # Unregister a course to a curriculum.
    def deleteCourseFromCurriculum(self, idCourse, idCurriculum):
        self.cursor.execute(f"""
        DELETE FROM Contains
        WHERE p_id = {idCurriculum} AND c_id = {idCourse};
        """)

##############################################
######   Queries for tab  COURSE/<ID>   ######
##############################################

    # TODO 24 - Easy
    # Get the name of a given course.
    def getNameOfCourse(self, id):
        self.cursor.execute(f"""
        SELECT name
        FROM Course
        WHERE c_id = {id};
        """)
        # suppose that there is a solution
        return self.cursor.fetchall()[0][0]

    # TODO 25 - Easy
    # Return a list of (id, name, ECTS) of the curriculums in
    # which a given course is registered.
    def listCurriculumsOfCourse(self, idCourse):
        self.cursor.execute(f"""
        SELECT p_id, name, ects
        FROM Program
        NATURAL JOIN Contains
        WHERE c_id = {idCourse};
        """)
        return self.cursor.fetchall()

    # TODO 26 - Easy
    # Returns a list of (id, date, name, coefficent) for the validations
    # assiociated to a given course.
    def listValidationsOfCourse(self, idCourse):
        self.cursor.execute(f"""
        SELECT v_id, date, name, coeff
        FROM Validation
        WHERE c_id = {idCourse};
        """)
        return self.cursor.fetchall()

    # TODO 27 - Hard
    # Return a list (id, full name, average grade) of students that are
    # registered in a curriculum with the given course. The
    # average grade is computed as described in the document, but
    # beware that if a student does not have a grade for a validation
    # or is not registered to a course, he should have 0.
    def listStudentsOfCourse(self, idCourse):
        self.cursor.execute(f"""
        SELECT SUM(coeff)
        FROM Validation
        WHERE c_id = {idCourse};
        """)
        total_coeff = self.cursor.fetchall()[0][0]
        self.cursor.execute(f"""
        WITH attending AS (
            SELECT DISTINCT(a.s_id)
            FROM Attends AS a
            JOIN Contains AS cont
                ON cont.c_id = { idCourse } AND cont.p_id = a.p_id
        )
        SELECT s.s_id,
            s.first_name || ' ' || s.last_name,
            SUM( v.coeff * g.grade ) / { total_coeff }
        FROM attending AS att
        JOIN Student AS s
            ON s.s_id = att.s_id
        JOIN Validation AS v
            ON v.c_id = { idCourse }
        JOIN Grade AS g
            ON g.v_id = v.v_id AND g.s_id = att.s_id
        GROUP BY s.s_id;
        """)
        return self.cursor.fetchall()

    # TODO 28 - Medium
    # Return a list (id, date, curriculum name, student full name,
    # validation name, grade, coefficient) of grades for all the
    # validations and students having taken them, sorted by decreasing
    # date of validation.
    def listGradesOfCourse(self, idCourse):
        self.cursor.execute(f"""
        WITH attending AS (
            SELECT DISTINCT(a.s_id), a.p_id
            FROM Attends AS a
            JOIN Contains AS cont
                ON cont.c_id = { idCourse } AND cont.p_id = a.p_id
        )
        SELECT
            v.v_id,
            v.date,
            p.name,
            s.first_name || ' ' || s.last_name,
            v.name,
            g.grade,
            v.coeff
        FROM Grade AS g
        JOIN attending AS att
            ON g.s_id = att.s_id
        JOIN Student AS s
            ON s.s_id = g.s_id
        JOIN Validation AS v
            ON v.v_id = g.v_id
        JOIN Program AS p
            ON p.p_id = att.p_id
        WHERE v.c_id = {idCourse}
        ORDER BY date DESC;
        """)
        return self.cursor.fetchall()

    # TODO 29 - Easy
    # Add a validation to a given course.
    def addValidationToCourse(self, name, coef, date, idCourse):
        self.cursor.execute(f"""
        INSERT INTO Validation(c_id, name, coeff, date) VALUES
            ({idCourse}, '{name}', {coef}, '{date}');
        """)

    # TODO 30 - Easy
    # Add a grade to a student.
    def addGrade(self, idValidation, idStudent, grade):
        self.cursor.execute(f"""
        INSERT INTO Grade(v_id, s_id, grade) VALUES
            ({idValidation}, {idStudent}, {grade});
        """)

##############################################
######       Queries for tab            ######
######      COURSE/<ID1>/<ID2           ######
###### corresponding to validations     ######
##############################################

    # TODO 31 - Easy
    # Return a list (full name, grade) of grades for
    # a given validation.
    def listGradesOfValidation(self, idValidation):
        self.cursor.execute(f"""
        SELECT first_name || ' ' || last_name, grade
        FROM Student
        NATURAL JOIN GRADE
        WHERE v_id = {idValidation};
        """)
        return self.cursor.fetchall()

    # TODO 32 - Easy
    # Get the complete name of a validation given its ID. The
    # complete name of a validation with name "exam" of a course "BDD"
    # is "BDD - exam". You should therefore preppend the name of the
    # course.
    def getNameOfValidation(self, id):
        self.cursor.execute(f"""
        SELECT c.name || ' - ' || v.name
        FROM (
        SELECT * FROM Validation WHERE v_id = {id}
            ) AS v
        JOIN Course AS c
            ON c.c_id = v.c_id;
        """)
        # suppose that there is a solution
        return self.cursor.fetchall()[0][0]

##############################################
######   Queries for tab  TEACHER/<ID>  ######
##############################################

    # TODO 33 - Easy
    # Get the name of a teacher given its ID.
    def getNameOfTeacher(self, id):
        self.cursor.execute(f"""
        SELECT first_name || ' ' || last_name FROM Teacher WHERE t_id = {id};
        """)
        # suppose that there is a solution
        return self.cursor.fetchall()[0][0]

    # TODO 34 - Easy
    # Return a list (name) of all the curriculums supervised
    # by a given teacher
    def listCurriculumsOfTeacher(self, idTeacher):
        self.cursor.execute(f"""
        SELECT name
        FROM Program
        WHERE t_id = {idTeacher};
        """)
        return self.cursor.fetchall()

    # TODO 35 - Easy
    # Return a list (name) of all the courses supervised
    # by a given teacher
    def listCoursesOfTeacher(self, idTeacher):
        self.cursor.execute(f"""
        SELECT name
        FROM Course
        WHERE t_id = {idTeacher};
        """)
        return self.cursor.fetchall()

    # TODO 36 - Medium
    # Return a list (date, course name, exam name) of exams
    # for all courses taught by a given teacher, such that the
    # due date is passed and there is no grade for at least one
    # registered studentgrades for a given student, sorted
    # by increasing date of validation.
    def listValidationsOfTeacherToGrade(self, idTeacher):
        self.cursor.execute(f"""
        SELECT v.date, c.name, v.name
        FROM Validation AS v
        JOIN Course AS c
            ON c.c_id = v.c_id
        JOIN Contains AS cont
            ON cont.c_id = v.c_id
        JOIN Attends AS a
            ON a.p_id = cont.p_id
        LEFT JOIN Grade AS g
            ON g.v_id = v.v_id AND g.s_id = a.s_id
        WHERE g.grade IS NULL
        GROUP BY (v.v_id, c.name, c.t_id)
        HAVING c.t_id = {idTeacher}
            AND v.date < NOW()
        ORDER BY v.date;
        """)
        return self.cursor.fetchall()


##############################################
######   Queries for tab  STUDENT/<ID>  ######
##############################################

    # TODO 37 - Easy
    # Get the name of a student given its ID.
    def getNameOfStudent(self, id):
        self.cursor.execute(f"""
        SELECT first_name || ' ' || last_name
        FROM Student
        WHERE s_id = {id};
        """)
        # suppose that there is a solution
        return self.cursor.fetchall()[0][0]

    # TODO 38 - Medium
    # Return a list (id, date, curriculum name, course name,
    # exam name, grade)
    # by decreasing date of validation.
    def listValidationsOfStudent(self, idStudent):
        self.cursor.execute(f"""
        SELECT v.v_id, v.date, p.name, c.name, v.name, g.grade
        FROM Grade AS g
        JOIN Validation AS v
            ON v.v_id = g.v_id
        JOIN Course AS c
            ON c.c_id = v.c_id
        JOIN Attends AS a
            ON a.s_id = v.s_id
        JOIN Contains AS cont
            ON cont.c_id = c.c_id AND cont.p_id = a.p_id
        WHERE v.s_id = {idStudent};
        """)
        return self.cursor.fetchall()

    # TODO 39 - Hard
    # Return a list (curriculum name, average grade) of all the
    # curriculum a given student is registered to, where the
    # average grade is computed as before.
    def listCurriculumsOfStudent(self, idStudent):
        self.cursor.execute(f"""
        TODO 39
        """)
        return self.cursor.fetchall()
