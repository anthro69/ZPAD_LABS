#pragma once
#include <opencv2/opencv.hpp>
#include "KeyProcessor.hpp"
#include "FaceDetector.hpp"

class FrameProcessor {
public:
    FrameProcessor();

    cv::Mat process(const cv::Mat& frame, Mode mode);

    // Draw face rectangles on top of frame
    void overlayFaces(cv::Mat& frame, const std::vector<FaceRect>& faces);

    // Zoom factor controlled by mouse wheel
    void setZoom(double zoom);
    double getZoom() const;

    // Brightness offset from trackbar (0–200, neutral=100)
    void setBrightness(int value);

    // Overlay FPS and frame counter on image
    void overlayStats(cv::Mat& frame, double fps, int frameCount, Mode mode);

private:
    double zoom_;
    int brightness_;

    cv::Mat applyZoom(const cv::Mat& src) const;
    cv::Mat applyBrightness(const cv::Mat& src) const;
};
