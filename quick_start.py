#!/usr/bin/env python3
"""
Quick Start Script for Emotion-Based Music Recommendation App
Automatically sets up and runs the application with minimal user input
"""

import os
import sys
import subprocess
import importlib.util
import time

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit', 'opencv-python', 'deepface', 
        'spotipy', 'numpy', 'pillow', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                importlib.import_module('cv2')
            elif package == 'pillow':
                importlib.import_module('PIL')
            else:
                importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - Not installed")
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    print("\n🔧 Installing missing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_webcam():
    """Check if webcam is available"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✅ Webcam detected and accessible")
            cap.release()
            return True
        else:
            print("⚠️  Webcam not accessible (may be in use by another application)")
            return False
    except Exception as e:
        print(f"❌ Error checking webcam: {e}")
        return False

def create_env_file():
    """Create .env file for environment variables"""
    env_content = """# Environment variables for Emotion-Based Music Recommendation App
# Add your Spotify API credentials here (optional)

# Spotify API (Optional)
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here

# App Configuration
DEBUG=False
LOG_LEVEL=INFO
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file for configuration")
    else:
        print("ℹ️  .env file already exists")

def show_spotify_setup():
    """Show instructions for Spotify API setup"""
    print("\n🎧 Spotify API Setup (Optional)")
    print("=" * 40)
    print("To enable Spotify integration:")
    print("1. Go to: https://developer.spotify.com/dashboard")
    print("2. Create a new app")
    print("3. Copy your Client ID and Client Secret")
    print("4. Enter them in the app's sidebar when running")
    print("5. Or add them to the .env file")
    print("\nNote: The app works without Spotify using default playlists")

def run_app():
    """Run the Streamlit application"""
    print("\n🚀 Starting the Emotion-Based Music Recommendation App...")
    print("=" * 60)
    print("The app will open in your default web browser.")
    print("If it doesn't open automatically, go to: http://localhost:8501")
    print("\n📱 App Features:")
    print("• Real-time emotion detection using your webcam")
    print("• Music recommendations based on detected emotions")
    print("• Spotify integration (optional)")
    print("• Beautiful, responsive web interface")
    print("\n⏹️  To stop the app: Press Ctrl+C in this terminal")
    print("=" * 60)
    
    try:
        # Run the Streamlit app
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
    except KeyboardInterrupt:
        print("\n\n👋 App stopped by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error running app: {e}")

def main():
    """Main function to run the quick start process"""
    print("🎵 Emotion-Based Music Recommendation App - Quick Start")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        install_choice = input("Install missing dependencies? (y/n): ").lower().strip()
        
        if install_choice == 'y':
            if not install_dependencies():
                print("❌ Failed to install dependencies. Please install manually:")
                print("pip install -r requirements.txt")
                return
        else:
            print("❌ Cannot continue without required dependencies.")
            return
    
    # Check webcam
    print("\n📷 Checking webcam...")
    webcam_available = check_webcam()
    
    if not webcam_available:
        print("⚠️  Webcam may not be available. The app may not work properly.")
        continue_choice = input("Continue anyway? (y/n): ").lower().strip()
        if continue_choice != 'y':
            return
    
    # Create environment file
    print("\n⚙️  Setting up configuration...")
    create_env_file()
    
    # Show Spotify setup info
    show_spotify_setup()
    
    # Ask user if they want to run the app
    print("\n" + "=" * 60)
    run_choice = input("Ready to start the app? (y/n): ").lower().strip()
    
    if run_choice == 'y':
        run_app()
    else:
        print("\n📚 To run the app later, use:")
        print("streamlit run app.py")
        print("\n🎵 Happy coding!")

if __name__ == "__main__":
    main()
