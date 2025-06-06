# Amazon Disputes Management System

A Django-based web application for managing and tracking Amazon seller disputes.

## Project Overview

This application helps Amazon sellers manage and track their disputes with Amazon. It provides a centralized platform to organize dispute cases, track their status, and maintain related documentation.

## Features

- Dispute case management
- Document attachment handling
- Status tracking
- User authentication and authorization
- Responsive web interface

## Technology Stack

- Python 3.x
- Django
- SQLite (Development)
- Docker (for containerization)
- HTML/CSS/JavaScript

## Prerequisites

- Python 3.x
- pip (Python package manager)
- Docker and Docker Compose (optional, for containerized deployment)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Vinuthan093/amazon-disputes.git
cd amazon-disputes
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Docker Deployment

To run the application using Docker:

1. Build the Docker image:
```bash
docker-compose build
```

2. Start the containers:
```bash
docker-compose up
```

## Project Structure

```
amazon_disputes/
├── amazon_disputes/     # Main project directory
├── core/               # Core application
├── templates/          # HTML templates
├── dispute_attachments/ # Uploaded dispute documents
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
├── dockerfile         # Docker configuration
└── docker-compose.yml # Docker Compose configuration
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Security

- All sensitive data is encrypted
- User authentication is required for access
- File uploads are validated and sanitized
- Regular security updates are implemented

## Development Guidelines

1. Follow PEP 8 style guide for Python code
2. Write unit tests for new features
3. Document all new functions and classes
4. Keep the codebase clean and maintainable

## Deployment

### Production Deployment

1. Set up a production database (PostgreSQL recommended)
2. Configure environment variables
3. Set up a web server (Nginx/Apache)
4. Use Gunicorn as the WSGI server
5. Enable HTTPS

### Environment Variables

Create a `.env` file with the following variables:
```
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

## Maintenance

- Regular database backups
- Monitor system logs
- Update dependencies regularly
- Perform security audits

## Future Enhancements

- API integration with Amazon Seller Central
- Automated dispute tracking
- Advanced analytics and reporting
- Mobile application
- Multi-language support 
