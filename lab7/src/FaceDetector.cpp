#include "FaceDetector.hpp"
#include <iostream>
#include <chrono>

FaceDetector::FaceDetector(const std::string& prototxt, const std::string& caffemodel) {
    try {
        net_ = cv::dnn::readNetFromCaffe(prototxt, caffemodel);
        loaded_ = true;
    } catch (const cv::Exception& e) {
        std::cerr << "[FaceDetector] Failed to load model: " << e.what() << "\n";
        loaded_ = false;
        return;
    }

    running_ = true;
    worker_ = std::thread(&FaceDetector::workerLoop, this);
}

FaceDetector::~FaceDetector() {
    running_ = false;
    if (worker_.joinable())
        worker_.join();
}

void FaceDetector::pushFrame(const cv::Mat& frame) {
    std::lock_guard<std::mutex> lock(mutex_);
    inputFrame_ = frame.clone();
    hasNewFrame_ = true;
}

std::vector<FaceRect> FaceDetector::getFaces() {
    std::lock_guard<std::mutex> lock(mutex_);
    return faces_;
}

void FaceDetector::workerLoop() {
    while (running_) {
        cv::Mat frame;
        {
            std::lock_guard<std::mutex> lock(mutex_);
            if (!hasNewFrame_) {
              
            } else {
                frame = inputFrame_.clone();
                hasNewFrame_ = false;
            }
        }

        if (frame.empty()) {
            std::this_thread::sleep_for(std::chrono::milliseconds(5));
            continue;
        }

       

        int h = frame.rows, w = frame.cols;
        cv::Mat blob = cv::dnn::blobFromImage(frame, 1.0, cv::Size(300, 300),
                                               cv::Scalar(104.0, 177.0, 123.0));
        net_.setInput(blob);
        cv::Mat detections = net_.forward();

       
        cv::Mat det = detections.reshape(1, detections.total() / 7);

        std::vector<FaceRect> found;
        for (int i = 0; i < det.rows; ++i) {
            float confidence = det.at<float>(i, 2);
            if (confidence < 0.5f) continue;

            int x1 = static_cast<int>(det.at<float>(i, 3) * w);
            int y1 = static_cast<int>(det.at<float>(i, 4) * h);
            int x2 = static_cast<int>(det.at<float>(i, 5) * w);
            int y2 = static_cast<int>(det.at<float>(i, 6) * h);

            x1 = std::max(0, x1); y1 = std::max(0, y1);
            x2 = std::min(w - 1, x2); y2 = std::min(h - 1, y2);

            found.push_back({x1, y1, x2 - x1, y2 - y1, confidence});
        }

        {
            std::lock_guard<std::mutex> lock(mutex_);
            faces_ = found;
        }
    }
}
