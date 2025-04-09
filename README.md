# Lottie Library

A modern, feature-rich web application for managing and displaying Lottie animations with multi-format support.

![Lottie Library Screenshot](https://via.placeholder.com/800x450.png?text=Lottie+Library)

## Features

### Multi-format Support
- **JSON**: Native Lottie animation format
- **MP4**: Video export for non-Lottie environments
- **GIF**: Animated GIF export for universal compatibility
- **SVG**: Frame-by-frame SVG export for static use cases

### User Interface
- **Expandable Thumbnail Controls**: Size controls in header that expand on hover
- **Interactive 3D Cube**: Engaging homepage animation
- **Animated Search Bar**: Gradient underglow effect
- **Category Filtering**: Easy navigation between animation types
- **Responsive Design**: Works on various screen sizes

### Admin Features
- **Admin Mode**: Toggle for administrative functions
- **Upload Interface**: Add missing media files for any animation
- **Delete Functionality**: Remove animations with confirmation
- **Visual Feedback**: Status indicators for all operations

### Technical Highlights
- **Robust Error Handling**: Automatic retry with exponential backoff
- **Modal Interactions**: Scroll locking and backdrop blur effects
- **Animation Optimization**: Efficient loading and rendering
- **Clean Code Structure**: Maintainable and extensible design

## Setup Instructions

### Prerequisites
- Python 3.7+
- Flask

### Installation

1. Clone the repository:
```bash
git clone https://github.com/jishnujyoth/LootBox.git
cd LootBox
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Access the application:
- Local access: http://127.0.0.1:8080
- Network access: http://[your-ip-address]:8080 (shown in terminal output)

## Usage Guide

### Browsing Animations
- Use the category buttons to filter animations
- Adjust thumbnail size using the controls in the header
- Search for specific animations using the search bar

### Downloading Animations
- Click on an animation to view details
- Use the format buttons (JSON, MP4, GIF, SVG) to download

### Admin Functions
1. Click the "Admin" button in the header to enable admin mode
2. Upload missing media:
   - Missing formats will show a blue "+" icon
   - Click to upload the corresponding file
3. Delete animations:
   - Hover over an animation to reveal the delete button
   - Confirm deletion in the modal dialog

## Recent UI Enhancements

- **Redesigned Delete Dialog**: Modern interface with trash icon and improved typography
- **Hover-Only Delete Buttons**: Cleaner interface with contextual controls
- **Improved Upload Icons**: Blue "+" symbol for better visual consistency
- **Fixed Category Buttons**: Ensured proper clickability with z-index adjustments
- **Scroll Locking**: Prevented background scrolling during modal interactions
- **Enhanced Error Handling**: More informative messages with retry options

## License

[MIT License](LICENSE)

## Acknowledgments

- [Lottie by Airbnb](https://airbnb.design/lottie/) for the animation format
- [Flask](https://flask.palletsprojects.com/) for the web framework
