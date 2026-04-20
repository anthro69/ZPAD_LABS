#include "KeyProcessor.hpp"

KeyProcessor::KeyProcessor() : mode_(Mode::NORMAL), quit_(false) {}

bool KeyProcessor::processKey(int key) {
    if (key == 'q' || key == 27) { // 'q' or ESC
        quit_ = true;
        return false;
    }
    switch (key) {
        case '0': mode_ = Mode::NORMAL;  break;
        case '1': mode_ = Mode::INVERT;  break;
        case '2': mode_ = Mode::BLUR;    break;
        case '3': mode_ = Mode::CANNY;   break;
        case '4': mode_ = Mode::SOBEL;   break;
        case '5': mode_ = Mode::BINARY;  break;
        default: break;
    }
    return true;
}

Mode KeyProcessor::getMode() const { return mode_; }
bool KeyProcessor::shouldQuit() const { return quit_; }
