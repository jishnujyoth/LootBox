# LootBox - Animation Asset Management Tool

LootBox is a web-based animation library application that allows you to browse, upload, and manage animation assets in various formats (JSON, MP4, GIF).

## Features

- **Animation Library**: Browse animations organized by categories
- **Multi-format Support**: Upload and download animations in JSON, MP4, and GIF formats
- **Preview Functionality**: Preview animations before download
- **Search & Filter**: Find animations by name, category, or tags
- **Admin Interface**: Manage animation assets with an intuitive admin interface
- **Responsive Design**: Works on desktop and mobile devices

## Getting Started

### Prerequisites

- Python 3.7+
- Flask 2.0.1+
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/jishnujyoth/LootBox.git
   cd LootBox
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the application:
   - Local: http://127.0.0.1:8000
   - Network: The application will display a network URL you can use

## Deployment

### Server Requirements

- Python 3.7+
- 1GB+ RAM
- 10GB+ storage (depending on the number and size of animations)
- Linux-based OS recommended (Ubuntu 20.04+)

### Deployment Options

#### Option 1: Traditional Server Deployment

1. Set up a server with Python 3.7+
2. Clone the repository
3. Install dependencies: `pip install -r requirements.txt`
4. Set up a production WSGI server:
   ```
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```
5. Configure Nginx as a reverse proxy (recommended)

#### Option 2: Docker Deployment

1. Build the Docker image:
   ```
   docker build -t lootbox .
   ```

2. Run the container:
   ```
   docker run -p 8000:8000 lootbox
   ```

#### Option 3: Cloud Platform Deployment

The application can be deployed to:
- AWS Elastic Beanstalk
- Google Cloud Run
- Azure App Service
- Heroku

Follow the platform-specific deployment guides.

## Directory Structure

```
LootBox/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── static/                # Static assets
│   ├── animations/        # Animation files
│   │   ├── illustrations/
│   │   ├── loadings/
│   │   └── ...
│   ├── metadata/          # Animation metadata
│   └── ...
└── templates/             # HTML templates
    └── index.html         # Main application template
```

## Environment Variables

The following environment variables can be configured:

- `PORT`: The port to run the application on (default: 8000)
- `DEBUG`: Enable debug mode (default: False)
- `SECRET_KEY`: Secret key for session management

## Upload Animation Component

The upload animation component follows this structure:
1. Initial state: Dropzone for file uploads with "Drop files here, or click to browse" message
2. After file selection: Preview container appears with animation preview and progress bars below
3. File upload process: Progress bars show upload status for each file (JSON, MP4, GIF)
4. Form fields: Animation name, category, and hashtags fields appear below the upload section

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
