# AN Tech Solutions - Flask Web Application

## Project Overview
**AN Tech Solutions** is a mini full-stack web application built using **Flask** and **SQLite** (or MySQL if upgraded).  
The application demonstrates:

- **Customer Features:**
  - Home page, About page, Services page, Contact page
  - Register & Login functionality
  - Customer dashboard showing services provided, past projects, and company accomplishments
  - Contact form to send messages via email

- **Admin Features:**
  - Admin Register & Login
  - Admin dashboard to manage all customer data
  - Full **CRUD operations** (Create, Read, Update, Delete) on customer records

- **Other Features:**
  - Session-based login
  - Flash messages for success/error notifications
  - Basic navigation menu with Home, About, Services, Contact, Login/Register, Admin

---

## Project Structure
PythonProject/
├── app.py # Main Flask application
├── database.db # SQLite database file
├── requirements.txt # Python dependencies
├── .gitignore
├── README.md
├── templates/ # HTML templates
│ ├── index.html
│ ├── about.html
│ ├── services.html
│ ├── contact.html
│ ├── login.html
│ ├── register.html
│ ├── admin_login.html
│ ├── admin_register.html
│ ├── admin_dashboard.html
│ ├── add_customer.html
│ └── services_dashboard.html
└── static/
└── style.css # Basic CSS styles
