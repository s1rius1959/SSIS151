import os
import re
import sys
import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from SSISFINAL import Ui_MainWindow 

# Get the directory where the script is running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define CSV file paths inside the current script directory
StudentCSV = os.path.join(BASE_DIR, "students.csv")
CollegeCSV = os.path.join(BASE_DIR, "colleges.csv")
ProgramCSV = os.path.join(BASE_DIR, "programs.csv")


class StudentSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Information System")
        #self.setWindowIcon
    
     

        # Initialize Combo Boxes For Program and College Code
        self.Program_Code = set()
        self.College_Code = set()
        self.ProgramCollegeMap = {}

        # Add Buttons
        self.ui.AddSt.clicked.connect(self.AddStudent)
        self.ui.AddCo.clicked.connect(self.AddCollege)
        self.ui.AddProg.clicked.connect(self.AddProgram)
        self.ui.EditSt.clicked.connect(self.EditStudent)
        self.ui.EditSt_2.clicked.connect(self.EditCollege)
        self.ui.EditSt_3.clicked.connect(self.EditProgram)
        self.ui.SEARCHbutton.clicked.connect(self.SearchStudent)
        self.ui.Searchbutton.clicked.connect(self.SearchCollege)
        self.ui.Searchbutton_2.clicked.connect(self.SearchProgram)
        
        # Load 
        self.LoadStudent()
        self.LoadCollege()
        self.LoadProgram()
        self.SaveOriginalPrograms()
        self.combo_boxes()

        # Deleting
        self.ui.DeleteSt.clicked.connect(self.DeleteStudent)
        self.ui.DeleteSt_2.clicked.connect(self.DeleteCollege)
        self.ui.DeleteSt_3.clicked.connect(self.DeleteProgram)

        self.ui.tabWidget.setCurrentIndex(0)

        # Filter Search 
        self.ui.Sortbybox.currentIndexChanged.connect(self.FilterStudents)
        self.ui.Searchbybox.textChanged.connect(self.FilterStudents)

        self.ui.Sortbox.currentIndexChanged.connect(self.FilterColleges)
        self.ui.Searchbox.textChanged.connect(self.FilterColleges)

        self.ui.Sortbybox_2.currentIndexChanged.connect(self.FilterPrograms)
        self.ui.Searchbybox_2.textChanged.connect(self.FilterPrograms)
        
        # REFRESH
        self.ui.SREFRESH.clicked.connect(self.StudentRefresh)
        self.ui.CREFRESH.clicked.connect(self.CollegeRefresh)
        self.ui.REFRESH.clicked.connect(self.ProgramRefresh)  

        # Updater
        self.ui.SLoad.clicked.connect(self.StudentsUpdate)

       #Combo Boxes 
    def combo_boxes(self):
        self.ui.Yrlvlbox.clear()
        self.ui.genderbox.clear()
        self.ui.Yrlvlbox.addItems(["Please Select", "1st", "2nd", "3rd", "4th"])
        self.ui.genderbox.addItems(["Please Select", "M", "F", "Other"])
        self.ui.Yrlvlbox.setCurrentIndex(0)
        self.ui.genderbox.setCurrentIndex(0)

        self.ui.prcComboBox.clear()
        self.ui.prcComboBox.addItem("Please Select")
        self.ui.prcComboBox.addItems(self.Program_Code)
        self.ui.prcComboBox.setCurrentIndex(0)

        self.ui.ccComboBox.clear()
        self.ui.ccComboBox.addItem("Please Select")
        self.ui.ccComboBox.addItems(self.College_Code)
        self.ui.ccComboBox.setCurrentIndex(0)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++   
    #STUDENTS

    def AddStudent(self):
        
        sorting_enabled = self.ui.StudentTable.isSortingEnabled()
        sort_column = self.ui.StudentTable.horizontalHeader().sortIndicatorSection()
        sort_order = self.ui.StudentTable.horizontalHeader().sortIndicatorOrder()

        self.ui.StudentTable.setSortingEnabled(False)

        #Initializing
        id = self.ui.IDnoBox.text().strip()
        fname = self.ui.FristNbox.text().strip()
        lastname = self.ui.LastNbox.text().strip()
        yearlevel = self.ui.Yrlvlbox.currentText().strip()
        gender = self.ui.genderbox.currentText().strip()
        code = self.ui.prcComboBox.currentText().strip()

        # Validating Add Student Inputs
        if not id or not fname or not lastname or not code or yearlevel == "Please Select" or gender == "Please Select":
            QMessageBox.warning(self, "Input Error", "All fields must be filled.")
            return

        if not self.studentidformat(id):
            QMessageBox.warning(self, "Input Error", "Invalid Student ID format. Must be in YYYY - NNNN format.")
            return
        
        if not self.studentnameformat(fname) or not self.studentnameformat(lastname):
            QMessageBox.warning(self, "Input Error", "Names must contain only letters and spaces!")
            return
        
        if not all(c.isalpha() or c.isspace() for c in code): 
            QMessageBox.warning(self, "Input Error", "Invalid Program Code! Only letters and spaces are allowed.")
            return
        
        if code not in self.Program_Code:
            QMessageBox.warning(self, "Input Error", "Invalid Program Code!")
            return


        if self.studentexists(id):
            QMessageBox.warning(self, "Duplicate Entry", "Student ID already exists.")
            return
        
        college_code = self.ProgramCollegeMap.get(code, "")
        if college_code not in self.College_Code:
            QMessageBox.warning(self, "Input Error", "The College associated with this Program Code does not exist.")
            return

        if code not in self.Program_Code:
            QMessageBox.warning(self, "Input Error", "Invalid Program Code! Please add the program first.")
            return
        
        # Saving
        with open(StudentCSV, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([id, fname, lastname, yearlevel, gender, code])
        
        row_index = self.ui.StudentTable.rowCount()
        self.ui.StudentTable.insertRow(row_index)
        student_data = [id, fname, lastname, yearlevel, gender, code]

        for col_index, data in enumerate(student_data):
            self.ui.StudentTable.setItem(row_index, col_index, QTableWidgetItem(data))

        self.ui.StudentTable.setSortingEnabled(sorting_enabled)
        if sorting_enabled:
            self.ui.StudentTable.sortItems(sort_column, sort_order)
            
        QMessageBox.information(self, "Success", "Student added successfully.")
        self.ClearStudentInputs()
    
    def StudentsUpdate(self):
        try:
            original_program_path = os.path.join(BASE_DIR, "programs_original.csv")

            # Step 1: Load OLD Programs from programs_original.csv
            old_programs = {}
            if os.path.exists(original_program_path):
                with open(original_program_path, "r", newline="") as file:
                    reader = csv.reader(file)
                    old_program_header = next(reader, None)
                    for row in reader:
                        if row and len(row) >= 3:
                            old_program_code = row[0].strip()
                            old_programs[old_program_code] = (row[1].strip(), row[2].strip())  # (Program Name, College Code)

            # Step 2: Load NEW Programs from current Program Table
            new_programs = {}
            for row in range(self.ui.COLLEGETABLE_2.rowCount()):
                program_code = self.ui.COLLEGETABLE_2.item(row, 0).text().strip()
                program_name = self.ui.COLLEGETABLE_2.item(row, 1).text().strip()
                college_code = self.ui.COLLEGETABLE_2.item(row, 2).text().strip()
                if program_code:
                    new_programs[program_code] = (program_name, college_code)

            # Step 3: Build mapping OLD ➔ NEW
            program_code_mapping = {}
            for old_code, (old_name, old_college) in old_programs.items():
                for new_code, (new_name, new_college) in new_programs.items():
                    if old_name == new_name and old_college == new_college:
                        program_code_mapping[old_code] = new_code
                        break
                else:
                    program_code_mapping[old_code] = "NONE"

            # Step 4: Load students
            students = []
            if os.path.exists(StudentCSV):
                with open(StudentCSV, "r", newline="") as file:
                    reader = csv.reader(file)
                    student_header = next(reader, None)
                    for row in reader:
                        if row and len(row) >= 6:
                            students.append(row)

            # Step 5: Update students
            for student in students:
                old_program_code = student[5].strip()
                new_program_code = program_code_mapping.get(old_program_code, "NONE")
                student[5] = new_program_code

            # Step 6: Save students
            with open(StudentCSV, "w", newline="") as file:
                writer = csv.writer(file)
                if student_header:
                    writer.writerow(student_header)
                writer.writerows(students)

            # After successful update, re-save a fresh backup of programs
            self.SaveOriginalPrograms()

            self.LoadStudent()
            QMessageBox.information(self, "Success", "Student Program Codes have been updated based on Program changes.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while updating student programs: {e}")


    def SaveOriginalPrograms(self):
        try:
            original_path = os.path.join(BASE_DIR, "programs_original.csv")
            with open(ProgramCSV, "r", newline="") as source, open(original_path, "w", newline="") as dest:
                dest.write(source.read())
        except Exception as e:
            print(f"Error saving original programs: {e}")



    
    def LoadStudent(self):
        
        if not os.path.exists(StudentCSV):
            with open(StudentCSV, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "First Name", "Last Name", "Year Level", "Gender", "Program Code"]) 

        with open(StudentCSV, "r", newline="") as file:
            reader = csv.reader(file)
            self.ui.StudentTable.setRowCount(0)
            next(reader, None)  
            for row_index, row_data in enumerate(reader):
                self.ui.StudentTable.insertRow(row_index)
                for col_index, data in enumerate(row_data):
                    self.ui.StudentTable.setItem(row_index, col_index, QTableWidgetItem(data))
    
    #Check if Student Exists
    def studentexists(self, student_id):
        with open(StudentCSV, "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == student_id:    
                    return True
        return False
    
    # Clearing Add Student Inputs
    def ClearStudentInputs(self):
        
        self.ui.IDnoBox.clear()
        self.ui.FristNbox.clear()
        self.ui.LastNbox.clear()
        self.ui.prcComboBox.setCurrentIndex(0)
        self.ui.Yrlvlbox.setCurrentIndex(0)  
        self.ui.genderbox.setCurrentIndex(0)  

    # ID Format
    def studentidformat(self, student_id):
            valid_id_number = re.match(r'^\d{4}-\d{4}$', student_id)
            return bool(valid_id_number)
    # Name Format
    def studentnameformat(self, name):
        valid_name = re.match(r'^[a-zA-Z]+(?:\s[a-zA-Z]+)*$', name)
        return True if valid_name else False 
    # Deleting Student
    def DeleteStudent(self):
        try:
            selected_row = self.ui.StudentTable.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Input Error", "Please select a Student to delete.")
                return
            
            sorting_enabled = self.ui.StudentTable.isSortingEnabled()
            sort_column = self.ui.StudentTable.horizontalHeader().sortIndicatorSection()
            sort_order = self.ui.StudentTable.horizontalHeader().sortIndicatorOrder()
            self.ui.StudentTable.setSortingEnabled(False)

            student_data = [self.ui.StudentTable.item(selected_row, col).text() for col in range(self.ui.StudentTable.columnCount())]

            reply = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete student?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.No:
                return
            
            with open(StudentCSV, "r", newline="") as file:
                rows = list(csv.reader(file))

            with open(StudentCSV, "w", newline="") as file:
                writer = csv.writer(file)
                for row in rows:
                    if row and row != student_data:  # Keep all rows except the selected one
                        writer.writerow(row)
            
            self.LoadStudent()

            self.ui.StudentTable.setSortingEnabled(sorting_enabled)
            if sorting_enabled:
                self.ui.StudentTable.sortItems(sort_column, sort_order)

            
            QMessageBox.information(self, "Success", "Student deleted successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while deleting the student: {e}")
    

    # Edit Student
    def EditStudent(self):
        selectedrow = self.ui.StudentTable.currentRow()
    
        if selectedrow < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a student to edit.")
            return

        # original student data
        student_id = self.ui.StudentTable.item(selectedrow, 0).text()
        fname = self.ui.StudentTable.item(selectedrow, 1).text()
        lastname = self.ui.StudentTable.item(selectedrow, 2).text()
        yearlevel = self.ui.StudentTable.item(selectedrow, 3).text()
        gender = self.ui.StudentTable.item(selectedrow, 4).text()
        program_code = self.ui.StudentTable.item(selectedrow, 5).text()

        # For Inputs
        self.ui.IDnoBox.setText(student_id)
        self.ui.FristNbox.setText(fname)
        self.ui.LastNbox.setText(lastname)
        self.ui.Yrlvlbox.setCurrentText(yearlevel)
        self.ui.genderbox.setCurrentText(gender)
        self.ui.prcComboBox.setCurrentText(program_code)

        # Remove the selected student from the CSV
        try:
            with open(StudentCSV, "r", newline="") as file:
                Sedit = list(csv.reader(file))

            with open(StudentCSV, "w", newline="") as file:
                writer = csv.writer(file)
                for row in Sedit:
                    if row and row[0] != student_id:  
                        writer.writerow(row)

            # Remove row from UI table
            self.ui.StudentTable.removeRow(selectedrow)

            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while editing the student: {e}")

    # Search Student
    def SearchStudent(self):
        search_text = self.ui.Searchbybox.text().strip().lower()

        if not search_text:
            self.LoadStudent()  # Reload all students if search box is empty
            return

    # Allow valid student ID format (YYYY-NNNN) or names
        if not re.match(r'^\d{4}-\d{4}$', search_text) and not search_text.replace(" ", "").isalpha():
            QMessageBox.warning(self, "Input Error", "Search must be a valid Student ID (YYYY-NNNN) or a Name!")
            return

        with open(StudentCSV, "r") as file:
            reader = csv.reader(file)
            self.ui.StudentTable.setRowCount(0)
            next(reader, None)  

            for row_data in reader:
                if any(search_text in str(data).lower() for data in row_data):
                    row_index = self.ui.StudentTable.rowCount()
                    self.ui.StudentTable.insertRow(row_index)
                    for col_index, data in enumerate(row_data):
                        self.ui.StudentTable.setItem(row_index, col_index, QTableWidgetItem(data))

        QMessageBox.information(self, "Search Results", "Search completed.")

    def FilterStudents(self):
        search_text = self.ui.Searchbybox.text().strip().lower()
        selected_filter = self.ui.Sortbybox.currentIndex() 

        if not search_text:
            self.LoadStudent()  # Reload all students if search box is empty
            return

        
        filter_map = {
            1: 0,  # ID
            2: 1,  # First Name
            3: 2,  # Last Name
            4: 3,  # Year Level
            5: 4,  # Gender
            6: 5   # Program Code
        }

        if selected_filter not in filter_map:
            QMessageBox.warning(self, "Filter Error", "Please select a valid filtering option.")
            return

        filter_column = filter_map[selected_filter]  

        with open(StudentCSV, "r", newline="") as file:
            reader = csv.reader(file)
            self.ui.StudentTable.setRowCount(0)
            next(reader, None)  

            for row_data in reader:
            # Compare only the selected column for filtering
                if search_text in row_data[filter_column].lower():
                    row_index = self.ui.StudentTable.rowCount()
                    self.ui.StudentTable.insertRow(row_index)
                    for col_index, data in enumerate(row_data):
                        self.ui.StudentTable.setItem(row_index, col_index, QTableWidgetItem(data))
    
    def StudentRefresh(self):
        
        self.ui.StudentTable.setSortingEnabled(False)  

    # Reset search box and filter combo box
        self.ui.Searchbybox.clear()
        self.ui.Sortbybox.setCurrentIndex(0)  

        self.ui.StudentTable.horizontalHeader().setSortIndicator(-1, 0)  

    # Reload student data in original CSV order
        self.LoadStudent()

        self.ui.StudentTable.setSortingEnabled(True) 

        QMessageBox.information(self, "Refreshed", "Student table has been reset to its original order.")
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #COLLEGE  
    def AddCollege(self):
        try: 
            collegecode = self.ui.AddCCodeBox.text().strip().upper()
            collegename = self.ui.CollegeNbox.text().strip()

            # Validating Add College Inputs
            if not collegecode or not collegename:
                QMessageBox.warning(self, "Input Error", "All fields are required!")
                return
            if not collegecode.isalpha(): 
                QMessageBox.warning(self, "Input Error", "Invalid College Code! Only letters are allowed.")
                return
            if not all(c.isalpha() or c.isspace() for c in collegename): 
                QMessageBox.warning(self, "Input Error", "Invalid College Name! Only letters and spaces are allowed.")
                return

            # Check if the college already exists
            with open(CollegeCSV, "r", newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and row[0].strip().upper() == collegecode:
                        QMessageBox.warning(self, "Duplicate Entry", "College Code already exists!")
                        return

            sorting_enabled = self.ui.COLLEGETABLE.isSortingEnabled()
            sort_column = self.ui.COLLEGETABLE.horizontalHeader().sortIndicatorSection()
            sort_order = self.ui.COLLEGETABLE.horizontalHeader().sortIndicatorOrder()

            self.ui.COLLEGETABLE.setSortingEnabled(False)

            # Add new college to the CSV file
            with open(CollegeCSV, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([collegecode, collegename])

            # Add new row to the table directly (without reloading all data)
            row_index = self.ui.COLLEGETABLE.rowCount()
            self.ui.COLLEGETABLE.insertRow(row_index)
            self.ui.COLLEGETABLE.setItem(row_index, 0, QTableWidgetItem(collegecode))
            self.ui.COLLEGETABLE.setItem(row_index, 1, QTableWidgetItem(collegename))

            self.College_Code.add(collegecode)  # Update college code set
            self.combo_boxes()

            # Restore sorting
            self.ui.COLLEGETABLE.setSortingEnabled(sorting_enabled)
            if sorting_enabled:
                self.ui.COLLEGETABLE.sortItems(sort_column, sort_order)

            QMessageBox.information(self, "Success", "College added successfully!")
            self.ClearCollegeInputs()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while adding the College: {e}")


    # Clearing Add College Inputs
    def ClearCollegeInputs(self):
        self.ui.AddCCodeBox.clear()
        self.ui.CollegeNbox.clear()

    def LoadCollege(self):
        
        if not os.path.exists(CollegeCSV):
            with open(CollegeCSV, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["College Code", "College Name"]) 

        with open(CollegeCSV, mode="r", newline="") as file:
            reader = csv.reader(file)
            self.ui.COLLEGETABLE.setRowCount(0)
            self.College_Code.clear()
            next(reader, None)  
            for row in reader:
                row_position = self.ui.COLLEGETABLE.rowCount()
                self.ui.COLLEGETABLE.insertRow(row_position)
                for col, data in enumerate(row):
                    self.ui.COLLEGETABLE.setItem(row_position, col, QTableWidgetItem(data))
                if row:
                    self.College_Code.add(row[0])
            self.combo_boxes()
    
    
     # Delete College
    def DeleteCollege(self):
        try:
            selected_row = self.ui.COLLEGETABLE.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Input Error", "Please select a College to delete.")
                return

            # For Sorting
            sorting_enabled = self.ui.COLLEGETABLE.isSortingEnabled()
            sort_column = self.ui.COLLEGETABLE.horizontalHeader().sortIndicatorSection()
            sort_order = self.ui.COLLEGETABLE.horizontalHeader().sortIndicatorOrder()
            self.ui.COLLEGETABLE.setSortingEnabled(False)

            # Get College Code from the selected row
            college_code = self.ui.COLLEGETABLE.item(selected_row, 0).text()

            reply = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete college?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

            # Read all colleges and remove the selected one
            with open(CollegeCSV, "r", newline="") as file:
                rows = list(csv.reader(file))
        
            with open(CollegeCSV, "w", newline="") as file:
                writer = csv.writer(file)
                for row in rows:
                    if row and row[0] != college_code:  # Keep all except the deleted college
                        writer.writerow(row)

            # Remove programs associated with the deleted college
            programs_to_remove = set()
            with open(ProgramCSV, "r", newline="") as file:
                rows = list(csv.reader(file))

            with open(ProgramCSV, "w", newline="") as file:
                writer = csv.writer(file)
                for row in rows:
                    if row[2] != college_code:
                        writer.writerow(row)
                    else:
                        programs_to_remove.add(row[0])  

            # "NONE" for students in the deleted programs
            with open(StudentCSV, "r", newline="") as file:
                rows = list(csv.reader(file))

            with open(StudentCSV, "w", newline="") as file:
                writer = csv.writer(file)
                for row in rows:
                    if row[5] in programs_to_remove: 
                        row[5] = "NONE"  # Set program to NONE
                    writer.writerow(row)

            # Reload tables
            self.LoadCollege()
            self.LoadProgram()
            self.LoadStudent()

            # Restore sorting
            self.ui.COLLEGETABLE.setSortingEnabled(sorting_enabled)
            if sorting_enabled:
                self.ui.COLLEGETABLE.sortItems(sort_column, sort_order)

            QMessageBox.information(self, "Success", "College and its associated programs have been deleted.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while deleting the college: {e}")


    # Edit College
    def EditCollege(self):
        selected_row = self.ui.COLLEGETABLE.currentRow()

        if selected_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a College to edit.")
            return

        # original college data
        college_code = self.ui.COLLEGETABLE.item(selected_row, 0).text()
        college_name = self.ui.COLLEGETABLE.item(selected_row, 1).text()

        # For Inputs
        self.ui.AddCCodeBox.setText(college_code)
        self.ui.CollegeNbox.setText(college_name)

        # For Header Glitch and Removing the Selected College
        try:
        
            with open(CollegeCSV, "r", newline="") as file:
                reader = csv.reader(file)
                rows = list(reader)

            # For Header Glitch and Removing the Selected College
            if rows and rows[0] == ["College Code", "College Name"]:
                header = rows[0]  
                data_rows = rows[1:]  
            else:
                header = ["College Code", "College Name"]
                data_rows = rows

            # For Removing
            new_rows = [row for row in data_rows if row and row[0] != college_code]

            # keep the header only if there are remaining rows
            with open(CollegeCSV, "w", newline="") as file:
                writer = csv.writer(file)
                if new_rows:  
                    writer.writerow(header)  
                    writer.writerows(new_rows)
        
            # Remove a row from the Table
            self.ui.COLLEGETABLE.removeRow(selected_row)

            # For updating
            self.LoadCollege()

            QMessageBox.information(self, "Editing", "College removed. You can now update its information and add it again.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while editing the college: {e}")


    # Search College
    def SearchCollege(self):
        search_c = self.ui.Searchbox.text().strip().lower()
        
        if not search_c:
            self.LoadCollege()
            return
        if not search_c.isalpha():
            QMessageBox.warning(self, "Input Error", "Invalid College Code or College Name!")
            return
        
        
        with open(CollegeCSV, "r") as file:
            reader = csv.reader(file)
            self.ui.COLLEGETABLE.setRowCount(0)
            for row_data in reader:
                if any(search_c in str(data).lower() for data in row_data):
                    row_index = self.ui.COLLEGETABLE.rowCount()
                    self.ui.COLLEGETABLE.insertRow(row_index)
                    for col_index, data in enumerate(row_data):
                        self.ui.COLLEGETABLE.setItem(row_index, col_index, QTableWidgetItem(data))
        QMessageBox.information(self, "Search Results", "Search completed.")

    # Filter Search
    def FilterColleges(self):
        search_text = self.ui.Searchbox.text().strip().lower()
        selected_filter = self.ui.Sortbox.currentIndex()  # Get selected combo box index

        if not search_text:
            self.LoadCollege()  # Reload all colleges if search box is empty
            return

        # Map dropdown selection to CSV column index
        filter_map = {
            1: 0,  # College Code
            2: 1   # College Name
        }

        if selected_filter not in filter_map:
            QMessageBox.warning(self, "Filter Error", "Please select a valid filtering option.")
            return

        filter_column = filter_map[selected_filter]  # Get actual column index

        with open(CollegeCSV, "r", newline="") as file:
            reader = csv.reader(file)
            self.ui.COLLEGETABLE.setRowCount(0)
            next(reader, None)  # Skip header row

            for row_data in reader:
                if search_text in row_data[filter_column].lower():  # Match filter selection
                    row_index = self.ui.COLLEGETABLE.rowCount()
                    self.ui.COLLEGETABLE.insertRow(row_index)
                    for col_index, data in enumerate(row_data):
                        self.ui.COLLEGETABLE.setItem(row_index, col_index, QTableWidgetItem(data))
    
    def CollegeRefresh(self):
        self.ui.COLLEGETABLE.setSortingEnabled(False) 

        # Reset search box and filter combo box
        self.ui.Searchbox.clear()
        self.ui.Sortbox.setCurrentIndex(0)  

        # Reset sorting order (column & direction)
        self.ui.COLLEGETABLE.horizontalHeader().setSortIndicator(-1, 0)  

        # Reload college data in original CSV order
        self.LoadCollege()

        self.ui.COLLEGETABLE.setSortingEnabled(True)  

        QMessageBox.information(self, "Refreshed", "College table has been reset to its original order.")


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  
    #PROGRAMS
    def AddProgram(self):
        try:
            programcode = self.ui.PrCodeBox.text().strip()
            programname = self.ui.ProgNbox.text().strip()
            collegecode = self.ui.ccComboBox.currentText().strip()

            # Validating Add Program Inputs
            if not programcode or not programname or collegecode == "Please Select":
                QMessageBox.warning(self, "Input Error", "All fields are required!")
                return
            if not all(c.isalpha() or c.isspace() for c in programcode): 
                QMessageBox.warning(self, "Input Error", "Invalid Program Code! Only letters and spaces are allowed.")
                return
            if not all(c.isalpha() or c.isspace() for c in programname): 
                QMessageBox.warning(self, "Input Error", "Invalid Program Name! Only letters and spaces are allowed.")
                return
            if collegecode not in self.College_Code:
                QMessageBox.warning(self, "Input Error", "The selected College Code does not exist.")
                return  
            
             # Check if the program already exists
            with open(ProgramCSV, "r", newline="") as file:
                reader = csv.reader(file)
                for row in reader:
                    if row and row[0].strip() == programcode:
                        QMessageBox.warning(self, "Duplicate Entry", "Program Code already exists!")
                        return
        
            sorting_enabled = self.ui.COLLEGETABLE_2.isSortingEnabled()
            sort_column = self.ui.COLLEGETABLE_2.horizontalHeader().sortIndicatorSection() 
            sort_order = self.ui.COLLEGETABLE_2.horizontalHeader().sortIndicatorOrder()

            self.ui.COLLEGETABLE_2.setSortingEnabled(False)


            with open(ProgramCSV, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([programcode, programname, collegecode])

            # Add new row to the table directly (without reloading all data)
            row_index = self.ui.COLLEGETABLE_2.rowCount()
            self.ui.COLLEGETABLE_2.insertRow(row_index)
            program_data = [programcode, programname, collegecode]
            for col_index, data in enumerate(program_data):
                self.ui.COLLEGETABLE_2.setItem(row_index, col_index, QTableWidgetItem(data))


            self.Program_Code.add(programcode)  # Update program code set
            self.ProgramCollegeMap[programcode] = collegecode
            self.combo_boxes()

            

            # Restore sorting
            self.ui.COLLEGETABLE_2.setSortingEnabled(sorting_enabled)
            if sorting_enabled:
                self.ui.COLLEGETABLE_2.sortItems(sort_column, sort_order)

            QMessageBox.information(self, "Success", "Program added successfully!")
            self.ClearProgramInputs()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while adding the Program: {e}")

    def LoadProgram(self):
    
        if not os.path.exists(ProgramCSV):
            with open(ProgramCSV, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Program Code", "Program Name", "College Code"])  # Header row

        with open(ProgramCSV, mode="r", newline="") as file:
            reader = csv.reader(file)
            self.ui.COLLEGETABLE_2.setRowCount(0)
            self.Program_Code.clear()
            next(reader, None)  
            for row in reader:
                row_position = self.ui.COLLEGETABLE_2.rowCount()
                self.ui.COLLEGETABLE_2.insertRow(row_position)
                for col, data in enumerate(row):
                    self.ui.COLLEGETABLE_2.setItem(row_position, col, QTableWidgetItem(data))
                if row and len(row) >= 2:
                    self.Program_Code.add(row[0])  
                    self.ProgramCollegeMap[row[0]] = row[2]
            self.combo_boxes()


    # Clear Add Program Inputs
    def ClearProgramInputs(self):
        self.ui.PrCodeBox.clear()
        self.ui.ProgNbox.clear()
        self.ui.ccComboBox.setCurrentIndex(0)
    
    # Delete Program
    def DeleteProgram(self):
        try:
            selected_row = self.ui.COLLEGETABLE_2.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Input Error", "Please select a Program to delete.")
                return

            # For Sorting 
            sorting_enabled = self.ui.COLLEGETABLE_2.isSortingEnabled()
            sort_column = self.ui.COLLEGETABLE_2.horizontalHeader().sortIndicatorSection()
            sort_order = self.ui.COLLEGETABLE_2.horizontalHeader().sortIndicatorOrder()
            self.ui.COLLEGETABLE_2.setSortingEnabled(False)

            # Get Program Code from the selected row
            program_code = self.ui.COLLEGETABLE_2.item(selected_row, 0).text()

            reply = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete student?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

            # Read all programs and remove the selected one
            with open(ProgramCSV, "r", newline="") as file:
                rows = list(csv.reader(file))

            with open(ProgramCSV, "w", newline="") as file:
                writer = csv.writer(file)
                for row in rows:
                    if row and row[0] != program_code:  
                        writer.writerow(row)

            # "NONE" if the Program is removed
            with open(StudentCSV, "r", newline="") as file:
                rows = list(csv.reader(file))

            with open(StudentCSV, "w", newline="") as file:
                writer = csv.writer(file)
                for row in rows:
                    if row[5] == program_code: 
                        row[5] = "NONE"  # Set program to NONE
                    writer.writerow(row)

            # Reload tables
            self.LoadProgram()
            self.LoadStudent()

            # Restore sorting
            self.ui.COLLEGETABLE_2.setSortingEnabled(sorting_enabled)
            if sorting_enabled:
                self.ui.COLLEGETABLE_2.sortItems(sort_column, sort_order)

            QMessageBox.information(self, "Success", "Program deleted successfully, and students have been updated.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while deleting the program: {e}")

    #Edit Program
    def EditProgram(self):
        selected_row = self.ui.COLLEGETABLE_2.currentRow()

        if selected_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a Program to edit.")
            return

        # original program data
        program_code = self.ui.COLLEGETABLE_2.item(selected_row, 0).text()
        program_name = self.ui.COLLEGETABLE_2.item(selected_row, 1).text()
        college_code = self.ui.COLLEGETABLE_2.item(selected_row, 2).text()

        # For Inputs
        self.ui.PrCodeBox.setText(program_code)
        self.ui.ProgNbox.setText(program_name)
        self.ui.ccComboBox.setCurrentText(college_code)

        # For Header Glitch and Removing the Selected Program
        try:
          
            with open(ProgramCSV, "r", newline="") as file:
                reader = csv.reader(file)
                rows = list(reader)

            # Header Glitch
            if rows and rows[0] == ["Program Code", "Program Name", "College Code"]:
                header = rows[0]  
                data_rows = rows[1:] 
            else:
                header = ["Program Code", "Program Name", "College Code"]
                data_rows = rows

            # For Removing
            new_rows = [row for row in data_rows if row and row[0] != program_code]

            # keep the header only if there are remaining rows
            with open(ProgramCSV, "w", newline="") as file:
                writer = csv.writer(file)
                if new_rows:  
                    writer.writerow(header)  
                    writer.writerows(new_rows)
        
            # Remove a row from the Table
            self.ui.COLLEGETABLE_2.removeRow(selected_row)

            # For updating
            self.LoadProgram()

            QMessageBox.information(self, "Editing", "Program removed. You can now update its information and add it again.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while editing the program: {e}")
    
    # Search Program
    def SearchProgram(self):
        search_p = self.ui.Searchbybox_2.text().strip().lower()
        
        if not search_p:
            self.LoadProgram()
            return
        if not search_p.isalpha():
            QMessageBox.warning(self, "Input Error", "Invalid Program Code or Program Name or College Code!")
            return
        
        with open(ProgramCSV, "r") as file:
            reader = csv.reader(file)
            self.ui.COLLEGETABLE_2.setRowCount(0)
            for row_data in reader:
                if any(search_p in str(data).lower() for data in row_data):
                    row_index = self.ui.COLLEGETABLE_2.rowCount()
                    self.ui.COLLEGETABLE_2.insertRow(row_index)
                    for col_index, data in enumerate(row_data):
                        self.ui.COLLEGETABLE_2.setItem(row_index, col_index, QTableWidgetItem(data))
        QMessageBox.information(self, "Search Results", "Search completed.")
    
    
    # Sorting Program
    def FilterPrograms(self):
        search_text = self.ui.Searchbybox_2.text().strip().lower()
        selected_filter = self.ui.Sortbybox_2.currentIndex()  

        if not search_text:
            self.LoadProgram()  # Reload all programs if search box is empty
            return

        # Map dropdown selection to CSV column index
        filter_map = {
        1: 0,  # Program Code
        2: 1,  # Program Name
        3: 2   # College Code
    }

        if selected_filter not in filter_map:
            QMessageBox.warning(self, "Filter Error", "Please select a valid filtering option.")
            return

        filter_column = filter_map[selected_filter]  # Get actual column index

        with open(ProgramCSV, "r", newline="") as file:
            reader = csv.reader(file)
            self.ui.COLLEGETABLE_2.setRowCount(0)
            next(reader, None)  # Skip header row

        for row_data in reader:
            if search_text in row_data[filter_column].lower():  # Match filter selection
                row_index = self.ui.COLLEGETABLE_2.rowCount()
                self.ui.COLLEGETABLE_2.insertRow(row_index)
                for col_index, data in enumerate(row_data):
                    self.ui.COLLEGETABLE_2.setItem(row_index, col_index, QTableWidgetItem(data))
    
    def ProgramRefresh(self):
        self.ui.COLLEGETABLE_2.setSortingEnabled(False)  

        # Reset search box and filter combo box
        self.ui.Searchbybox_2.clear()
        self.ui.Sortbybox_2.setCurrentIndex(0)  

        # Reset sorting order (column & direction)
        self.ui.COLLEGETABLE_2.horizontalHeader().setSortIndicator(-1, 0)  

        
        self.LoadProgram()

        self.ui.COLLEGETABLE_2.setSortingEnabled(True) 

        QMessageBox.information(self, "Refreshed", "Program table has been reset to its original order.")

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentSystem()
    window.setWindowTitle("Information System")
    window.show()
    sys.exit(app.exec_())
