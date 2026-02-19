import os
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
import seaborn as sns
import pandas as pd



#get the name of directory in which we are working and change that directory to the desired one
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir,"..","TEXT FILES")

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
#-------------------HeatMap-------------------------
def heatmap(input_file):

    df = pd.read_csv(input_file, header=None)

    marks_df = df.iloc[:, 2:]
    marks_df.columns = subject_names[:len(marks_df.columns)]

    plt.figure(figsize=(10,10))
    sns.heatmap(marks_df, cmap="coolwarm")

    plt.title("Class Performance Heatmap")
    plt.xlabel("Subjects")
    plt.ylabel("Students")

    heatmap_path = os.path.join(data_dir, "heatmap.png")
    plt.savefig(heatmap_path)
    plt.close()
    return heatmap_path
#-----------------TOPPER VS AVERAGE-------------
def topper_vs_average_graph(input_file):

    df = pd.read_csv(input_file, header=None)

    marks_df = df.iloc[:, 2:]
    marks_df.columns = subject_names

    subject_avg = marks_df.mean()
    subject_topper = marks_df.max()

    plt.figure(figsize=(12,10))

    plt.plot(subject_names, subject_avg, marker='o', label="Class Average")
    plt.plot(subject_names, subject_topper, marker='o', label="Topper Marks")

    plt.title("Topper vs Class Average Comparison")
    plt.xlabel("Subjects")
    plt.ylabel("Marks")
    plt.legend()

    plt.savefig(comparison_path)
    plt.close()
    gap = subject_topper - subject_avg
    return subject_avg, subject_topper, gap

#------------REPORT - TOPPER VS AVERAGE--------------
def topper_vs_average_report(input_file):

    subject_avg, subject_topper, gap = topper_vs_average_graph(input_file)

    graph_path = os.path.join(data_dir, "topper_vs_average.png")
    pdf_path = os.path.join(data_dir, "topper_vs_average_report.pdf")

    doc = SimpleDocTemplate(pdf_path)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("TOPPER VS CLASS AVERAGE ANALYSIS REPORT", styles['Title']))
    elements.append(Spacer(1, 0.3 * inch))

    # Attach graph
    elements.append(Image(graph_path, width=400, height=250))
    elements.append(Spacer(1, 0.4 * inch))

    elements.append(Paragraph("SUBJECT-WISE COMPETITION GAP:", styles['Heading2']))
    elements.append(Spacer(1, 0.2 * inch))

    # Add subject analysis
    max_gap_subject = gap.idxmax()
    min_gap_subject = gap.idxmin()

    for subject in subject_names:
        elements.append(Paragraph(
            f"{subject}: Average = {round(subject_avg[subject],2)}, "
            f"Topper = {subject_topper[subject]}, "
            f"Gap = {round(gap[subject],2)}",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.15 * inch))

    elements.append(Spacer(1, 0.3 * inch))

    # Key Insights
    elements.append(Paragraph("KEY INSIGHTS:", styles['Heading2']))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        f"• Highest Competition Gap observed in {max_gap_subject}.",
        styles['Normal']
    ))

    elements.append(Paragraph(
        f"• Most Balanced Subject is {min_gap_subject} (smallest gap).",
        styles['Normal']
    ))

    elements.append(Paragraph(
        "• Larger gap indicates strong competition difference between top performers and average students.",
        styles['Normal']
    ))

    doc.build(elements)
#-----------------HeatMap report--------------
def heatmap_report(input_file):


    df = pd.read_csv(input_file, header=None)
    marks_df = df.iloc[:, 2:]
    marks_df.columns = subject_names

    plt.figure(figsize=(8,5))
    sns.heatmap(marks_df, cmap="coolwarm")
    plt.title("Class Performance Heatmap")
    plt.xlabel("Subjects")
    plt.ylabel("Students")

    heatmap_path = os.path.join(data_dir, "heatmap.png")
    plt.savefig(heatmap_path)
    plt.close()

    pdf_path = os.path.join(data_dir, "heatmap_report.pdf")
    doc = SimpleDocTemplate(pdf_path)
    elements = []

    styles = getSampleStyleSheet()

    elements.append(Paragraph("CLASS PERFORMANCE ANALYSIS REPORT", styles['Title']))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Image(heatmap_path, width=400, height=250))
    elements.append(Spacer(1, 0.4 * inch))

    elements.append(Paragraph("SUBJECT-WISE ANALYSIS:", styles['Heading2']))
    elements.append(Spacer(1, 0.2 * inch))

    for subject in marks_df.columns:

        avg = float(marks_df[subject].mean())
        avg = round(avg, 2)

        highest = marks_df[subject].max()
        lowest = marks_df[subject].min()

        if avg >= 75:
            level = "Easy"
            observation = "Most students performed well in this subject."
        elif avg >= 50:
            level = "Moderate"
            observation = "Average performance observed."
        else:
            level = "Difficult"
            observation = "Students are struggling in this subject."

        elements.append(Paragraph(
            f"{subject} → Avg: {avg}, Highest: {highest}, Lowest: {lowest}",
            styles['Normal']
        ))

        elements.append(Paragraph(
            f"Difficulty Level: {level}",
            styles['Normal']
        ))

        elements.append(Paragraph(
            f"Observation: {observation}",
            styles['Normal']
        ))

        elements.append(Spacer(1, 0.3 * inch))

    doc.build(elements)
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
            doc = SimpleDocTemplate(pdf_path,pagesize = A4)
            elements = []

            styles = getSampleStyleSheet()
             # ---------------- HEADER ----------------
            elements.append(Paragraph("<b>ABC INSTITUTE OF TECHNOLOGY</b>", styles['Title']))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph("<b>ACADEMIC REPORT CARD</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.3 * inch))
            info_data = [
              ["Student ID", sid],
              ["Name", name],
              ["Rank", rank_dic[sid]],
              ["Total Marks", total],
              ["Percentage", f"{percentage:.2f}%"],
              ["Grade", grade],
              ["Final Result", status],
            ]

            info_table = Table(info_data, colWidths=[150, 300])
            info_table.setStyle(TableStyle([
             ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
             ('GRID', (0,0), (-1,-1), 1, colors.grey),
             ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
             ('FONTSIZE', (0,0), (-1,-1), 10),
             ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
            ]))

            elements.append(info_table)
            elements.append(Spacer(1, 0.4 * inch))

        # ---------------- SUBJECT TABLE ----------------
            subject_data = [["Subject", "Marks"]]

            for subject, marks in student_marks:
             subject_data.append([subject, marks])

            subject_table = Table(subject_data, colWidths=[250, 200])
            subject_table.setStyle(TableStyle([
             ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
             ('GRID', (0,0), (-1,-1), 1, colors.black),
             ('ALIGN', (1,1), (-1,-1), 'CENTER'),
             ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
             ('FONTSIZE', (0,0), (-1,-1), 10),
            ]))

            elements.append(Paragraph("<b>Subject-wise Performance</b>", styles['Heading3']))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(subject_table)
            elements.append(Spacer(1, 0.4 * inch))

        # ---------------- PERFORMANCE SUMMARY ----------------
            elements.append(Paragraph("<b>Performance Summary</b>", styles['Heading3']))
            elements.append(Spacer(1, 0.2 * inch))

            elements.append(Paragraph(f"Strongest Subject: {strongest[0]}", styles['Normal']))
            elements.append(Paragraph(f"Weakest Subject: {weakest[0]}", styles['Normal']))
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph(f"Teacher's Remark: {remark}", styles['Normal']))

            elements.append(Spacer(1, 0.5 * inch))
            elements.append(Paragraph("----- End of Report -----", styles['Normal']))

            doc.build(elements)
# ------------------ MAIN ANALYSER ------------------
def analyser(input_file):

    students, subject_lists = load_students(input_file)
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
