# PhotoBooth Repository Documentation

## Overview
PhotoBooth is a Python-based photo booth application designed for Raspberry Pi systems. It provides a touchscreen interface for taking photos, applying fun effects, and automatically uploading images to cloud storage services like Google Drive and Google Picasa.

## Repository Information
- **Repository**: vk02169/PhotoBooth
- **Author**: Vinayak Kumar (vinayak.v.kumar@gmail.com)
- **Version**: 1.0
- **License**: None specified
- **URL**: https://github.com/vk02169/PhotoBooth

## Project Structure

### Root Directory
```
PhotoBooth/
├── README.md                    # Basic project readme (minimal content)
├── setup.py                     # Python package setup configuration
├── clean                        # Executable cleanup script
├── auth/                        # Authentication modules
├── conf/                        # Configuration files
├── corecam/                     # Camera core functionality
├── coregui/                     # GUI core components
├── coreimgs/                    # Core image assets
├── scripts/                     # Image processing scripts
├── thrmodel/                    # Threading model components
└── uploaders/                   # Cloud upload functionality
```

### Module Breakdown

#### Authentication (`auth/`)
- `__init__.py` - Package initialization
- `auth.py` - Authentication handling for Google services

#### Configuration (`conf/`)
- `vkphotobooth.conf` - Main configuration file with settings for:
  - Photo capture settings (countdown text, number of pics, resolution)
  - Camera attributes (ISO, sharpness, preview settings)
  - Flash configuration (GPIO pin, timing)
  - Upload settings (Google Drive, Picasa integration)
  - Fun effects configuration

#### Core Camera (`corecam/`)
- `__init__.py` - Package initialization
- `camera.py` - Main camera class (`BoothCamera`) extending PiCamera
- `camflash.py` - Camera flash control using GPIO

#### Core GUI (`coregui/`)
- `__init__.py` - Package initialization
- `main.py` - Main application entry point and GUI logic (364 lines)
- `camconfig.py` - Configuration management
- `util.py` - Utility functions

#### Core Images (`coreimgs/`)
- `TouchHere.png` - Touch interface image
- `press.png` - Press button image
- `press1.png` - Alternative press button image

#### Scripts (`scripts/`)
Image processing effect scripts:
- `cartoon` - Cartoon effect processing
- `chrome` - Chrome effect processing
- `credits` - Credits processing
- `greenscreen` - Green screen effect
- `sketch` - Sketch effect processing
- `toon` - Toon effect processing
- `toonify` - Advanced toonify effects
- `toonizarro` - Toonizarro effect processing

#### Threading Model (`thrmodel/`)
- `__init__.py` - Package initialization
- `backgroundupload.py` - Background processing for uploads

#### Uploaders (`uploaders/`)
- `__init__.py` - Package initialization
- `googledriveuploader.py` - Google Drive upload functionality (139 lines)
- `upload.py` - General upload coordination

## Technical Details

### Dependencies
- **Core**: Python 3.x, tkinter, PIL (Pillow)
- **Camera**: picamera (Raspberry Pi camera module)
- **Cloud Services**: googleapiclient
- **Hardware**: GPIO support for flash control

### Key Features
1. **Touchscreen Interface**: Full-screen tkinter GUI optimized for touch interaction
2. **Camera Integration**: Direct integration with Raspberry Pi camera module
3. **Flash Control**: GPIO-controlled camera flash
4. **Image Effects**: Multiple post-processing effects via external scripts
5. **Cloud Upload**: Automatic upload to Google Drive and Google Picasa
6. **Background Processing**: Threaded upload system to prevent UI blocking
7. **Configurable**: Extensive configuration options via conf file

### Configuration Options
- **Photo Settings**: Number of photos per session, countdown text, archive directory
- **Display**: Screen resolution (800x480 default), UI element positioning
- **Camera**: Resolution (3280x2464 default), ISO (250), sharpness (60), preview alpha
- **Flash**: GPIO pin (11), flash duration (2 seconds)
- **Upload**: Google account integration, folder specifications, service selection
- **Effects**: Configurable fun commands for image processing

### Architecture Patterns
- **Singleton Pattern**: Used for camera, configuration, and uploader classes
- **Background Processing**: Separate threads for upload operations
- **Event-Driven**: GUI responds to touch/click events
- **Modular Design**: Clear separation of concerns across modules

## Code Statistics
- **Total Python Files**: 15
- **Total Lines of Code**: 1,714
- **Main Application**: 364 lines (main.py)
- **Google Drive Uploader**: 139 lines

## Hardware Requirements
- Raspberry Pi with camera module
- Touchscreen display (800x480 recommended)
- GPIO-controlled flash (pin 11)
- Network connectivity for cloud uploads

## Setup and Installation
1. Install on Raspberry Pi with camera module enabled
2. Configure Google API credentials for cloud uploads
3. Adjust configuration file (`conf/vkphotobooth.conf`) for specific setup
4. Run `python coregui/main.py` to start the application

## Cloud Integration
### Google Drive
- Requires OAuth2 authentication
- Uploads to specified folder
- Uses Google Drive API v3
- Supports JPEG image uploads

### Google Picasa (Legacy)
- Legacy support for Google Picasa
- Album-based organization
- Configurable via album ID

## Image Processing Pipeline
1. **Capture**: High-resolution image capture via PiCamera
2. **Archive**: Local storage with timestamp-based naming
3. **Effects**: Optional post-processing via shell scripts
4. **Display**: Thumbnail generation and grid display
5. **Upload**: Background upload to configured cloud services

## User Interface
- **Full-screen Mode**: Optimized for kiosk-style operation
- **Touch Interface**: Single-touch activation
- **Visual Feedback**: Countdown timers, blinking text, image previews
- **Configuration UI**: Optional admin interface for settings
- **Exit Controls**: Configurable exit and configuration buttons

## Error Handling
- Exception logging to photobooth.log
- Graceful degradation for upload failures
- Camera resource management
- Clean shutdown procedures

## Extensibility
- **Modular Upload System**: Easy to add new cloud providers
- **Effect Scripts**: Shell-based image processing allows easy effect addition
- **Configuration-Driven**: Most behavior controllable via config file
- **Plugin Architecture**: Background processor pattern for new features

## Development Notes
- Originally based on WYLUM photobooth application
- Enhanced with additional features and cloud integration
- Designed for embedded/kiosk deployment
- Optimized for Raspberry Pi hardware constraints

## File Permissions
- `clean` script: Executable (cleanup utility)
- `setup.py`: Executable (installation script)
- All Python modules: Standard read permissions

## Logging
- Centralized logging to `log/photobooth.log`
- INFO level logging for operations
- Exception tracking with stack traces
- Startup and shutdown event logging

## Security Considerations
- OAuth2 for Google service authentication
- Local credential storage (pickle files)
- GPIO hardware access requirements
- Network-based cloud uploads

## Future Enhancement Opportunities
1. **Modern UI Framework**: Migrate from tkinter to more modern GUI framework
2. **Additional Cloud Providers**: Support for more cloud storage services
3. **Advanced Effects**: Real-time image processing and filters
4. **Multi-Camera Support**: Support for multiple camera inputs
5. **Web Interface**: Remote configuration and monitoring
6. **Database Integration**: Photo metadata and session tracking
7. **Social Media Integration**: Direct sharing to social platforms
8. **Print Integration**: Local photo printing capabilities

## Maintenance Notes
- Regular cleanup of archived images required
- Google API credential refresh handling
- Hardware component monitoring (camera, flash, display)
- Log file rotation and management
- Configuration backup and versioning