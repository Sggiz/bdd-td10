#!/usr/bin/python

from model import Model
from flask import *
from forms import *
from psycopg2 import errors

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

################################################################
####              HANDLING OF STUDENTS                      ####
################################################################


@app.route('/student/', methods=['GET', 'POST'])
def showStudents():
    with Model() as model:
        form = StudentForm(request.form)
        if request.method == 'POST' and form.validate():
            model.createStudent(form.lastname.data, form.firstname.data, form.phone.data)

        students = model.listStudents()
        keys = [
            '', 'Last name', 'First name', 'Phone', '#Curriculums',
            'Details', 'Delete'
        ]
        return render_template(
            'listing.html',
            to_list=[(students, keys, "Students")],
            title='Students',
            forms=[form])


@app.route('/student/del/<id>/')
def delStudent(id=None):
    with Model() as model:
        model.deleteStudent(id)
        return redirect(url_for('showStudents'))


@app.route('/student/<id>/', methods=['GET', 'POST'])
def showStudent(id=None):
    with Model() as model:
        curri = model.listCurriculumsOfStudent(id)
        exams = model.listValidationsOfStudent(id)
        keys_curri = ['Curriculum Name', 'Grade']
        keys_exams = [
            '', 'Date', 'Curriculum', 'Course', 'Validation', 'Grade'
        ]
        return render_template(
            'listing.html',
            to_list=[
                (curri, keys_curri, "Summary of " + model.getNameOfStudent(id)),
                (exams, keys_exams,
                 "Detailed grades of student " + model.getNameOfStudent(id))
            ],
            title='Student ' + model.getNameOfStudent(id))



################################################################
####              HANDLING OF ACCOUNTS                      ####
################################################################


@app.route('/account/', methods=['GET', 'POST'])
def showAccounts():
    with Model() as model:
        depForm = DepositForm(request.form)
        transForm = TransferForm(request.form)
        depForm.setNames()
        transForm.setNames()
        if request.method == 'POST':
            if transForm.validate():
                try:
                    model.transfer(transForm.source.data, transForm.target.data, transForm.amount.data)
                except Exception as e:
                    message = e.args
                    transForm.amount.errors = ([message])
            elif depForm.validate():
                try:
                    model.deposit(depForm.account.data, depForm.amount.data)
                    transForm = TransferForm()
                    transForm.setNames()
                except Exception as e:
                    message = e.args
                    transForm.amount.errors = ([message])

        accs = model.listAccounts()
        keys = ['', 'Name', 'Balance', 'Details']
        return render_template(
            'listing.html',
            to_list=[(accs, keys, "Accounts")],
            title='Accounts',
            forms=[transForm, depForm])


@app.route('/account/<id>/', methods=['GET', 'POST'])
def showAccount(id=None):
    with Model() as model:
        trans = model.listTransOfStudent(id)
        keys_trans = ['', 'Time', 'Operation', 'From/to', 'Amount']

        return render_template(
            'listing.html',
            to_list=[
                (trans, keys_trans,
                 "Detailed operations on " + model.getNameOfStudent(id) + "'s account")
            ],
            title='Student ' + model.getNameOfStudent(id))



################################################################
####              HANDLING OF TEACHERS                      ####
################################################################


@app.route('/teacher/', methods=['GET', 'POST'])
def showTeachers():
    with Model() as model:
        form = TeacherForm(request.form)
        if request.method == 'POST' and form.validate():
            model.createTeacher(form.lastname.data, form.firstname.data, form.phone.data)

        teach = model.listTeachers()
        keys = [
            '', 'Last name', 'First name', 'Phone', 'Details', 'Delete'
        ]
        return render_template(
            'listing.html',
            to_list=[(teach, keys, "Teachers")],
            title='Teachers',
            forms=[form])


@app.route('/teacher/del/<id>/')
def delTeacher(id=None):
    with Model() as model:
        model.deleteTeacher(id)
        return redirect(url_for('showTeachers'))


@app.route('/teacher/<id>/', methods=['GET', 'POST'])
def showTeacher(id=None):
    with Model() as model:
        curri = model.listCurriculumsOfTeacher(id)
        cours = model.listCoursesOfTeacher(id)
        exams = model.listValidationsOfTeacherToGrade(id)
        keys_curri = ['Curriculum Name']
        keys_cours = ['Course Name']
        keys_exams = [
            'Date', 'Course', 'Validation'
        ]
        return render_template(
            'listing.html',
            to_list=[
                (curri, keys_curri, "Curricula supervised by " + model.getNameOfTeacher(id)),
                (cours, keys_cours, "Courses given by " + model.getNameOfTeacher(id)),
                (exams, keys_exams, "Validations " + model.getNameOfTeacher(id) + " has to grade")
            ],
            title='Teacher ' + model.getNameOfTeacher(id))



################################################################
####              HANDLING OF CURRICULUMS                   ####
################################################################


@app.route('/curriculum/', methods=['GET', 'POST'])
def showCurriculums():
    with Model() as model:
        form = CurriculumForm(request.form)
        form.setNames()
        if request.method == 'POST' and form.validate():
            model.createCurriculum(form.name.data, form.director.data)
        students = model.listCurriculums()
        keys = [
            '', 'Name', 'Director', 'Details', 'Delete'
        ]
        return render_template(
            'listing.html',
            to_list=[(students, keys, "Curriculums")],
            title='Curriculums',
            forms=[form])


@app.route('/curriculum/del/<id>/')
def delCurriculum(id=None):
    with Model() as model:
        model.deleteCurriculum(id)
        return redirect(url_for('showCurriculums'))


@app.route('/curriculum/<id>/', methods=['GET', 'POST'])
def showCurriculum(id=None):
    with Model() as model:
        addStudentForm = SelectStudentForm(request.form)
        addStudentForm.setNames()
        addCourseForm = SelectCourseForm(request.form)
        addCourseForm.setNames()
        if request.method == 'POST':
            if addStudentForm.validate():
                try:
                    model.registerStudentToCurriculum(addStudentForm.student.data, id)
                except errors.UniqueViolation:
                    addStudentForm.student.errors = ([
                        "This student is already registered to this curriculum."
                    ])
            elif addCourseForm.validate():
                try:
                    model.registerCourseToCurriculum(addCourseForm.course.data,
                                                    id,
                                                    addCourseForm.ects.data)
                    addStudentForm = SelectStudentForm()
                    addStudentForm.setNames()
                except errors.UniqueViolation:
                    addCourseForm.course.errors = ([
                        "This course is already registered to this curriculum."
                    ])
        avg = model.averageGradesOfStudentsInCurriculum(id)
        cou = model.listCoursesOfCurriculum(id)
        keys_avg = ['Student', 'Grade']
        keys_cou = [
            '', 'Name', 'Teacher', 'ECTS', 'Delete'
        ]
        return render_template(
            'listing.html',
            to_list=[
                (avg, keys_avg, "Averaged grades of curriculum " +
                 model.getNameOfCurriculum(id)),
                (cou, keys_cou,
                 "Courses of curriculum " + model.getNameOfCurriculum(id)),
            ],
            title='Curriculum ' + model.getNameOfCurriculum(id),
            forms=[addStudentForm, addCourseForm])


@app.route('/curriculum/<idCurr>/del/<idCou>/')
def delCourseFromCurriculum(idCurr=None, idCou=None):
    with Model() as model:
        model.deleteCourseFromCurriculum(idCou, idCurr)
        return redirect(url_for('showCurriculum', id=idCurr))


################################################################
####              HANDLING OF COURSES                       ####
################################################################


@app.route('/course/', methods=['GET', 'POST'])
def showCourses():
    with Model() as model:
        addCourseForm = CourseForm(request.form)
        addCourseForm.setNames()
        if request.method == 'POST' and addCourseForm.validate():
            model.createCourse(addCourseForm.name.data,
                               addCourseForm.teacher.data)
        students = model.listCourses()
        keys = [
            '', 'Name', '', 'Teacher', 'Details',
            'Delete'
        ]
        return render_template(
            'listing.html',
            to_list=[(students, keys, "Courses")],
            title='Courses',
            forms=[addCourseForm])


@app.route('/course/del/<id>/')
def delCourse(id=None):
    with Model() as model:
        model.deleteCourse(id)
        return redirect(url_for('showCourses'))


@app.route('/course/<id>/', methods=['GET', 'POST'])
def showCourse(id=None):
    with Model() as model:
        form = ValidationForm(request.form)
        if request.method == 'POST' and form.validate():
            model.addValidationToCourse(form.name.data, form.coef.data, form.date.data, id)
        exams = model.listValidationsOfCourse(id)
        grades = model.listGradesOfCourse(id)
        curri = model.listCurriculumsOfCourse(id)
        students = model.listStudentsOfCourse(id)
        keys_grades = [
            '', 'Date', 'Curriculum', 'Student',
            'Validation', 'Grade', 'Coef'
        ]
        keys_exams = ['', 'Date', 'Name', 'Coef', 'Details']
        keys_curri = ['', 'Curriculum', 'ECTS']
        keys_students = ['', 'Name', 'Total grade']
        return render_template(
            'listing.html',
            to_list=[(curri, keys_curri,
                      "Curriculums of course " + model.getNameOfCourse(id)),
                     (exams, keys_exams,
                      "List of exams for course " + model.getNameOfCourse(id)),
                     (grades, keys_grades,
                      "Grades of course " + model.getNameOfCourse(id)),
                     (students, keys_students,
                      "Students of course " + model.getNameOfCourse(id))],
            forms=[form])


@app.route('/course/<idCourse>/<idValidation>/', methods=['GET', 'POST'])
def showValidation(idCourse=None, idValidation=None):
    with Model() as model:
        form = GradesForm(request.form)
        form.setNames(idCourse)
        if request.method == 'POST' and form.validate():
            try:
                model.addGrade(idValidation, form.student.data,
                               str(form.grade.data))
            except errors.UniqueViolation:
                form.student.errors = ([
                    "This student already has a grade."
                ])

        grades = model.listGradesOfValidation(idValidation)
        keys_grades = ['Student', 'Grade']
        return render_template(
            'listing.html',
            to_list=[(grades, keys_grades,
                      "Grades of " + model.getNameOfValidation(idValidation))],
            forms=[form])


if __name__ == '__main__':
    app.run(debug=True)
