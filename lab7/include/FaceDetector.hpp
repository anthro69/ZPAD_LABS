#pragma once
#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <thread>
#include <mutex>
#include <atomic>
#include <vector>

struct FaceRect {
    int x, y, w, h;
    float confidence;
};

class FaceDetector {
public:
    FaceDetector(const std::string& prototxt, const std::string& caffemodel);
    ~FaceDetector();

    // Main thread calls this — sends a copy of the frame to worker
    void pushFrame(const cv::Mat& frame);

    // Main thread calls this — gets last known face rects
    std::vector<FaceRect> getFaces();

    bool isLoaded() const { return loaded_; }

private:
    void workerLoop();

    cv::dnn::Net net_;
    bool loaded_ = false;

    std::thread worker_;
    std::mutex mutex_;
    std::atomic<bool> running_{false};

    cv::Mat inputFrame_;
    bool hasNewFrame_ = false;

    std::vector<FaceRect> faces_;
};
