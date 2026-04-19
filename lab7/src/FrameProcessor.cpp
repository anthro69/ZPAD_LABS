#include "FrameProcessor.hpp"
#include <sstream>
#include <iomanip>

FrameProcessor::FrameProcessor() : zoom_(1.0), brightness_(100) {}

void FrameProcessor::setZoom(double zoom) {
    zoom_ = std::max(0.2, std::min(zoom, 5.0));
}

double FrameProcessor::getZoom() const { return zoom_; }

void FrameProcessor::setBrightness(int value) {
    brightness_ = value;
}

cv::Mat FrameProcessor::applyZoom(const cv::Mat& src) const {
    if (std::abs(zoom_ - 1.0) < 1e-6) return src;

    int newW = static_cast<int>(src.cols * zoom_);
    int newH = static_cast<int>(src.rows * zoom_);

    if (zoom_ > 1.0) {
        int x = (newW - src.cols) / 2;
        int y = (newH - src.rows) / 2;
        cv::Mat scaled;
        cv::resize(src, scaled, cv::Size(newW, newH));
        cv::Rect roi(x, y, src.cols, src.rows);
        roi &= cv::Rect(0, 0, scaled.cols, scaled.rows);
        return scaled(roi).clone();
    } else {
        cv::Mat scaled;
        cv::resize(src, scaled, cv::Size(newW, newH));
        cv::Mat canvas = cv::Mat::zeros(src.size(), src.type());
        int x = (src.cols - newW) / 2;
        int y = (src.rows - newH) / 2;
        scaled.copyTo(canvas(cv::Rect(x, y, newW, newH)));
        return canvas;
    }
}

cv::Mat FrameProcessor::applyBrightness(const cv::Mat& src) const {
    double alpha = brightness_ / 100.0;
    cv::Mat result;
    src.convertTo(result, -1, alpha, 0);
    return result;
}

cv::Mat FrameProcessor::process(const cv::Mat& frame, Mode mode) {
    if (frame.empty()) return frame;

    cv::Mat zoomed = applyZoom(frame);
    cv::Mat bright = applyBrightness(zoomed);
    cv::Mat result;

    switch (mode) {
        case Mode::NORMAL:
        case Mode::FACE:   // FACE mode shows normal video; faces drawn separately
            result = bright;
            break;

        case Mode::INVERT:
            cv::bitwise_not(bright, result);
            break;

        case Mode::BLUR:
            cv::GaussianBlur(bright, result, cv::Size(21, 21), 0);
            break;

        case Mode::CANNY: {
            cv::Mat gray;
            cv::cvtColor(bright, gray, cv::COLOR_BGR2GRAY);
            cv::Canny(gray, result, 50, 150);
            cv::cvtColor(result, result, cv::COLOR_GRAY2BGR);
            break;
        }

        case Mode::SOBEL: {
            cv::Mat gray, gradX, gradY, absX, absY;
            cv::cvtColor(bright, gray, cv::COLOR_BGR2GRAY);
            cv::Sobel(gray, gradX, CV_16S, 1, 0, 3);
            cv::Sobel(gray, gradY, CV_16S, 0, 1, 3);
            cv::convertScaleAbs(gradX, absX);
            cv::convertScaleAbs(gradY, absY);
            cv::addWeighted(absX, 0.5, absY, 0.5, 0, result);
            cv::cvtColor(result, result, cv::COLOR_GRAY2BGR);
            break;
        }

        case Mode::BINARY: {
            cv::Mat gray;
            cv::cvtColor(bright, gray, cv::COLOR_BGR2GRAY);
            cv::threshold(gray, result, 127, 255, cv::THRESH_BINARY);
            cv::cvtColor(result, result, cv::COLOR_GRAY2BGR);
            break;
        }
    }

    return result;
}

void FrameProcessor::overlayFaces(cv::Mat& frame, const std::vector<FaceRect>& faces) {
    for (const auto& f : faces) {
        cv::rectangle(frame,
                      cv::Rect(f.x, f.y, f.w, f.h),
                      cv::Scalar(0, 255, 0), 2, cv::LINE_AA);

        std::ostringstream conf;
        conf << std::fixed << std::setprecision(0) << (f.confidence * 100) << "%";
        cv::putText(frame, conf.str(),
                    cv::Point(f.x, f.y - 6),
                    cv::FONT_HERSHEY_SIMPLEX, 0.55,
                    cv::Scalar(0, 255, 0), 1, cv::LINE_AA);
    }
}

void FrameProcessor::overlayStats(cv::Mat& frame, double fps, int frameCount, Mode mode) {
    if (frame.empty()) return;

    std::string modeName;
    switch (mode) {
        case Mode::NORMAL: modeName = "Normal";  break;
        case Mode::INVERT: modeName = "Invert";  break;
        case Mode::BLUR:   modeName = "Blur";    break;
        case Mode::CANNY:  modeName = "Canny";   break;
        case Mode::SOBEL:  modeName = "Sobel";   break;
        case Mode::BINARY: modeName = "Binary";  break;
        case Mode::FACE:   modeName = "Face";    break;
    }

    std::ostringstream ss;
    ss << "FPS: " << std::fixed << std::setprecision(1) << fps
       << "  Frame: " << frameCount
       << "  Zoom: " << std::setprecision(2) << zoom_ << "x"
       << "  Mode: " << modeName;

    cv::putText(frame, ss.str(),
                cv::Point(10, 30),
                cv::FONT_HERSHEY_SIMPLEX, 0.7,
                cv::Scalar(0, 255, 0), 2, cv::LINE_AA);

    cv::putText(frame,
                "0:Normal 1:Invert 2:Blur 3:Canny 4:Sobel 5:Binary F:Face | Scroll=Zoom | q=Quit",
                cv::Point(10, frame.rows - 10),
                cv::FONT_HERSHEY_SIMPLEX, 0.45,
                cv::Scalar(200, 200, 200), 1, cv::LINE_AA);
}
