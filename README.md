# Installation
### 1. Install python
> https://realpython.com/installing-python/
### 2. Clone this repo into your local machine 
> git clone https://github.com/tabbott207/CircleEvents
<<<<<<< HEAD
### 3. CD into CircleEvents and set up VirtualEnv
> pip3 install virtualenv
> 
> python3 -m venv env
> 
> on MacOS/Linux: source env/bin/activate
> 
> on Windows: .\env\Scripts\activate

### 4. Install django
> pip3 install django
### 5. Install required dependencies
> pip3 install -r requirements.txt
### 6. Final Step
=======
### 3. Install VirtualEnv
>pip install virtualenv
>
>python -m venv env
>
>On macOS and Linux:
>source env/bin/activate
>
>On Windows:
>.\env\Scripts\activate
>
### 3. Install django
> pip install django
### 4. Install required dependencies
> pip install -r requirements.txt
### 5. Final Step
>>>>>>> 71bb607a (update readme)
> go to the directory where manage.py is located and run the following command
>
>python manage.py runserver
>>if you get a google api error, run this command and try again: 
>
>>python -m pip install --upgrade google-api-python-client

