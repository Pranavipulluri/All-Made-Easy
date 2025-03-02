# Community Hub Web Application

A feature-rich web application built with Flask that serves as a community platform with multiple integrated services.

## Description

This Community Hub is a comprehensive web application that provides users with various services including content sharing, bike rentals, task management, job postings, messaging, news updates, and more. The platform is designed to foster community engagement while offering practical utilities for users.

## Features

### User Authentication
- User registration and login
- Profile management with customizable profile pictures
- Secure session management

### Content Sharing
- Upload and share content with images
- Browse community content
- Personal content management

### Bike Sharing Marketplace
- List bikes for rental
- Detailed bike information including condition and hourly rates
- Rental system with availability tracking
- Edit and manage your listed bikes

### Task Management
- Create, edit, and delete tasks
- Set due dates and categories
- Filter tasks by category
- Track task status (Incomplete, Complete, Missed)

### Job Board
- Post job opportunities
- Browse available jobs
- Detailed job listings with requirements and contact information

### Messaging System
- Direct messaging between users
- Message read status tracking
- Chat history

### News Integration
- Technology news feed via News API
- Latest articles display

### Learning Center
- Educational resources
- Community learning materials

### Community Features
- User discovery
- Community engagement tools

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML, CSS, JavaScript
- **External APIs**: News API for technology news
- **File Handling**: Werkzeug for secure file uploads

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/community-hub.git
   cd community-hub
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your News API key:
   - Sign up at [News API](https://newsapi.org/) to get an API key
   - Replace the `API_KEY` in app.py with your key

5. Initialize the database:
   ```
   python
   >>> from app import app, db
   >>> with app.app_context():
   ...     db.create_all()
   >>> exit()
   ```

6. Run the application:
   ```
   python app.py
   ```

7. Access the application in your web browser at `http://127.0.0.1:5000`

## Project Structure

```
community-hub/
├── app.py                  # Main application file
├── static/                 # Static files (CSS, JS, images)
│   ├── css/                # CSS stylesheets
│   ├── js/                 # JavaScript files
│   └── uploads/            # User uploaded content
├── templates/              # HTML templates
│   ├── layout.html         # Base template
│   ├── home.html           # Homepage
│   ├── login.html          # Login page
│   ├── signup.html         # Registration page
│   ├── profile.html        # User profile
│   ├── content_sharing.html# Content sharing page
│   ├── bike_sharing.html   # Bike sharing marketplace
│   ├── todo.html           # Task management
│   ├── chat.html           # Messaging interface
│   ├── job_board.html      # Job listings
│   ├── tech_news.html      # Technology news
│   └── ...                 # Other templates
└── requirements.txt        # Python dependencies
```

## Database Models

- **User**: User account information
- **Content**: Shared content with images
- **Bike**: Bike rental listings
- **Task**: User tasks with due dates
- **Message**: User-to-user messages
- **Job**: Job listings

## Security Notes

- In a production environment, implement proper password hashing
- Configure a more secure database system like PostgreSQL
- Set a strong, secret `SECRET_KEY`
- Implement CSRF protection
- Consider adding rate limiting for API endpoints

## Future Enhancements

- Email verification for user registration
- Social media integration
- Mobile app version
- Advanced search functionality
- Rating and review system for bikes and content
- Payment integration for bike rentals
- Community events calendar
- User notifications system

## License

[MIT License](LICENSE)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## Contact

For questions or support, please contact [pulluripranavi](mailto:pulluripranavi@gmail.com)
