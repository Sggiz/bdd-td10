
from random import seed, randrange, choice, sample, random

seed(42)

nb_student = 61
nb_teacher = 8
nb_program = 16
nb_course = 23

val_names = ["Exam", "Homework", "Presentation"]

dates = ["01-01-1980", "01-01-2077"]

contains = [[] for _ in range(nb_course)]
attends = [[] for _ in range(nb_program)]
validation = [[] for _ in range(nb_course)]


# Contains
cont_file = open("./contains.txt", "w")

for c_id in range(nb_course):
    nb = randrange(1, 4)
    ects_l = [randrange(3, 15, 3) for _ in range(nb)]
    program_l = sample(range(nb_program), nb)
    data = [
            ( program_l[i] , ects_l[i] )
            for i in range(nb)
        ]
    contains[c_id] = data
    for p_id, ects in data:
        cont_file.write(f"{c_id+1},{p_id+1},{ects}\n")

cont_file.close()



# Attends
a_file = open("./attends.txt", "w")

for p_id in range(nb_program):
    data = sample(range(nb_student),randrange(10,20))
    attends[p_id] = data
    for s_id in data:
        a_file.write(f"{s_id+1},{p_id+1}\n")

a_file.close()


# Validation, Grade
v_file = open("./validation.txt", "w")
g_file = open("./grade.txt", "w")

v_id = 0
for c_id in range(nb_course):
    programs = [p_id for p_id, _ in contains[c_id]]
    students = []
    for p_id in programs:
        students = students + attends[p_id]
    students = set(students)
    data = [
            ( choice(val_names), randrange(1,5), choice(dates) )
            for _ in range(randrange(1,6))
        ]
    validation[c_id] = data
    for name, coeff, date in data:
        v_file.write(f"{c_id+1},{name},{coeff},{date}\n")


        for s_id in students:
            if random() > 0.9:
                continue
            grade = randrange(20)
            g_file.write(f"{v_id+1},{s_id+1},{grade}\n")

        v_id += 1


v_file.close()
g_file.close()


