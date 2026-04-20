#pragma once
#include <opencv2/opencv.hpp>
#include "KeyProcessor.hpp"

class FrameProcessor {
public:
    FrameProcessor();

    cv::Mat process(const cv::Mat& frame, Mode mode);

   
    void setZoom(double zoom);
    double getZoom() const;

    void setBrightness(int value);

   
    void overlayStats(cv::Mat& frame, double fps, int frameCount);

private:
    double zoom_;
    int brightness_; 

    cv::Mat applyZoom(const cv::Mat& src) const;
    cv::Mat applyBrightness(const cv::Mat& src) const;
};
