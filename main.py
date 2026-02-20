import os
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF


#get the name of directory in which we are working and change that directory to the desired one
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir,"TEXT FILES")

input_file = os.path.join(data_dir,"students_data.txt")
result_path = os.path.join(data_dir, "result.txt")
grade_path = os.path.join(data_dir,"grades.txt")
pass_path = os.path.join(data_dir, "pass_list.txt")
fail_path = os.path.join(data_dir, "fail_list.txt")
rank_path = os.path.join(data_dir, "rank_list.txt")
stats_path = os.path.join(data_dir, "class_statistics.txt")
bar_path = os.path.join(data_dir, "grade_distribution.png")
reports_dir = os.path.join(data_dir, "report_cards")
comparison_path = os.path.join(data_dir, "topper_vs_average.png")

subject_names = []

# ------------------ DATA INPUT ----------------------
def data_input(input_file) :
    global subject_names
    num = int(input("Enter number of subjects : "))
    subject_names = []

    for i in range(num):
      while True:
        name = input(f"Enter name of Subject {i+1}: ").strip()
        if name == "":
            print("Subject name cannot be empty.")
        elif name in subject_names:
            print("Subject names must be unique.")
        else:
            subject_names.append(name)
            break
    print("Enter student data in the given format \n")
    print("ID, Name, ",",".join(subject_names))
    print("Type END to finish \n")
    
    existing_ids = set()

    # file_path from joining the path to student_data.txt
    with open(input_file, "w") as f :
        while True :
            line = input()
            if line == "END":
                break

            parts = [p.strip() for p in line.split(",")]
            
            #constraints for adding atleast one subject marks
            if len(parts) < 3 :
               print("INVALID FORMAT")
               continue

            sid = parts[0]

            #constraints for student id
            if not sid.isdigit() :
                print("Roll number must contain only digits")
                continue
            if sid in existing_ids :
                print("Roll number must be unique")
                continue

            sname = parts[1]

            #constraints for name
            if sname.isdigit() :
                print("Name cannot be numeric")
                continue
            if sname == "" :
                print("Name cannot be empty")
                continue

            marks = parts[2:]

            #constraints for marks
            valid = True
            for m in marks :
               if (not m.isdigit())  or (int(m) < 0 or int(m) > 100) :
                  print("Invalid marks. Enter in range of[0,100]")
                  valid = False
                  break
            if not valid :
                continue

            existing_ids.add(sid) # add only if every constraint is met
            f.write(line + "\n")

# ------------------ GRADE FUNCTION ------------------
def get_grade(percentage):
    if percentage >= 85:
        return "AA"
    elif percentage >= 75:
        return "AB"
    elif percentage >= 65:
        return "BB"
    elif percentage >= 55:
        return "BC"
    elif percentage >= 45:
        return "CC"
    elif percentage >= 35:
        return "CD"
    else:
        return "F"
# ------------------ LOAD STUDENTS -------------------
def load_students(input_file) :
    students =[]
    subject_lists = []
    with open(input_file, "r") as f :
        lines = f.readlines()
        if not lines:
            return [], []
        first_parts = lines[0].strip().split(",")
        num_subjects = len(first_parts) - 2
        subject_lists = [[] for _ in range(num_subjects)]
        
        for line in lines:
               parts = line.strip().split(",")
               if len(parts) - 2 != num_subjects:
                  print("Error: All students must have same number of subjects")
                  return [], []
               sid = parts[0]
               name = parts[1]
               marks = list(map(int, parts[2:]))
               total = sum(marks)
               percentage = round((total / len(marks)),3)
               students.append((sid, name,total, percentage))
               for i in range(len(marks)) :
                subject_lists[i].append((sid, name, marks[i]))
    return students, subject_lists
          
# ------------------ RESULTS and GRADES ------------------
def write_results(students) :
    with open(result_path, "w") as r, open(grade_path,"w" ) as g :
        r.write(f"{'ID':<15}{'Name':<25}{'Total':<15}{'Percentage':<15}\n")
        g.write(f"{'ID':<15}{'Name':<25}{'Grade':<15}\n")


        for s in students :
            grade = get_grade(s[3])

            r.write(f"{s[0]:<15}{s[1]:<25}{s[2]:<15}{s[3]:<15.2f}\n")
            g.write(f"{s[0]:<15}{s[1]:<25}{grade:<15}\n")

#------------------CLASS STATISTICS-----------------------
def statistics(students) :
    total_students = len(students)
    if total_students == 0:
      return

    class_average = sum(s[3] for s in students)/total_students
    
    highest = max(students, key = lambda x: x[3])
    lowest = min(students, key = lambda x: x[3])
    grade_count = {}
    for s in students :
        grade = get_grade(s[3])
        grade_count[grade] = grade_count.get(grade,0) + 1
    with open(stats_path,"w") as f :
        f.write("-----------CLASS STATISTICS REPORT-------------\n")
        f.write(f"Total Students     : {total_students}\n")
        f.write(f"Class Average        : {class_average:.2f}\n")

        f.write("Highest Percentage   : ")
        f.write(f"{highest[3]:.2f} (ID: {highest[0]}, Name: {highest[1]})\n")

        f.write("Lowest Percentage    : ")
        f.write(f"{lowest[3]:.2f} (ID: {lowest[0]}, Name: {lowest[1]})\n\n")

        f.write("Grade Distribution:\n")

        for grade in sorted(grade_count.keys()):
            f.write(f"{grade:<3} : {grade_count[grade]}\n")
# ------------------ RANK AND PASS/FAIL LIST---------
def rank_and_passfail(students):
    students_sorted = sorted(students, key=lambda x: x[3], reverse=True)

    with open(rank_path, "w") as r, open(pass_path, "w") as p, open(fail_path, "w") as f:

        r.write(f"{'Rank':<8}{'ID':<15}{'Name':<25}{'Total':<15}{'Percentage':<15}\n")
        p.write(f"{'ID':<15}{'Name':<25}{'Percentage':<15}\n")
        f.write(f"{'ID':<15}{'Name':<25}{'Percentage':<15}\n")


        rank = 1
        for s in students_sorted:
            r.write(f"{rank:<8}{s[0]:<15}{s[1]:<25}{s[2]:<15}{s[3]:<15.2f}\n")

            grade = get_grade(s[3])

            if grade == "F":
                f.write(f"{s[0]:<12}{s[1]:<20}{s[3]:<15.2f}\n")
            else:
                p.write(f"{s[0]:<12}{s[1]:<20}{s[3]:<15.2f}\n")

            rank += 1
# ------------------TOP 10 LIST ------------------
def top_ten(subject_lists):
    for i, subject in enumerate(subject_lists):
        subject_sorted = sorted(subject, key=lambda x: x[2], reverse=True)

        subject_path = os.path.join(data_dir, f"{subject_names[i]}_top10.txt")

        with open(subject_path, "w") as f:
            f.write(f"{'Rank':<8}{'ID':<15}{'Name':<25}{'Marks':<12}\n")

            rank = 1
            for s in subject_sorted[:10]:
                f.write(f"{rank:<8}{s[0]:<15}{s[1]:<25}{s[2]:<12}\n")
                rank += 1
#-------------------BAR CHART----------------------
def bar_chart(students) :
    if not students :
        return
    grade_count = {}
    for s in students:
        grade = get_grade(s[3])
        grade_count[grade] = grade_count.get(grade, 0) + 1

    grade_order = ["AA","AB","BB","BC","CC","CD","F"]

    grades = []
    counts = []

    for g in grade_order:
      if g in grade_count:
        grades.append(g)
        counts.append(grade_count[g])
  

    plt.figure(figsize = (8,5))
    plt.bar(grades,counts)
    plt.title(" Grade Distribution")
    plt.xlabel("Grades")
    plt.ylabel("Number of Students")
    plt.savefig(bar_path)
    plt.close()
def topper_vs_average_graph(input_file):

    marks_matrix = []

    with open(input_file, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            marks = list(map(int, parts[2:]))
            marks_matrix.append(marks)

    # Transpose matrix to get subject-wise marks
    subject_wise = list(zip(*marks_matrix))

    subject_avg = []
    subject_topper = []

    for subject_marks in subject_wise:
        subject_avg.append(sum(subject_marks) / len(subject_marks))
        subject_topper.append(max(subject_marks))

    plt.figure(figsize=(10,6))

    plt.plot(subject_names, subject_avg, marker='o', label="Class Average")
    plt.plot(subject_names, subject_topper, marker='o', label="Topper Marks")

    plt.title("Topper vs Class Average Comparison")
    plt.xlabel("Subjects")
    plt.ylabel("Marks")
    plt.legend()

    plt.savefig(comparison_path)
    plt.close()

    gap = [t - a for t, a in zip(subject_topper, subject_avg)]

    return subject_avg, subject_topper, gap
#------------REPORT - TOPPER VS AVERAGE--------------
def topper_vs_average_report(input_file):

    subject_avg, subject_topper, gap = topper_vs_average_graph(input_file)

    pdf_path = os.path.join(data_dir, "topper_vs_average_report.pdf")

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "TOPPER VS CLASS AVERAGE ANALYSIS REPORT", ln=True, align="C")
    pdf.ln(10)

    # Add graph image
    pdf.image(comparison_path, w=180)
    pdf.ln(10)

    pdf.set_font("Arial", size=12)

    max_gap_index = gap.index(max(gap))
    min_gap_index = gap.index(min(gap))

    for i in range(len(subject_names)):
        pdf.multi_cell(
            0,
            8,
            f"{subject_names[i]}: "
            f"Average = {subject_avg[i]:.2f}, "
            f"Topper = {subject_topper[i]}, "
            f"Gap = {gap[i]:.2f}"
        )
        pdf.ln(2)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Key Insights:", ln=True)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, f"Highest Competition Gap: {subject_names[max_gap_index]}")
    pdf.multi_cell(0, 8, f"Most Balanced Subject: {subject_names[min_gap_index]}")
    pdf.multi_cell(0, 8, "Larger gap indicates stronger performance disparity.")

    pdf.output(pdf_path)
#----------------HEATMAP---------------------
def heatmap(input_file):

    marks_matrix = []

    with open(input_file, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            marks = list(map(int, parts[2:]))
            marks_matrix.append(marks)

    plt.figure(figsize=(8,6))
    sns.heatmap(
        marks_matrix,
        annot=True,
        fmt="d",
        cmap="coolwarm",
        xticklabels=subject_names,
        yticklabels=[i+1 for i in range(len(marks_matrix))]
    )

    heatmap_path = os.path.join(data_dir, "heatmap.png")
    plt.tight_layout()
    plt.savefig(heatmap_path)
    plt.close()
#-----------------HeatMap report--------------
def heatmap_report(input_file):

    marks_matrix = []

    with open(input_file, "r") as f:
        for line in f:
            parts = line.strip().split(",")
            marks = list(map(int, parts[2:]))
            marks_matrix.append(marks)

    subject_wise = list(zip(*marks_matrix))

    plt.figure(figsize=(8,6))
    sns.heatmap(
        marks_matrix,
        annot=True,
        fmt="d",
        cmap="coolwarm",
        xticklabels=subject_names,
        yticklabels=[i+1 for i in range(len(marks_matrix))]
    )

    heatmap_path = os.path.join(data_dir, "heatmap.png")
    plt.savefig(heatmap_path)
    plt.close()

    pdf_path = os.path.join(data_dir, "heatmap_report.pdf")
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "CLASS PERFORMANCE ANALYSIS REPORT", ln=True, align="C")
    pdf.ln(10)

    pdf.image(heatmap_path, w=180)
    pdf.ln(10)

    pdf.set_font("Arial", size=12)

    for i, subject_marks in enumerate(subject_wise):

        avg = sum(subject_marks) / len(subject_marks)
        highest = max(subject_marks)
        lowest = min(subject_marks)

        pdf.multi_cell(0, 8,
            f"{subject_names[i]} - Avg: {avg:.2f}, Highest: {highest}, Lowest: {lowest}"
        )
        pdf.ln(2)

    pdf.output(pdf_path)
#----------------------REPORT CARDS-----------------
def report_cards(students, subject_lists) :

        if not os.path.exists(reports_dir):
          os.mkdir(reports_dir)

        students_sorted = sorted(students, key=lambda x: x[3], reverse=True)
        rank_dic = {}

        rank = 1
        for s in students_sorted :
            rank_dic[s[0]] = rank
            rank = rank + 1
        
        for s in students :
            sid = s[0]
            name = s[1]
            total = s[2]
            percentage = s[3]
            grade = get_grade(percentage)

            if grade!= "F" :
                status = "PASS"
            else :
                status = "FAIL"
            student_marks = []
            for i in range(len(subject_lists)):
                for entry in subject_lists[i]:
                    if entry[0] == sid:
                         student_marks.append((subject_names[i], entry[2]))

            strongest = max(student_marks, key=lambda x: x[1])
            weakest = min(student_marks, key=lambda x: x[1])

            if percentage >= 85:
              remark = f"Excellent overall performance. Strong in {strongest[0]}. Keep maintaining consistency."
            elif percentage >= 70:
             remark = f"Very good performance. Strong in {strongest[0]}, but improvement needed in {weakest[0]}."
            elif percentage >= 50:
              remark = f"Good effort. However, focus more on {weakest[0]} to improve results."
            elif percentage >= 35:
               remark = f"Needs improvement. Performance in {weakest[0]} is weak."
            else:
             remark = f"Serious improvement required. Major focus needed on {weakest[0]}." 

            pdf_path = os.path.join(reports_dir, f"{sid}_{name}.pdf")
            pdf = FPDF()
            pdf.add_page()

            # Header
            pdf.set_fill_color(30, 60, 120)   # dark blue
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", "B", 18)
            pdf.cell(0, 15, "ACADEMIC REPORT CARD", ln=True, align="C", fill=True)

            pdf.ln(10)

            # Reset text color
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Arial", size=12)

            # Student Info Box
            pdf.set_draw_color(0, 0, 0)
            pdf.cell(0, 8, f"Student ID: {sid}", ln=True, border=1)
            pdf.cell(0, 8, f"Name: {name}", ln=True, border=1)
            pdf.cell(0, 8, f"Rank: {rank_dic[sid]}", ln=True, border=1)
            pdf.cell(0, 8, f"Total: {total}", ln=True, border=1)
            pdf.cell(0, 8, f"Percentage: {percentage:.2f}%", ln=True, border=1)
            pdf.cell(0, 8, f"Grade: {grade}", ln=True, border=1)
            pdf.cell(0, 8, f"Result: {status}", ln=True, border=1)

            pdf.ln(10)

            # Subject Table Header
            pdf.set_fill_color(200, 220, 255)
            pdf.set_font("Arial", "B", 12)
            pdf.cell(100, 10, "Subject", border=1, fill=True)
            pdf.cell(80, 10, "Marks", border=1, fill=True)
            pdf.ln()

            pdf.set_font("Arial", size=12)

            for subject, marks in student_marks:
                pdf.cell(100, 10, subject, border=1)
                pdf.cell(80, 10, str(marks), border=1)
                pdf.ln()

            pdf.ln(10)

            # Remark Section
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, "Teacher's Remark:", ln=True)

            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 8, remark)

            pdf.ln(10)

            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 8, "---- End of Report ----", align="C")

            pdf.output(pdf_path)
# ------------------ MAIN ANALYSER ------------------
def analyser(input_file):

    students, subject_lists = load_students(input_file)
    if not students :
        print("No data found")
        return
    write_results(students)
    rank_and_passfail(students)
    top_ten(subject_lists)
    statistics(students)
    bar_chart(students)
    report_cards(students, subject_lists)
    heatmap_report(input_file)
    topper_vs_average_report(input_file)

data_input(input_file)
analyser(input_file)
