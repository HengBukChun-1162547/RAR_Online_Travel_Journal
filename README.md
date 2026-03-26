# COMP639_Project_2_RAR
The RAR Online Travel Journal is an improved version of our free online travel journal platform. It now has new features and a paid subscription model. The original platform was successful and created a strong travel community. But it had problems with making money and keeping users active. This project fixes these problems by adding premium features, better tools, and rewards to help the platform grow and stay strong.

## Demo
[Website on Pythonanywhere](https://comp639prj2rar.pythonanywhere.com/)

## Installation
1. Clone the project from [github](https://github.com/LUMasterOfAppliedComputing2025S1/COMP639_Project_2_RAR.git)
2. Open the project in Visual Studio Code.
3. Create a virtual environment.
   1. Open the `Command Palette` (Ctrl+Shift+P) which is under `View` tab
   2. Search for the `Python: Create Environment command`, and select it.
   3. Using `Venv`, and the command presents a list of `interpreters`, choose one.
   4. Select `requirements.txt`, press `OK`, then it will create a virtual environment and install packages list in the file.
4. Create a database.
   1. Open MySQL Workbench and login.
   2. Create a new schema name.
   3. Use the [Database Creation Script](create_table.sql) to create table.
        * File -> Open SQL Script -> Choose `create_table.sql` -> execute the file. 
   4. Use the [Database Population Script](populate.sql) to populate data.
        * File -> Open SQL Script -> Choose `populate.sql` -> execute the file. 
5. Add `connect.py` which is in the `app` folder with the connection details for local database server.
   1. dbuser = "`your local user name`"
   2. dbpass = "`your local user password`"
   3. dbhost = "localhost" 
   4. dbport = "3306"
   5. dbname = "`your database name`"
6. Run the application.  
   ```
   python run.py
   ```
## Account/Password
For testing purposes, you can use the following accounts:

| Username | Password | Role |
|----------|----------|------|
| Traveller1 | 1qaz@WSX | Traveller |
| Traveller2 | 1qaz@WSX | Traveller |
| Traveller3 | 1qaz@WSX | Traveller |
| Traveller4 | 1qaz@WSX | Traveller |
| Traveller5 | 1qaz@WSX | Traveller |
| Traveller6 | 1qaz@WSX | Traveller |
| Traveller7 | 1qaz@WSX | Traveller |
| Traveller8 | 1qaz@WSX | Traveller |
| Traveller9 | 1qaz@WSX | Traveller |
| Traveller10 | 1qaz@WSX | Traveller |
| Traveller11 | 1qaz@WSX | Traveller(Premium) |
| Traveller12 | 1qaz@WSX | Traveller(Premium) |
| Traveller13 | 1qaz@WSX | Traveller(Premium) |
| Traveller14 | 1qaz@WSX | Traveller(Premium) |
| Traveller15 | 1qaz@WSX | Traveller(Premium) |
| Traveller16 | 1qaz@WSX | Traveller(Trial) |
| Traveller17 | 1qaz@WSX | Traveller(Trial) |
| Traveller18 | 1qaz@WSX | Traveller(Trial) |
| Traveller19 | 1qaz@WSX | Traveller(Trial) |
| Traveller20 | 1qaz@WSX | Traveller(Trial) |
| Admin1 | 1qaz@WSX | Admin |
| Admin2 | 1qaz@WSX | Admin |
| Admin3 | 1qaz@WSX | Admin |
| Admin5 | 1qaz@WSX | Admin |
| Editor1 | 1qaz@WSX | Editor |
| Editor2 | 1qaz@WSX | Editor |
| Editor3 | 1qaz@WSX | Editor |
| Editor4 | 1qaz@WSX | Editor |
| Editor5 | 1qaz@WSX | Editor |
| SupportTech1 | 1qaz@WSX | Support Tech |
| SupportTech2 | 1qaz@WSX | Support Tech |
| SupportTech3 | 1qaz@WSX | Support Tech |
| SupportTech4 | 1qaz@WSX | Support Tech |
| SupportTech5 | 1qaz@WSX | Support Tech |



### Image Reference

> #### Traveller's Profile Image: 
(n.d.). Thispersondoesnotexist.com. https://thispersondoesnotexist.com