#pragma once
#include <opencv2/opencv.hpp>
#include <string>

class Display {
public:
    explicit Display(const std::string& windowName = "Camera");
    ~Display();

    void show(const cv::Mat& frame);
    const std::string& windowName() const;

private:
    std::string windowName_;
};
