from flask import Flask, render_template, send_file, jsonify, request
import os
import shutil
import json
import uuid
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request, send_file, redirect

app = Flask(__name__)

# Path to store metadata
META_DIR = os.path.join(app.static_folder, 'metadata')
os.makedirs(META_DIR, exist_ok=True)

# Define animation categories
CATEGORIES = {
    'illustrations': 'Illustrations',
    'loadings': 'Loadings',
    'logo-animations': 'Logo Animations',
    'backgrounds': 'Backgrounds',
    'design-elements': 'Design Elements',
    'icons': 'Icons'
}

# Ensure media directories exist
for category in CATEGORIES:
    for media_type in ['mp4', 'gif']:
        media_dir = os.path.join(app.static_folder, 'animations', category, media_type)
        os.makedirs(media_dir, exist_ok=True)

@app.route('/', defaults={'category': None})
@app.route('/<category>')
def index(category):
    # Always return to homepage state
    return render_template('index.html',
                          categories=CATEGORIES,
                          current_category='',
                          search_query='',
                          current_page=1,
                          total_pages=1,
                          total_animations=0,
                          animations=[])

@app.route('/api/animations')
def get_animations():
    category = request.args.get('category', '')
    page = int(request.args.get('page', 1))
    per_page = 12
    search_query = request.args.get('q', '').lower()
    
    animations = []
    
    # If category is specified, search only in that category
    categories_to_search = [category] if category in CATEGORIES else CATEGORIES.keys()
    
    for current_category in categories_to_search:
        # Look in the category metadata directory first (more reliable)
        meta_dir = os.path.join(META_DIR, current_category)
        lottie_dir = os.path.join(app.static_folder, 'animations', current_category, 'lottie')
        animations_dir = os.path.join(app.static_folder, 'animations', current_category)
        os.makedirs(animations_dir, exist_ok=True)
        
        # First check for metadata files in the category's metadata directory
        if os.path.exists(meta_dir):
            for meta_file in os.listdir(meta_dir):
                if meta_file.endswith('.json'):
                    meta_path = os.path.join(meta_dir, meta_file)
                    name = os.path.splitext(meta_file)[0]
                    
                    try:
                        with open(meta_path, 'r') as f:
                            meta = json.load(f)
                            path = meta.get('path')
                            hashtags = meta.get('hashtags', [])
                            formats = meta.get('formats', [])
                            
                            # If no path in metadata, try to construct it
                            if not path:
                                path = f'/static/animations/{current_category}/lottie/{name}.json'
                            
                            # Check if animation matches search query
                            search_terms = name.lower() + ' ' + ' '.join(hashtags).lower()
                            if not search_query or search_query in search_terms:
                                animations.append({
                                    'name': name,
                                    'path': path,
                                    'category': current_category,
                                    'hashtags': hashtags,
                                    'formats': formats
                                })
                    except Exception as e:
                        app.logger.error(f"Error loading metadata file {meta_path}: {str(e)}")
                        continue
        
        # Next look in lottie subfolder (for files that might not have metadata)
        if os.path.exists(lottie_dir):
            for file in os.listdir(lottie_dir):
                if file.endswith('.json'):
                    name = os.path.splitext(file)[0]
                    
                    # Skip if we already added this animation from metadata
                    if any(a['name'] == name and a['category'] == current_category for a in animations):
                        continue
                    
                    # Try to find metadata in other locations
                    meta_file = os.path.join(META_DIR, current_category, f'{name}.json')
                    if not os.path.exists(meta_file):
                        meta_file = os.path.join(META_DIR, f'{name}.json')
                    
                    hashtags = []
                    
                    if os.path.exists(meta_file):
                        with open(meta_file, 'r') as f:
                            meta = json.load(f)
                            hashtags = meta.get('hashtags', [])
                    
                    # Check if animation matches search query
                    search_terms = name.lower() + ' ' + ' '.join(hashtags).lower()
                    if not search_query or search_query in search_terms:
                        animations.append({
                            'name': name,
                            'path': f'/static/animations/{current_category}/lottie/{file}',
                            'category': current_category,
                            'hashtags': hashtags
                        })
        
        # Also check for files in the root directory (for backwards compatibility)
        if os.path.exists(animations_dir):
            for file in os.listdir(animations_dir):
                if file.endswith('.json') and file != 'metadata.json':
                    name = os.path.splitext(file)[0]
                    # Skip if we already added this animation from the lottie folder or metadata
                    if any(a['name'] == name and a['category'] == current_category for a in animations):
                        continue
                        
                    # Try to find metadata
                    meta_file = os.path.join(META_DIR, current_category, f'{name}.json')
                    if not os.path.exists(meta_file):
                        meta_file = os.path.join(META_DIR, f'{name}.json')
                        
                    hashtags = []
                    
                    if os.path.exists(meta_file):
                        with open(meta_file, 'r') as f:
                            try:
                                meta = json.load(f)
                                hashtags = meta.get('hashtags', [])
                            except:
                                # If metadata is invalid, just continue with empty hashtags
                                pass
                    
                    # Check if animation matches search query
                    search_terms = name.lower() + ' ' + ' '.join(hashtags).lower()
                    if not search_query or search_query in search_terms:
                        animations.append({
                            'name': name,
                            'path': f'/static/animations/{current_category}/{file}',
                            'category': current_category,
                            'hashtags': hashtags
                        })
    
    # Sort animations by name
    animations.sort(key=lambda x: x['name'])
    
    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_animations = animations[start:end]
    
    return jsonify({
        'animations': paginated_animations,
        'total': len(animations),
        'has_more': end < len(animations)
    })



@app.route('/api/hashtags/<name>', methods=['POST'])
def update_hashtags(name):
    data = request.get_json()
    hashtags = data.get('hashtags', [])
    
    meta_file = os.path.join(META_DIR, f'{name}.json')
    with open(meta_file, 'w') as f:
        json.dump({'hashtags': hashtags}, f)
    
    return jsonify({'status': 'success'})

@app.route('/api/export/<category>/<name>')
def export_animation(category, name):
    format_type = request.args.get('format', 'json')
    
    # Updated path for JSON files now in the lottie subfolder
    file_path = os.path.join(app.static_folder, 'animations', category, 'lottie', f'{name}.json')
    # Removed debug print
    
    if format_type == 'json' and not os.path.exists(file_path):
        # Also try looking in the root directory for backward compatibility
        old_path = os.path.join(app.static_folder, 'animations', category, f'{name}.json')
        if os.path.exists(old_path):
            file_path = old_path
        else:
            return jsonify({'error': f'Animation file not found: {name}'}), 404
    
    if format_type == 'json':
        try:
            # Read the file content directly
            with open(file_path, 'r') as f:
                file_content = f.read()
            
            # Removed debug print
            
            # Return the raw file content with proper headers
            response = app.response_class(
                response=file_content,
                status=200,
                mimetype='application/json'
            )
            response.headers['Content-Disposition'] = f'attachment; filename={name}.json'
            response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    elif format_type == 'mp4':
        # Look for mp4 file in the category/mp4 subdirectory
        mp4_dir = os.path.join(app.static_folder, 'animations', category, 'mp4')
        mp4_file_path = os.path.join(mp4_dir, f'{name}.mp4')
        
        if os.path.exists(mp4_file_path):
            try:
                # Return the mp4 file as an attachment
                # Use a more compatible approach
                return send_file(
                    mp4_file_path,
                    mimetype='video/mp4',
                    as_attachment=True
                )
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': f'MP4 version not available for {name}'}), 404
            
    elif format_type == 'gif':
        # Look for gif file in the category/gif subdirectory
        gif_dir = os.path.join(app.static_folder, 'animations', category, 'gif')
        gif_file_path = os.path.join(gif_dir, f'{name}.gif')
        
        if os.path.exists(gif_file_path):
            try:
                # Return the gif file as an attachment
                # Use a more compatible approach
                return send_file(
                    gif_file_path,
                    mimetype='image/gif',
                    as_attachment=True
                )
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        else:
            return jsonify({'error': f'GIF version not available for {name}'}), 404
    
    return jsonify({'error': 'Invalid format'}), 400

@app.route('/api/upload-media', methods=['POST'])
def upload_media():
    """Handler for uploading MP4 and GIF files for existing animations"""
    # Check if user is admin
    # In a real app, you'd check session or token-based auth
    # Here we're using a simplified approach
    
    # Get form data
    file = request.files.get('file')
    name = request.form.get('name')
    category = request.form.get('category')
    format_type = request.form.get('format')  # 'mp4' or 'gif'
    
    # Validate input
    if not file or not name or not category or not format_type:
        return jsonify({
            'success': False,
            'error': 'Missing required parameters'
        }), 400
        
    if format_type not in ['mp4', 'gif']:
        return jsonify({
            'success': False,
            'error': 'Invalid format type'
        }), 400
    
    # Check if original animation exists
    lottie_path = os.path.join(app.static_folder, 'animations', category, 'lottie', f'{name}.json')
    old_path = os.path.join(app.static_folder, 'animations', category, f'{name}.json')
    
    if not os.path.exists(lottie_path) and not os.path.exists(old_path):
        return jsonify({
            'success': False,
            'error': 'Original animation not found'
        }), 404
    
    # Create directory if it doesn't exist
    media_dir = os.path.join(app.static_folder, 'animations', category, format_type)
    os.makedirs(media_dir, exist_ok=True)
    
    # Generate safe filename and save file
    filename = f"{name}.{format_type}"
    file_path = os.path.join(media_dir, filename)
    
    try:
        file.save(file_path)
        
        # Return success response with the URL to the file
        file_url = f"/static/animations/{category}/{format_type}/{filename}"
        
        return jsonify({
            'success': True,
            'url': file_url,
            'name': filename
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload-temp', methods=['POST'])
def upload_temp():
    """Temporary endpoint to handle individual file uploads with progress tracking"""
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # If user does not select file
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400
    
    # Validate file format
    filename = secure_filename(file.filename)
    _, ext = os.path.splitext(filename)
    allowed_extensions = ['.json', '.gif', '.mp4', '.svg']
    
    if ext.lower() not in allowed_extensions:
        return jsonify({'success': False, 'error': f'File type {ext} not allowed. Allowed types: {", ".join(allowed_extensions)}'}), 400
    
    # Create temp directory if it doesn't exist
    temp_dir = os.path.join(app.static_folder, 'temp_uploads')
    os.makedirs(temp_dir, exist_ok=True)
    
    # Generate a unique filename to avoid conflicts
    temp_id = str(uuid.uuid4())
    temp_filename = f"{temp_id}{ext}"
    temp_path = os.path.join(temp_dir, temp_filename)
    
    try:
        # Save the file to temp directory
        file.save(temp_path)
        
        return jsonify({
            'success': True,
            'temp_id': temp_id,
            'original_name': filename,
            'temp_path': temp_path,
            'format': ext[1:] # Remove the dot from extension
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/save-animation', methods=['POST'])
def save_animation():
    """Save animation metadata and move files to their final locations"""
    # Get form data
    name = request.form.get('name')
    category = request.form.get('category')
    tags_json = request.form.get('tags')
    file_count = request.form.get('fileCount')
    
    # Validate input
    if not name or not category or not file_count:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    # Parse tags
    try:
        tags = json.loads(tags_json) if tags_json else []
    except json.JSONDecodeError:
        tags = []
    
    # Check if category exists
    if category not in CATEGORIES:
        return jsonify({'success': False, 'error': 'Invalid category'}), 400
    
    try:
        file_count = int(file_count)
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid file count'}), 400
    
    # Used to track created files
    created_files = {}
    json_path = None
    
    # Process each file
    for i in range(file_count):
        file_format = request.form.get(f'fileFormat_{i}')
        file_id = request.form.get(f'fileId_{i}')
        
        if not file_format or not file_id:
            continue
        
        # Find the temp file
        temp_dir = os.path.join(app.static_folder, 'temp_uploads')
        temp_path = os.path.join(temp_dir, f"{file_id}.{file_format}")
        
        if not os.path.exists(temp_path):
            # File may have been uploaded directly via the regular upload endpoint
            continue
        
        # Determine target directory based on format
        if file_format.lower() == 'json':
            target_dir = os.path.join(app.static_folder, 'animations', category, 'lottie')
        elif file_format.lower() == 'mp4':
            target_dir = os.path.join(app.static_folder, 'animations', category, 'mp4')
        elif file_format.lower() == 'gif':
            target_dir = os.path.join(app.static_folder, 'animations', category, 'gif')
        else:
            # Skip unsupported formats
            continue
        
        # Create directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # Generate target filename
        target_filename = f"{secure_filename(name)}.{file_format.lower()}"
        target_path = os.path.join(target_dir, target_filename)
        
        # Copy the file to the target location
        try:
            shutil.copy(temp_path, target_path)
            created_files[file_format] = target_path
            
            # Save the JSON path for metadata
            if file_format.lower() == 'json':
                json_path = f"/static/animations/{category}/lottie/{target_filename}"
            
            # Clean up temp file
            try:
                os.remove(temp_path)
            except:
                pass  # Ignore errors in cleanup
        except Exception as e:
            return jsonify({'success': False, 'error': f'Error saving {file_format} file: {str(e)}'}), 500
    
    # Handle case where files were uploaded directly via existing endpoint
    if not json_path and 'json' not in created_files:
        # Try to find the JSON file in the lottie directory
        lottie_dir = os.path.join(app.static_folder, 'animations', category, 'lottie')
        if os.path.exists(os.path.join(lottie_dir, f"{secure_filename(name)}.json")):
            json_path = f"/static/animations/{category}/lottie/{secure_filename(name)}.json"
    
    # Ensure we have a JSON file
    if not json_path:
        return jsonify({'success': False, 'error': 'No JSON animation file was uploaded'}), 400
    
    # Create metadata
    metadata = {
        'name': name,
        'path': json_path,
        'category': category,
        'hashtags': tags,
        'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'formats': list(created_files.keys()) + ['json']
    }
    
    # Save metadata
    metadata_dir = os.path.join(META_DIR, category)
    os.makedirs(metadata_dir, exist_ok=True)
    metadata_path = os.path.join(metadata_dir, f"{secure_filename(name)}.json")
    
    try:
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error saving metadata: {str(e)}'}), 500


@app.route('/api/upload', methods=['POST'])
def upload_animation():
    """Legacy endpoint for backward compatibility"""
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'}), 400
    
    file = request.files['file']
    name = request.form.get('name')
    category = request.form.get('category')
    tags_json = request.form.get('tags', '[]')
    
    # Check for filename from the redesigned upload component
    filename = request.form.get('filename')
    
    # If we have a filename but no name/category, this is likely from the new upload UI
    # Just save to temp and return a success
    if filename and not (name and category):
        return upload_temp()
    
    # Validate inputs
    if not file or not name or not category:
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
    
    # Parse tags
    try:
        tags = json.loads(tags_json)
    except json.JSONDecodeError:
        tags = []
    
    # Determine file extension and validate format
    filename = secure_filename(file.filename)
    _, ext = os.path.splitext(filename)
    allowed_extensions = ['.json', '.gif', '.mp4', '.svg']
    
    if ext.lower() not in allowed_extensions:
        return jsonify({'success': False, 'error': f'File type {ext} not allowed. Allowed types: {", ".join(allowed_extensions)}'}), 400
    
    # Determine the appropriate directory based on file type
    if ext.lower() == '.json':
        subdir = 'lottie'
    elif ext.lower() == '.mp4':
        subdir = 'mp4'
    elif ext.lower() == '.gif':
        subdir = 'gif'
    else:
        subdir = ''
    
    # Create a unique filename
    unique_id = str(uuid.uuid4())[:8]
    new_filename = f"{secure_filename(name)}{ext}"
    
    # Ensure category directory exists
    if subdir:
        category_dir = os.path.join(app.static_folder, 'animations', category, subdir)
    else:
        category_dir = os.path.join(app.static_folder, 'animations', category)
    
    os.makedirs(category_dir, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(category_dir, new_filename)
    file.save(file_path)
    
    # Create animation metadata
    if ext.lower() == '.json':
        path = f"/static/animations/{category}/lottie/{new_filename}"
    else:
        path = f"/static/animations/{category}/{subdir}/{new_filename}"
    
    animation_data = {
        'name': name,
        'path': path,
        'category': category,
        'hashtags': tags,
        'added_date': datetime.now().isoformat(),
        'id': unique_id
    }
    
    # Save metadata if it's a JSON file
    if ext.lower() == '.json':
        metadata_dir = os.path.join(META_DIR, category)
        os.makedirs(metadata_dir, exist_ok=True)
        meta_file = os.path.join(metadata_dir, f'{secure_filename(name)}.json')
        
        metadata = {
            'name': name,
            'path': path,
            'category': category,
            'hashtags': tags,
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    return jsonify({'success': True, 'animation': animation_data, 'id': unique_id})


@app.route('/api/delete-animation', methods=['POST'])
def delete_animation():
    """Delete an animation and all its associated files (JSON, MP4, GIF)"""
    data = request.json
    
    if not data or 'name' not in data or 'category' not in data:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
    name = data['name']
    category = data['category']
    
    # Make sure the name and category are valid
    if not name or not category or category not in CATEGORIES:
        return jsonify({'success': False, 'error': 'Invalid name or category'}), 400
    
    # We need to check both the safe filename and the original filename
    # since the files could be stored with spaces in their names
    safe_name = secure_filename(name)
    
    # Define paths with sanitized filename
    json_path_safe = os.path.join(app.static_folder, 'animations', category, 'lottie', f'{safe_name}.json')
    mp4_path_safe = os.path.join(app.static_folder, 'animations', category, 'mp4', f'{safe_name}.mp4')
    gif_path_safe = os.path.join(app.static_folder, 'animations', category, 'gif', f'{safe_name}.gif')
    old_json_path_safe = os.path.join(app.static_folder, 'animations', category, f'{safe_name}.json')
    
    # Define paths with original filename (which may contain spaces)
    json_path = os.path.join(app.static_folder, 'animations', category, 'lottie', f'{name}.json')
    mp4_path = os.path.join(app.static_folder, 'animations', category, 'mp4', f'{name}.mp4')
    gif_path = os.path.join(app.static_folder, 'animations', category, 'gif', f'{name}.gif')
    old_json_path = os.path.join(app.static_folder, 'animations', category, f'{name}.json')
    
    # Metadata files (try both safe and original filenames)
    metadata_path_safe = os.path.join(META_DIR, category, f'{safe_name}.json')
    old_metadata_path_safe = os.path.join(META_DIR, f'{safe_name}.json')
    metadata_path = os.path.join(META_DIR, category, f'{name}.json')
    old_metadata_path = os.path.join(META_DIR, f'{name}.json')
    
    # Track which files were deleted
    deleted_files = []
    
    # Try to delete each file if it exists (try both safe and original paths)
    all_paths = [
        json_path, mp4_path, gif_path, old_json_path, metadata_path, old_metadata_path,
        json_path_safe, mp4_path_safe, gif_path_safe, old_json_path_safe, metadata_path_safe, old_metadata_path_safe
    ]
    
    for file_path in all_paths:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                deleted_files.append(file_path)
                app.logger.info(f"Successfully deleted: {file_path}")
            except Exception as e:
                app.logger.error(f"Error deleting {file_path}: {str(e)}")
    
    # Check if we deleted at least one file
    if not deleted_files:
        return jsonify({
            'success': False, 
            'error': f'No files found for animation {name} in category {category}'
        }), 404
    
    return jsonify({
        'success': True, 
        'message': f'Deleted animation {name} from category {category}',
        'deleted_files': deleted_files
    })

def find_free_port(start_port=5000, max_port=5050):
    """Find a free port to run the Flask app"""
    import socket
    from contextlib import closing
    
    for port in range(start_port, max_port):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start_port  # Fallback to default

if __name__ == '__main__':
    # Run the app on 0.0.0.0 to make it accessible from other devices
    # Find an available port
    port = find_free_port(8000, 9000)
    print("\n🚀 Lottie Library running at:")
    print(f"💻 Local:   http://127.0.0.1:{port}")
    
    # Get all available IP addresses for better network access
    import socket
    
    # Try multiple methods to get network IPs
    try:
        # Method 1: Basic hostname lookup
        hostname = socket.gethostname()
        basic_ip = socket.gethostbyname(hostname)
        print(f"🌐 Network: http://{basic_ip}:{port}")
        
        # Method 2: Try to get a more reliable IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn't have to be reachable
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
            if ip != basic_ip:
                print(f"🌐 Alternative Network: http://{ip}:{port}")
        except Exception:
            pass
        finally:
            s.close()
            
        print("\n📱 You can access the Lottie Library from other devices using the Network URL above.")
        print("   For internet access, consider using a service like ngrok or deploying to a cloud platform.")
    except Exception as e:
        print(f"🌐 Network: Unable to determine network IP: {str(e)}")
    
    print("\n📌 Features available:")
    print("   - Multi-format downloads (JSON, MP4, GIF, SVG)")
    print("   - Admin mode for uploading missing media files")
    print("   - Expandable thumbnail size controls")
    print("   - Redesigned delete confirmation dialog")
    print("   - Improved error handling with retry logic")
    
    print("\nPress CTRL+C to quit\n")
    
    # Run on all interfaces (0.0.0.0) with public port
    app.run(host='0.0.0.0', port=port, debug=False)
