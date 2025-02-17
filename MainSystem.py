import os
import re
import sys
import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from SSISFINAL import Ui_MainWindow 


# Directory for CSV Files
CSV_FILES = "E:\\COLLEGE DOCUMENTS\\SSIS\\CSV FILES"
os.makedirs(CSV_FILES, exist_ok=True)

#CSV Files
CSV = os.path.join(CSV_FILES, "students.csv")
COLLEGE_CSV = os.path.join(CSV_FILES, "colleges.csv")
PROGRAM_CSV = os.path.join(CSV_FILES, "programs.csv")


class StudentSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Information System")
        #self.setWindowIcon


        # Initialize program codes set
        self.program_codes = set()
        self.college_codes = set()
        self.programcollege_map = {}

        # Add Buttons
        self.ui.AddSt.clicked.connect(self.add_student)
        self.ui.AddCo.clicked.connect(self.add_college)
        self.ui.AddProg.clicked.connect(self.add_program)
        self.ui.EditSt.clicked.connect(self.edit_student)
        self.ui.EditSt_2.clicked.connect(self.edit_college)
        self.ui.EditSt_3.clicked.connect(self.edit_program)
        self.ui.SEARCHbutton.clicked.connect(self.search_student)
        self.ui.Searchbutton.clicked.connect(self.search_college)
        self.ui.Searchbutton_2.clicked.connect(self.search_program)
        
        # Load 
        self.load_students()
        self.load_colleges()
        self.load_programs()
        self.populate_combo_boxes()

        # Deleting
        self.ui.DeleteSt.clicked.connect(self.delete_student)
        self.ui.DeleteSt_2.clicked.connect(self.delete_college)
        self.ui.DeleteSt_3.clicked.connect(self.delete_program)

        self.ui.tabWidget.setCurrentIndex(0)

        # Sorting
        self.ui.Sortbybox.currentIndexChanged.connect(self.sort_students)
        self.ui.Sortbox.currentIndexChanged.connect(self.sort_college)
        self.ui.Sortbybox_2.currentIndexChanged.connect(self.sort_program)

       #Combo Boxes 
    def populate_combo_boxes(self):
        self.ui.Yrlvlbox.clear()
        self.ui.genderbox.clear()
        self.ui.Yrlvlbox.addItems(["Please Select", "1st", "2nd", "3rd", "4th"])
        self.ui.genderbox.addItems(["Please Select", "M", "F", "Other"])
        self.ui.Yrlvlbox.setCurrentIndex(0)
        self.ui.genderbox.setCurrentIndex(0)

        self.ui.prcComboBox.clear()
        self.ui.prcComboBox.addItem("Please Select")
        self.ui.prcComboBox.addItems(self.program_codes)
        self.ui.prcComboBox.setCurrentIndex(0)

        self.ui.ccComboBox.clear()
        self.ui.ccComboBox.addItem("Please Select")
        self.ui.ccComboBox.addItems(self.college_codes)
        self.ui.ccComboBox.setCurrentIndex(0)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++   
    #STUDENTS
    def load_students(self):
        try:
            with open(CSV, "r", newline="") as file:
                reader = csv.reader(file)
                self.ui.StudentTable.setRowCount(0)
                for row_index, row_data in enumerate(reader):
                    self.ui.StudentTable.insertRow(row_index)
                    for col_index, data in enumerate(row_data):
                        self.ui.StudentTable.setItem(row_index, col_index, QTableWidgetItem(data))
        except FileNotFoundError:
            with open(CSV, "w", newline="") as file:
                pass  

    def student_exists(self, student_id):
        with open(CSV, "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == student_id:    
                    return True
        return False

    def add_student(self):
        #For adding student
        id = self.ui.IDnoBox.text().strip()
        fname = self.ui.FristNbox.text().strip()
        lastname = self.ui.LastNbox.text().strip()
        yearlevel = self.ui.Yrlvlbox.currentText().strip()
        gender = self.ui.genderbox.currentText().strip()
        code = self.ui.prcComboBox.currentText().strip()

        # Validators
        if not id or not fname or not lastname or not code or yearlevel == "Please Select" or gender == "Please Select":
            QMessageBox.warning(self, "Input Error", "All fields must be filled.")
            return

        if not self.student_idformat(id):
            QMessageBox.warning(self, "Input Error", "Invalid Student ID format. Must be in YYYY - NNNN format.")
            return
        
        if not self.student_nameformat(fname) or not self.student_nameformat(lastname):
            QMessageBox.warning(self, "Input Error", "Names must contain only letters and spaces!")
            return
        
        if not all(c.isalpha() or c.isspace() for c in code): 
            QMessageBox.warning(self, "Input Error", "Invalid Program Code! Only letters and spaces are allowed.")
            return
        
        if code not in self.program_codes:
            QMessageBox.warning(self, "Input Error", "Invalid Program Code!")
            return


        if self.student_exists(id):
            QMessageBox.warning(self, "Duplicate Entry", "Student ID already exists.")
            return
        
        college_code = self.programcollege_map.get(code, "")
        if college_code not in self.college_codes:
            QMessageBox.warning(self, "Input Error", "The College associated with this Program Code does not exist.")
            return

        if code not in self.program_codes:
            QMessageBox.warning(self, "Input Error", "Invalid Program Code! Please add the program first.")
            return
        
        # Saving
        with open(CSV, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([id, fname, lastname, yearlevel, gender, code])

        # Refresh the table and clear inputs
        self.load_students()
        QMessageBox.information(self, "Success", "Student added successfully.")
        self.clear_inputs()

    def clear_inputs(self):
        
        self.ui.IDnoBox.clear()
        self.ui.FristNbox.clear()
        self.ui.LastNbox.clear()
        self.ui.prcComboBox.setCurrentIndex(0)
        self.ui.Yrlvlbox.setCurrentIndex(0)  
        self.ui.genderbox.setCurrentIndex(0)  
    
    def student_idformat(self, student_id, edit_state=False):
        if not edit_state:
            valid_id_number = re.match(r'^[0-9]{4}-[0-9]{4}$', student_id)
        else:
            valid_id_number = re.match(r'^[0-9]{4}-[0-9]{4}$|^$', student_id)
        return True if valid_id_number else False
    
    def student_nameformat(self, name):
        valid_name = re.match(r'^[a-zA-Z]+(?:\s[a-zA-Z]+)*$', name)
        return True if valid_name else False 

    
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #COLLEGE  
    def load_colleges(self):
        try:
            with open(COLLEGE_CSV, mode="r") as file:
                reader = csv.reader(file)
                self.ui.COLLEGETABLE.setRowCount(0)
                self.college_codes.clear()
                for row in reader:
                    row_position = self.ui.COLLEGETABLE.rowCount()
                    self.ui.COLLEGETABLE.insertRow(row_position)
                    for col, data in enumerate(row):
                        self.ui.COLLEGETABLE.setItem(row_position, col, QTableWidgetItem(data))
                    if row:
                        self.college_codes.add(row[0])
            self.populate_combo_boxes()  # Update combo box
        except FileNotFoundError:
            open(COLLEGE_CSV, "w").close()

   
    def add_college(self):
        collegecode = self.ui.AddCCodeBox.text().strip()
        collegename = self.ui.CollegeNbox.text().strip()

        if not collegecode or not collegename:
            QMessageBox.warning(self, "Input Error", "All fields are required!")
            return
        
        
        with open(COLLEGE_CSV, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([collegecode, collegename])

        QMessageBox.information(self, "Success", "College added successfully!")
        self.load_colleges()  
        self.clear_course_inputs()
        self.populate_combo_boxes()

    def clear_course_inputs(self):
        self.ui.AddCCodeBox.clear()
        self.ui.CollegeNbox.clear()
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  
    #PROGRAMS
    def load_programs(self):
        try:
            with open(PROGRAM_CSV, mode="r") as file:
                reader = csv.reader(file)
                self.ui.COLLEGETABLE_2.setRowCount(0)
                self.program_codes.clear()
                for row in reader:
                    row_position = self.ui.COLLEGETABLE_2.rowCount()
                    self.ui.COLLEGETABLE_2.insertRow(row_position)
                    for col, data in enumerate(row):
                        self.ui.COLLEGETABLE_2.setItem(row_position, col, QTableWidgetItem(data))
                    if row and len(row) >= 2:
                        self.program_codes.add(row[0])  
                        self.programcollege_map[row[0]] = row[2]
            self.populate_combo_boxes()  # Update combo box
        except FileNotFoundError:
            open(PROGRAM_CSV, "w").close()

    
    def add_program(self):
        program_code = self.ui.PrCodeBox.text().strip()
        program_name = self.ui.ProgNbox.text().strip()
        college_code = self.ui.ccComboBox.currentText().strip()

        if not program_code or not program_name or college_code == "Please Select":
            QMessageBox.warning(self, "Input Error", "All fields are required!")
            return
        
        with open(PROGRAM_CSV, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([program_code, program_name, college_code])

        QMessageBox.information(self, "Success", "Program added successfully!")
        self.load_programs()
        self.clear_program_inputs()
        self.populate_combo_boxes()

    def clear_program_inputs(self):
        self.ui.PrCodeBox.clear()
        self.ui.ProgNbox.clear()
        self.ui.ccComboBox.clear()
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Delete Student 
    def delete_student(self):
        selected_row = self.ui.StudentTable.currentRow()
        if selected_row >= 0:
            self.ui.StudentTable.removeRow(selected_row)
            with open(CSV, "r") as file:
                rows= list(csv.reader(file))
            with open(CSV, "w", newline="") as file:        
                writer = csv.writer(file)
                for i, row in enumerate(rows):
                    if i != selected_row:
                        writer.writerow(row)
            QMessageBox.information(self, "Success", "Student deleted successfully!")
            self.load_students()      
    
    # Delete College
    def delete_college(self):
        selected_row = self.ui.COLLEGETABLE.currentRow()
        if selected_row >= 0:
            college_code = self.ui.COLLEGETABLE.item(selected_row, 0).text()

        # Remove College from Table
        self.ui.COLLEGETABLE.removeRow(selected_row)
    
        # Remove College from CSV
        with open(COLLEGE_CSV, "r") as file:
            rows = list(csv.reader(file))
        with open(COLLEGE_CSV, "w", newline="") as file:
            writer = csv.writer(file)
            for row in rows:
                if row[0] != college_code:
                    writer.writerow(row)
    
        # Remove Programs that are connected to College
        programs_to_remove = set()
        with open(PROGRAM_CSV, "r") as file:
            rows = list(csv.reader(file))
        with open(PROGRAM_CSV, "w", newline="") as file:
            writer = csv.writer(file)
            for row in rows:
                if row[2] != college_code:
                    writer.writerow(row)
                else:
                    programs_to_remove.add(row[0])  # Store deleted program codes

        # Unenroll Students who were in Deleted Programs
        with open(CSV, "r") as file:
            rows = list(csv.reader(file))
        with open(CSV, "w", newline="") as file:
            writer = csv.writer(file)
            for row in rows:
                if row[5] in programs_to_remove:  
                    row[5] = "Unenrolled"  # Change program column to "Unenrolled"
                writer.writerow(row)  # Write back all rows correctly

        # Show confirmation message
        QMessageBox.information(self, "Success", "College Deleted Successfully")
        
        # Refresh UI
        self.load_colleges()
        self.load_programs()
        self.load_students()
        self.populate_combo_boxes()  # Refresh dropdowns




    # Delete Program
    def delete_program(self):
        selected_row = self.ui.COLLEGETABLE_2.currentRow()
        if selected_row >= 0:
            program_code = self.ui.COLLEGETABLE_2.item(selected_row, 0).text()

        # Remove Program from Table
        self.ui.COLLEGETABLE_2.removeRow(selected_row)

        # Remove Program from CSV
        with open(PROGRAM_CSV, "r") as file:
            rows = list(csv.reader(file))
        with open(PROGRAM_CSV, "w", newline="") as file:
            writer = csv.writer(file)
            for row in rows:
                if row[0] != program_code:
                    writer.writerow(row)

        # 
        with open(CSV, "r") as file:
            rows = list(csv.reader(file))
        with open(CSV, "w", newline="") as file:
            writer = csv.writer(file)
            for row in rows:
                if row[5] == program_code:  
                    row[5] = "Unenrolled" 
                writer.writerow(row)  

        QMessageBox.information(self, "Success", "Program Deleted Successfully")

        self.load_programs()
        self.load_students()
        self.populate_combo_boxes()

    # Edit Student
    def edit_student(self):
        selected_row = self.ui.StudentTable.currentRow()
        if selected_row >= 0:
            self.ui.IDnoBox.setText(self.ui.StudentTable.item(selected_row, 0).text())
            self.ui.FristNbox.setText(self.ui.StudentTable.item(selected_row, 1).text())
            self.ui.LastNbox.setText(self.ui.StudentTable.item(selected_row, 2).text())
            self.ui.Yrlvlbox.setCurrentText(self.ui.StudentTable.item(selected_row, 3).text())
            self.ui.genderbox.setCurrentText(self.ui.StudentTable.item(selected_row, 4).text())
            self.ui.prcComboBox.setCurrentText(self.ui.StudentTable.item(selected_row, 5).text())
            self.ui.StudentTable.removeRow(selected_row)
            with open(CSV, "r") as file:
                rows = list(csv.reader(file))
            with open(CSV, "w", newline="") as file:
                writer = csv.writer(file)
                for i, row in enumerate(rows):
                    if i != selected_row:
                        writer.writerow(row)
            self.load_students()

    # Edit College
    def edit_college(self):
        selected_row = self.ui.COLLEGETABLE.currentRow()
        if selected_row >= 0:
            self.ui.AddCCodeBox.setText(self.ui.COLLEGETABLE.item(selected_row, 0).text())
            self.ui.CollegeNbox.setText(self.ui.COLLEGETABLE.item(selected_row, 1).text())
            self.ui.COLLEGETABLE.removeRow(selected_row)
            with open(COLLEGE_CSV, "r") as file:
                rows = list(csv.reader(file))
            with open(COLLEGE_CSV, "w", newline="") as file:
                writer = csv.writer(file)
                for i, row in enumerate(rows):
                    if i != selected_row:
                        writer.writerow(row)
            self.load_colleges()

    #Edit Program
    def edit_program(self):
        selected_row = self.ui.COLLEGETABLE_2.currentRow()
        if selected_row >= 0:
            self.ui.PrCodeBox.setText(self.ui.COLLEGETABLE_2.item(selected_row, 0).text())
            self.ui.ProgNbox.setText(self.ui.COLLEGETABLE_2.item(selected_row, 1).text())
            self.ui.ccComboBox.setCurrentText(self.ui.COLLEGETABLE_2.item(selected_row, 2).text())
            self.ui.COLLEGETABLE_2.removeRow(selected_row)
            with open(PROGRAM_CSV, "r") as file:
                rows = list(csv.reader(file))
            with open(PROGRAM_CSV, "w", newline="") as file:
                writer = csv.writer(file)
                for i, row in enumerate(rows):
                    if i != selected_row:
                        writer.writerow(row)
            self.load_programs()
    
    # Search Student
    def search_student(self):
        search_text = self.ui.Searchbybox.text().strip().lower()
        
        if not search_text:
            QMessageBox.warning(self, "Input Error", "Please enter a Student to search.")
            return
        if not search_text.isalnum():
            QMessageBox.warning(self, "Input Error", "Invalid Student ID!")
            return
        if not search_text.isalpha():
            QMessageBox.warning(self, "Input Error", "Invalid Student Name!")
            return
        
        with open(CSV, "r") as file:
            reader = csv.reader(file)
            self.ui.StudentTable.setRowCount(0)
            for row_data in reader:
                if any(search_text in str(data).lower() for data in row_data):
                    row_index = self.ui.StudentTable.rowCount()
                    self.ui.StudentTable.insertRow(row_index)
                    for col_index, data in enumerate(row_data):
                        self.ui.StudentTable.setItem(row_index, col_index, QTableWidgetItem(data))
        QMessageBox.information(self, "Search Results", "Search completed.")

    # Search College
    def search_college(self):
        search_c = self.ui.Searchbox.text().strip().lower()
        
        if not search_c:
            QMessageBox.warning(self, "Input Error", "Please enter a College to search.")
            return
        if not search_c.isalpha():
            QMessageBox.warning(self, "Input Error", "Invalid College Code!")
            return
        
        with open(COLLEGE_CSV, "r") as file:
            reader = csv.reader(file)
            self.ui.COLLEGETABLE.setRowCount(0)
            for row_data in reader:
                if any(search_c in str(data).lower() for data in row_data):
                    row_index = self.ui.COLLEGETABLE.rowCount()
                    self.ui.COLLEGETABLE.insertRow(row_index)
                    for col_index, data in enumerate(row_data):
                        self.ui.COLLEGETABLE.setItem(row_index, col_index, QTableWidgetItem(data))
        QMessageBox.information(self, "Search Results", "Search completed.")

    # Search Program
    def search_program(self):
        search_p = self.ui.Searchbybox_2.text().strip().lower()
        
        if not search_p:
            QMessageBox.warning(self, "Input Error", "Please enter a Program to search.")
            return
        if not search_p.isalpha():
            QMessageBox.warning(self, "Input Error", "Invalid Program Code!")
            return
        
        with open(PROGRAM_CSV, "r") as file:
            reader = csv.reader(file)
            self.ui.COLLEGETABLE_2.setRowCount(0)
            for row_data in reader:
                if any(search_p in str(data).lower() for data in row_data):
                    row_index = self.ui.COLLEGETABLE_2.rowCount()
                    self.ui.COLLEGETABLE_2.insertRow(row_index)
                    for col_index, data in enumerate(row_data):
                        self.ui.COLLEGETABLE_2.setItem(row_index, col_index, QTableWidgetItem(data))
        QMessageBox.information(self, "Search Results", "Search completed.")
    
    # Sorting Students
    def sort_students(self):
        column_index = self.ui.Sortbybox.currentIndex()  

        if column_index == 0: # When Select is pressed, it will revert back to its original order
            self.load_students()
            return

    
        sort_mapping = {
            1: 0,  # ID#
            2: 2,  # Last Name
            3: 5   # Program Code
        }

        if column_index not in sort_mapping:
            QMessageBox.warning(self, "Sort Error", "Please select a sorting option.")
            return

        column_index = sort_mapping[column_index]  # Get actual column index

    
        with open(CSV, "r", newline="") as file:
            reader = list(csv.reader(file))  

  
        if column_index == 0: 
            try:
                reader.sort(key=lambda row: (int(row[0][:4]), int(row[0][5:]))) 
            except ValueError:
                QMessageBox.warning(self, "Sort Error", "Invalid ID format in data.")
                return
        else:  
            reader.sort(key=lambda row: row[column_index].lower())

  
        self.ui.StudentTable.setRowCount(0)
        for row_data in reader:
            row_index = self.ui.StudentTable.rowCount()
            self.ui.StudentTable.insertRow(row_index)
            for col_index, data in enumerate(row_data):
                self.ui.StudentTable.setItem(row_index, col_index, QTableWidgetItem(data))

    # Sorting College
    def sort_college(self):
        column_index = self.ui.Sortbox.currentIndex()
        
        if column_index == 0: # When Select is pressed, it will revert back to its original order
            self.load_colleges()
            return

    
        sort_mapping = {
            1: 0,  # College Code
            2: 1,  # College Name
            
        }

        if column_index not in sort_mapping:
            QMessageBox.warning(self, "Sort Error", "Please select a sorting option.")
            return

        column_index = sort_mapping[column_index]  # Get actual column index

    
        with open(COLLEGE_CSV, "r", newline="") as file:
            reader = list(csv.reader(file))  

        reader.sort(key=lambda row: row[column_index].lower())

        self.ui.COLLEGETABLE.setRowCount(0)
        for row_data in reader:
            row_index = self.ui.COLLEGETABLE.rowCount()
            self.ui.COLLEGETABLE.insertRow(row_index)
            for col_index, data in enumerate(row_data):
                self.ui.COLLEGETABLE.setItem(row_index, col_index, QTableWidgetItem(data))
    
    # Sorting Program
    def sort_program(self):
        column_index = self.ui.Sortbybox_2.currentIndex()
        
        if column_index == 0: # When Select is pressed, it will revert back to its original order
            self.load_programs()
            return
        
        sort_mapping = {
            1: 0,  # Program Code
            2: 1,  # Program Name
            3: 2   # College Code
        }

        if column_index not in sort_mapping:
            QMessageBox.warning(self, "Sort Error", "Please select a sorting option.")
            return

        column_index = sort_mapping[column_index]  # Get actual column index

    
        with open(PROGRAM_CSV, "r", newline="") as file:
            reader = list(csv.reader(file))  

        reader.sort(key=lambda row: row[column_index].lower())

        self.ui.COLLEGETABLE_2.setRowCount(0)
        for row_data in reader:
            row_index = self.ui.COLLEGETABLE_2.rowCount()
            self.ui.COLLEGETABLE_2.insertRow(row_index)
            for col_index, data in enumerate(row_data):
                self.ui.COLLEGETABLE_2.setItem(row_index, col_index, QTableWidgetItem(data))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentSystem()
    window.setWindowTitle("Information System")
    window.show()
    sys.exit(app.exec_())
