#include "CameraProvider.hpp"
#include <stdexcept>
#include <iostream>

CameraProvider::CameraProvider(int cameraIndex) {
    // Use libv4l2 backend — handles format conversion transparently
    cap_.open(cameraIndex, cv::CAP_V4L);
    if (!cap_.isOpened()) {
        throw std::runtime_error("Cannot open camera with index " + std::to_string(cameraIndex));
    }

    cap_.set(cv::CAP_PROP_FRAME_WIDTH,  640);
    cap_.set(cv::CAP_PROP_FRAME_HEIGHT, 480);
    cap_.set(cv::CAP_PROP_FPS, 30);

    // Drain init frames
    cv::Mat dummy;
    for (int i = 0; i < 5; ++i) cap_ >> dummy;

    cv::Mat test;
    cap_ >> test;
    if (!test.empty()) {
        std::cout << "[CameraProvider] Frame: "
                  << test.cols << "x" << test.rows
                  << " ch=" << test.channels()
                  << " type=" << test.type() << "\n";
        cv::Vec3b px = test.at<cv::Vec3b>(test.rows/2, test.cols/2);
        std::cout << "[CameraProvider] Center pixel B=" << (int)px[0]
                  << " G=" << (int)px[1] << " R=" << (int)px[2] << "\n";
    }
}

CameraProvider::~CameraProvider() {
    cap_.release();
}

bool CameraProvider::isOpened() const {
    return cap_.isOpened();
}

cv::Mat CameraProvider::getFrame() {
    cv::Mat frame;
    cap_ >> frame;
    return frame;
}
