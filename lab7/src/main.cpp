#include <opencv2/opencv.hpp>
#include <iostream>
#include <chrono>

#include "CameraProvider.hpp"
#include "KeyProcessor.hpp"
#include "FrameProcessor.hpp"
#include "Display.hpp"
#include "FaceDetector.hpp"

// ── Globals for callbacks ─────────────────────────────────────────────────────
static FrameProcessor* g_fp = nullptr;
static int g_brightness = 100;

void onMouse(int event, int /*x*/, int /*y*/, int flags, void* /*userdata*/) {
    if (!g_fp) return;
    if (event == cv::EVENT_MOUSEWHEEL) {
        double delta = (cv::getMouseWheelDelta(flags) > 0) ? 0.1 : -0.1;
        g_fp->setZoom(g_fp->getZoom() + delta);
    }
}

void onBrightness(int value, void* /*userdata*/) {
    if (g_fp) g_fp->setBrightness(value);
}

// ── main ──────────────────────────────────────────────────────────────────────
int main(int argc, char* argv[]) {
    int camIndex = 0;
    if (argc > 1) camIndex = std::stoi(argv[1]);

    CameraProvider camera(camIndex);
    KeyProcessor   keyProc;
    FrameProcessor frameProc;
    Display        display("Camera Viewer");

    g_fp = &frameProc;

    // Load face detector (worker thread starts inside constructor)
    FaceDetector faceDetector("deploy.prototxt",
                               "res10_300x300_ssd_iter_140000.caffemodel");

    if (!faceDetector.isLoaded()) {
        std::cerr << "[main] Warning: face detector not loaded. F mode will show no faces.\n";
    }

    cv::setMouseCallback(display.windowName(), onMouse, nullptr);
    cv::createTrackbar("Brightness", display.windowName(),
                       &g_brightness, 200, onBrightness);
    cv::setTrackbarPos("Brightness", display.windowName(), 100);

    int frameCount = 0;
    double fps = 0.0;
    auto tStart = std::chrono::steady_clock::now();

    while (!keyProc.shouldQuit()) {
        cv::Mat frame = camera.getFrame();
        if (frame.empty()) {
            std::cerr << "Empty frame received\n";
            break;
        }

        Mode mode = keyProc.getMode();

        // Send frame to background detector when in FACE mode
        if (mode == Mode::FACE && faceDetector.isLoaded()) {
            faceDetector.pushFrame(frame);
        }

        cv::Mat processed = frameProc.process(frame, mode);

        // Overlay face rectangles (drawn on top of processed frame)
        if (mode == Mode::FACE && faceDetector.isLoaded()) {
            auto faces = faceDetector.getFaces();
            frameProc.overlayFaces(processed, faces);
        }

        frameProc.overlayStats(processed, fps, frameCount, mode);
        display.show(processed);

        int key = cv::waitKey(1);
        keyProc.processKey(key);

        // FPS calculation
        ++frameCount;
        auto now = std::chrono::steady_clock::now();
        double elapsed = std::chrono::duration<double>(now - tStart).count();
        if (elapsed >= 1.0) {
            fps = frameCount / elapsed;
            frameCount = 0;
            tStart = now;
        }
    }

    return 0;
}
