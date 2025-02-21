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
        self.combo_boxes()

        # Deleting
        self.ui.DeleteSt.clicked.connect(self.DeleteStudent)
        self.ui.DeleteSt_2.clicked.connect(self.DeleteCollege)
        self.ui.DeleteSt_3.clicked.connect(self.DeleteProgram)

        self.ui.tabWidget.setCurrentIndex(0)

        # Sorting
        self.ui.Sortbybox.currentIndexChanged.connect(self.SortStudents)
        self.ui.Sortbox.currentIndexChanged.connect(self.SortCollege)
        self.ui.Sortbybox_2.currentIndexChanged.connect(self.SortProgram)

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
        self.LoadStudent()
        QMessageBox.information(self, "Success", "Student added successfully.")
        self.ClearStudentInputs()
    
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
            self.ui.StudentTable.removeRow(selected_row)
            
            with open(StudentCSV, "r", newline="") as file:
                rows = list(csv.reader(file))
            with open(StudentCSV, "w", newline="") as file:
                writer = csv.writer(file)
                for i, row in enumerate(rows):
                    if i != selected_row + 1:
                        writer.writerow(row)
            
            QMessageBox.information(self, "Success", "Student deleted successfully!")
            self.LoadStudent()
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
            self.LoadStudent()
            return
        if not search_text.isalnum():
            QMessageBox.warning(self, "Input Error", "Invalid Student ID!")
            return
        if not search_text.isalpha():
            QMessageBox.warning(self, "Input Error", "Invalid Student Name!")
            return
        
        with open(StudentCSV, "r") as file:
            reader = csv.reader(file)
            self.ui.StudentTable.setRowCount(0)
            for row_data in reader:
                if any(search_text in str(data).lower() for data in row_data):
                    row_index = self.ui.StudentTable.rowCount()
                    self.ui.StudentTable.insertRow(row_index)
                    for col_index, data in enumerate(row_data):
                        self.ui.StudentTable.setItem(row_index, col_index, QTableWidgetItem(data))
        QMessageBox.information(self, "Search Results", "Search completed.")

    # Sorting Students
    def SortStudents(self):
        indexcolumn = self.ui.Sortbybox.currentIndex()  

        # If "SELECT" is chosen, it reverts back to its original order(The order when it was added)
        if indexcolumn == 0:  
            self.LoadStudent()  
            return

        StudentSort = {
            1: 0,  # ID#
            2: 1,  # First Name
            3: 2,  # Last Name
            4: 3,  # Year Level
            5: 4,  # Gender
            6: 5   # Program Code
        }

        if indexcolumn not in StudentSort:
            QMessageBox.warning(self, "Sort Error", "Please select a valid sorting option.")
            return

        indexcolumn = StudentSort[indexcolumn]  # Get actual column index

        
        with open(StudentCSV, "r", newline="") as file:
            Ssort = csv.reader(file)
            rows = list(Ssort)

        if len(rows) <= 1:  # IF only header is available
            QMessageBox.warning(self, "Sort Error", "No data available for sorting.")
            return

        header, *inputs = rows  # Separate header from data

       
        inputs.sort(key=lambda row: row[indexcolumn].lower() if len(row) > indexcolumn else "")

        
        self.ui.StudentTable.setRowCount(0)
        for row_data in inputs:
            row_index = self.ui.StudentTable.rowCount()
            self.ui.StudentTable.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                self.ui.StudentTable.setItem(row_index, col_index, QTableWidgetItem(cell_data))
    
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #COLLEGE  
    def AddCollege(self):
        collegecode = self.ui.AddCCodeBox.text().strip()
        collegename = self.ui.CollegeNbox.text().strip()

        # Validating Add College Inputs
        if not collegecode or not collegename:
            QMessageBox.warning(self, "Input Error", "All fields are required!")
            return
        if not all(c.isalpha() for c in collegecode): 
            QMessageBox.warning(self, "Input Error", "Invalid College Code! Only letters are allowed.")
            return
        if not all(c.isalpha() or c.isspace() for c in collegename): 
            QMessageBox.warning(self, "Input Error", "Invalid College Name! Only letters and spaces are allowed.")
            return
        
        
        with open(CollegeCSV, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([collegecode, collegename])

        self.LoadCollege() 
        QMessageBox.information(self, "Success", "College added")
 
        self.ClearCollegeInputs()
        self.combo_boxes()

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
        college_code = None
        selected_row = self.ui.COLLEGETABLE.currentRow()
        if selected_row >= 0:
            college_code = self.ui.COLLEGETABLE.item(selected_row, 0).text()
        
        if college_code is None:
            QMessageBox.warning(self, "Input Error", "Please select a College to delete.")
            return

        # Remove College from Table
        self.ui.COLLEGETABLE.removeRow(selected_row)
    
        # Remove College from CSV
        try:
            with open(CollegeCSV, "r", newline="") as file:
                rows = list(csv.reader(file))
            with open(CollegeCSV, "w", newline="") as file:
                writer = csv.writer(file)
                for i, row in enumerate(rows):
                    if i != selected_row + 1:
                        writer.writerow(row)
        except Exception as e:
            QMessageBox.warning(self, "Error", "An error occurred while deleting the College.")
            return
    
        # Remove Programs that are connected to College
        programs_to_remove = set()
        try:
            with open(ProgramCSV, "r") as file:
                rows = list(csv.reader(file))
            with open(ProgramCSV, "w", newline="") as file:
                writer = csv.writer(file)
                for row in rows:
                    if row[2] != college_code:
                        writer.writerow(row)
                    else:
                        programs_to_remove.add(row[0]) 
        except Exception as e:
            QMessageBox.warning(self, "Error", "An error occurred while deleting the College.", {e})
            return

        # NULL the Program code in STUDENTS CSV
        try:
            with open(StudentCSV, "r") as file:
                rows = list(csv.reader(file))
            with open(StudentCSV, "w", newline="") as file:
                writer = csv.writer(file)
                for row in rows:
                    if row[5] in programs_to_remove:  
                        row[5] = "NULL"  
                    writer.writerow(row) 
        except Exception as e:
            QMessageBox.warning(self, "Error", "An error occurred while deleting the College.", {e})

    
        QMessageBox.information(self, "Success", "College Deleted Successfully")
        
        # Refresh UI
        self.LoadCollege()
        self.LoadProgram()
        self.LoadStudent()
        self.combo_boxes()

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

        # Sorting College
    def SortCollege(self):
        try:
            indexcolumn = self.ui.Sortbox.currentIndex()

            if indexcolumn == 0:  # If "Select" is chosen, reload original order
                self.LoadCollege()  # **Reload table from CSV**
                return

            CollegeSort = {
            1: 0,  # College Code
            2: 1   # College Name
            }

            if indexcolumn not in CollegeSort:
                QMessageBox.warning(self, "Sort Error", "Please select a valid sorting option.")
                return

            indexcolumn = CollegeSort[indexcolumn]  # Get actual column index

             
            with open(CollegeCSV, "r", newline="") as file:
                Csort = csv.reader(file)
                rows = list(Csort)

            if len(rows) <= 1:  # IF only header is available
                QMessageBox.warning(self, "Sort Error", "No data available for sorting.")
                return

            # Since my Table has a header, I separated it and my Table also has bugs so I used this method to sort
            header, *inputs = rows  # I separate header from the inputs in the table

            # Sort data based on the selected column
            inputs.sort(key=lambda row: row[indexcolumn].lower() if len(row) > indexcolumn else "")

            
            self.ui.COLLEGETABLE.setRowCount(0)
            for row_data in inputs:
                row_index = self.ui.COLLEGETABLE.rowCount()
                self.ui.COLLEGETABLE.insertRow(row_index)
                for col_index, cell_data in enumerate(row_data):
                    self.ui.COLLEGETABLE.setItem(row_index, col_index, QTableWidgetItem(cell_data))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while sorting the Colleges: {str(e)}")


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  
    #PROGRAMS
    def AddProgram(self):
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
        with open(ProgramCSV, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([programcode, programname, collegecode])

        QMessageBox.information(self, "Success", "Program added")
        self.LoadProgram()
        self.ClearProgramInputs()
        self.combo_boxes()

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
        self.ui.ccComboBox.clear()
    
    # Delete Program
    def DeleteProgram(self):
        program_code = None
        selected_row = self.ui.COLLEGETABLE_2.currentRow()
        if selected_row >= 0:
            program_code = self.ui.COLLEGETABLE_2.item(selected_row, 0).text()
        
        if program_code is None:  
            QMessageBox.warning(self, "Input Error", "Please select a Program to delete.")
            return

        # Remove Program from Table
        self.ui.COLLEGETABLE_2.removeRow(selected_row)

        # Remove Program from CSV   
        try:
             with open(ProgramCSV, "r", newline="") as file:
                rows = list(csv.reader(file))
                with open(ProgramCSV, "w", newline="") as file:
                    writer = csv.writer(file)
                    for i, row in enumerate(rows):
                        if i != selected_row + 1:
                            writer.writerow(row)
        except Exception as e:
            QMessageBox.warning(self, "Error", "An error occurred while deleting the Program.")
            return

        # Null the Program code in STUDENTS CSV (If you only delete the program)
        try:
            with open(StudentCSV, "r") as file:
                rows = list(csv.reader(file))
            with open(StudentCSV, "w", newline="") as file:
                writer = csv.writer(file)
                for row in rows:
                    if row[5] == program_code:  
                        row[5] = "NULL" 
                    writer.writerow(row)
        except Exception as e:
            QMessageBox.warning(self, "Error", "An error occurred while deleting the Program.")
            return
        QMessageBox.information(self, "Success", "Program Deleted Successfully")

        self.LoadProgram()
        self.LoadStudent()
        self.combo_boxes()
    
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
    def SortProgram(self):
        try:
            indexcolumn = self.ui.Sortbybox_2.currentIndex()

            # If "SELECT" is chosen, it reverts back to its original order(The order when it was added)
            if indexcolumn == 0:  
                self.LoadProgram()  
                return

            ProgramSort = {
                1: 0,  # Program Code
                2: 1,  # Program Name
                3: 2   # College Code
            }

            if indexcolumn not in ProgramSort:
                QMessageBox.warning(self, "Sort Error", "Please select a valid sorting option.")
                return

            indexcolumn = ProgramSort[indexcolumn]  # Get actual column index for sorting

            
            with open(ProgramCSV, "r", newline="") as file:
                Psort = csv.reader(file)
                rows = list(Psort)

            if len(rows) <= 1:  # IF only header is available
                QMessageBox.warning(self, "Sort Error", "No data available for sorting.")
                return

            # UI AND TABLE PROBLEMS... I USED THIS METHOD TO SORT
            header, *inputs = rows  

            # Sort data based on the selected column
            inputs.sort(key=lambda row: row[indexcolumn].lower() if len(row) > indexcolumn else "")

          
            self.ui.COLLEGETABLE_2.setRowCount(0)
            for row_data in inputs:
                row_index = self.ui.COLLEGETABLE_2.rowCount()
                self.ui.COLLEGETABLE_2.insertRow(row_index)
                for col_index, cell_data in enumerate(row_data):
                    self.ui.COLLEGETABLE_2.setItem(row_index, col_index, QTableWidgetItem(cell_data))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while sorting the Programs: {str(e)}")

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StudentSystem()
    window.setWindowTitle("Information System")
    window.show()
    sys.exit(app.exec_())