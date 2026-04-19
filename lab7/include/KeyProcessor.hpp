#pragma once

enum class Mode {
    NORMAL = 0,
    INVERT,
    BLUR,
    CANNY,
    SOBEL,
    BINARY,
    FACE
};

class KeyProcessor {
public:
    KeyProcessor();

    // Process key from cv::waitKey; returns false if quit requested
    bool processKey(int key);

    Mode getMode() const;
    bool shouldQuit() const;

private:
    Mode mode_;
    bool quit_;
};
