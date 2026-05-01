#!/usr/bin/python

from wtforms import Form, BooleanField, StringField, IntegerField, SelectField
from wtforms import DecimalField, DateField, DateTimeField, validators
from model import Model


class StudentForm(Form):
    formname = "Register a new student"
    lastname = StringField('Lastname', [validators.Length(min=2, max=25)])
    firstname = StringField('Firstname', [validators.Length(min=2, max=25)])
    phone = StringField('Phone', [validators.Length(min=6, max=14)])


class TransferForm(Form):
    formname = "Make a transfer"
    source = SelectField('From', coerce=int, choices=[])
    target = SelectField('To', coerce=int, choices=[])
    amount = DecimalField('Amount', [validators.NumberRange(min=0)])

    def setNames(self):
        with Model() as model:
            l = [(p[0], p[1]) for p in model.listAccounts()]
            self.source.choices = l
            self.target.choices = l


class DepositForm(Form):
    formname = "Deposit onto an account"
    account = SelectField('Account', coerce=int, choices=[])
    amount = DecimalField('Amount', [validators.NumberRange(min=0)])

    def setNames(self):
        with Model() as model:
            l = [(p[0], p[1]) for p in model.listAccounts()]
            self.account.choices = l


class TeacherForm(Form):
    formname = "Register a new teacher"
    lastname = StringField('Lastname', [validators.Length(min=2, max=25)])
    firstname = StringField('Firstname', [validators.Length(min=2, max=25)])
    phone = StringField('Phone', [validators.Length(min=6, max=14)])


class CurriculumForm(Form):
    formname = "Create a new curriculum"
    name = StringField('Name', [validators.Length(min=2, max=25)])
    director = SelectField('Director', coerce=int, choices=[])

    def setNames(self):
        with Model() as model:
            l = [(p[0], p[2] + " " + p[1]) for p in model.listTeachers()]
            self.director.choices = l


class CourseForm(Form):
    formname = "Create a new course"
    name = StringField('Name', [validators.Length(min=2, max=25)])
    teacher = SelectField('Teacher', coerce=int, choices=[])
    
    def setNames(self):
        with Model() as model:
            l = [(p[0], p[2] + " " + p[1]) for p in model.listTeachers()]
            self.teacher.choices = l


class SelectStudentForm(Form):
    formname = "Register a student into a curriculum"
    student = SelectField('Student', coerce=int, choices=[])

    def setNames(self):
        with Model() as model:
            l = [(p[0], p[2] + " " + p[1]) for p in model.listStudents()]
            self.student.choices = l


class SelectCourseForm(Form):
    formname = "Register a course into a curriculum"
    course = SelectField('Course', coerce=int, choices=[])
    ects = IntegerField('ECTS')

    def setNames(self):
        with Model() as model:
            l = [(p[0], p[1] + " by " + p[3])
                 for p in model.listCourses()]
            self.course.choices = l


class ValidationForm(Form):
    formname = "Create a new validation for a course"
    name = StringField('Name of the examination',
                        [validators.Length(min=2, max=25)])
    coef = IntegerField('Coefficient of the examination in the course',
                        [validators.NumberRange(min=1)])
    date = DateField('Date of the examination')


class GradesForm(Form):
    formname = "Add a new grade"
    student = SelectField('Student', coerce=int, choices=[])
    grade = DecimalField('Grade (over 20)')

    def setNames(self, idCourse):
        with Model() as model:
            l = [(p[0], p[1])
                 for p in model.listStudentsOfCourse(idCourse)]
            self.student.choices = l
