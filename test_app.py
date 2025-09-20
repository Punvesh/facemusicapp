"""
Test Script for Emotion-Based Music Recommendation App
Tests all modules to ensure they're working correctly
"""

import sys
import traceback
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    modules_to_test = [
        ('cv2', 'OpenCV'),
        ('numpy', 'NumPy'),
        ('streamlit', 'Streamlit'),
        ('PIL', 'Pillow'),
        ('requests', 'Requests')
    ]
    
    all_imported = True
    
    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {display_name} imported successfully")
        except ImportError as e:
            print(f"❌ {display_name} import failed: {e}")
            all_imported = False
    
    # Test our custom modules
    custom_modules = [
        ('camera', 'Camera Module'),
        ('emotion_detection', 'Emotion Detection Module'),
        ('recommendation', 'Music Recommendation Module')
    ]
    
    for module_name, display_name in custom_modules:
        try:
            __import__(module_name)
            print(f"✅ {display_name} imported successfully")
        except ImportError as e:
            print(f"❌ {display_name} import failed: {e}")
            all_imported = False
    
    return all_imported

def test_camera_module():
    """Test camera module functionality"""
    print("\n📷 Testing camera module...")
    
    try:
        from camera import CameraHandler
        
        # Create camera handler
        camera = CameraHandler()
        print("✅ CameraHandler created successfully")
        
        # Test camera info
        width, height = camera.get_camera_info()
        print(f"✅ Camera info: {width}x{height}")
        
        # Test camera status
        status = camera.is_camera_active()
        print(f"✅ Camera status check: {status}")
        
        # Cleanup
        camera.stop_camera()
        print("✅ Camera cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Camera module test failed: {e}")
        traceback.print_exc()
        return False

def test_emotion_detection_module():
    """Test emotion detection module functionality"""
    print("\n😊 Testing emotion detection module...")
    
    try:
        from emotion_detection import EmotionDetector
        
        # Create emotion detector
        detector = EmotionDetector()
        print("✅ EmotionDetector created successfully")
        
        # Test emotion info
        emotion_info = detector.get_emotion_info('happy')
        print(f"✅ Happy emotion info: {emotion_info['description']}")
        
        # Test genre mapping
        genre = detector.get_recommended_genre({'emotion': 'sad'})
        print(f"✅ Sad emotion genre: {genre}")
        
        # Test emotion summary
        summary = detector.get_emotion_summary({
            'emotion': 'neutral',
            'confidence': 0.85,
            'genre': 'Lo-fi/Instrumental',
            'label': '😐 Neutral'
        })
        print(f"✅ Emotion summary: {summary}")
        
        return True
        
    except Exception as e:
        print(f"❌ Emotion detection module test failed: {e}")
        traceback.print_exc()
        return False

def test_music_recommendation_module():
    """Test music recommendation module functionality"""
    print("\n🎵 Testing music recommendation module...")
    
    try:
        from recommendation import MusicRecommender
        
        # Create music recommender
        recommender = MusicRecommender()
        print("✅ MusicRecommender created successfully")
        
        # Test emotion info
        emotion_info = recommender.get_emotion_info('angry')
        print(f"✅ Angry emotion info: {emotion_info['description']}")
        
        # Test playlist recommendations
        playlists = recommender.get_recommended_playlists('happy', 2)
        print(f"✅ Happy playlists: {len(playlists)} found")
        
        # Test music summary
        summary = recommender.get_music_recommendation_summary('surprise')
        print(f"✅ Surprise music summary: {len(summary)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Music recommendation module test failed: {e}")
        traceback.print_exc()
        return False

def test_spotify_integration():
    """Test Spotify integration (without credentials)"""
    print("\n🎧 Testing Spotify integration...")
    
    try:
        from recommendation import MusicRecommender
        
        recommender = MusicRecommender()
        
        # Test without credentials
        success = recommender.setup_spotify("", "")
        if not success:
            print("✅ Spotify integration gracefully handles missing credentials")
            return True
        else:
            print("⚠️  Spotify integration unexpected success with empty credentials")
            return False
            
    except Exception as e:
        print(f"❌ Spotify integration test failed: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        'app.py',
        'camera.py',
        'emotion_detection.py',
        'recommendation.py',
        'requirements.txt',
        'README.md'
    ]
    
    all_files_exist = True
    
    for filename in required_files:
        if Path(filename).exists():
            print(f"✅ {filename} exists")
        else:
            print(f"❌ {filename} missing")
            all_files_exist = False
    
    return all_files_exist

def run_performance_test():
    """Run a simple performance test"""
    print("\n⚡ Running performance test...")
    
    try:
        import time
        import numpy as np
        
        # Test numpy performance
        start_time = time.time()
        large_array = np.random.rand(1000, 1000)
        result = np.linalg.eig(large_array)
        numpy_time = time.time() - start_time
        
        print(f"✅ NumPy performance test: {numpy_time:.3f} seconds")
        
        # Test OpenCV performance
        start_time = time.time()
        import cv2
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        gray = cv2.cvtColor(test_image, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (15, 15), 0)
        opencv_time = time.time() - start_time
        
        print(f"✅ OpenCV performance test: {opencv_time:.3f} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Emotion-Based Music Recommendation App - Test Suite")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("Camera Module", test_camera_module),
        ("Emotion Detection", test_emotion_detection_module),
        ("Music Recommendation", test_music_recommendation_module),
        ("Spotify Integration", test_spotify_integration),
        ("Performance", run_performance_test)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print("-" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    if passed == total:
        print("\n🎉 All tests passed! The app should work correctly.")
        print("🚀 You can now run: streamlit run app.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        print("🔧 Fix the issues before running the main app.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
