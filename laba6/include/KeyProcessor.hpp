#pragma once

enum class Mode {
    NORMAL = 0,
    INVERT,
    BLUR,
    CANNY,
    SOBEL,
    BINARY
};

class KeyProcessor {
public:
    KeyProcessor();

    bool processKey(int key);

    Mode getMode() const;
    bool shouldQuit() const;

private:
    Mode mode_;
    bool quit_;
};
