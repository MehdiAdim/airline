from wtforms import Form, StringField, TextAreaField, PasswordField, IntegerField, DecimalField,SelectField, validators


# Register Form Class
class RegisterForm(Form):
    surname =  StringField('Surname', [validators.Length(min=1, max=50)])
    firstname = StringField('First Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    adresse = StringField('Adresse',[validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')



class EmployeeForm(Form):
    surname =  StringField('Surname', [validators.Length(min=1, max=45)])
    firstname = StringField('First Name', [validators.Length(min=1, max=45)])
    address = StringField('Adresse',[validators.Length(min=6, max=500)])
    salary = DecimalField('Salary',[validators.DataRequired()])
    flight_hours = DecimalField('Flight hours',[validators.DataRequired()])
    social_security_number = IntegerField('Social Security Number',[validators.DataRequired()])
    role = SelectField('Role', [validators.DataRequired()],coerce=int)

