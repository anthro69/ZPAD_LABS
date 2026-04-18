# Lab 6 — C++ OpenCV Camera Viewer

## Вимоги до системи

| Параметр | Значення |
|---|---|
| ОС | Ubuntu 22.04 / Kali Linux (Debian-based) |
| Компілятор | GCC 9+ або Clang 10+ |
| CMake | 3.10+ |
| Бібліотека | libopencv-dev (≥ 4.x) |
| Камера | Будь-яка v4l2-сумісна (вбудована або USB) |

## Швидкий старт

```bash
git clone <repo_url>
cd lab6_opencv

./preinstall.sh   # встановити залежності (потрібен sudo)
./build.sh        # зібрати проєкт
./run.sh          # запустити (камера 0 за замовчуванням)
# або
./run.sh 1        # запустити з камерою з індексом 1
```

## Архітектура

```
lab6_opencv/
├── CMakeLists.txt
├── preinstall.sh
├── build.sh
├── run.sh
├── README.md
├── include/
│   ├── CameraProvider.hpp
│   ├── KeyProcessor.hpp
│   ├── FrameProcessor.hpp
│   └── Display.hpp
├── src/
│   ├── main.cpp
│   ├── CameraProvider.cpp
│   ├── KeyProcessor.cpp
│   ├── FrameProcessor.cpp
│   └── Display.cpp
└── build/           ← генерується при білді
```

| Клас | Відповідальність |
|---|---|
| `CameraProvider` | Захоплення кадрів з камери (`cv::VideoCapture`) |
| `KeyProcessor` | Обробка клавіш, зберігання поточного режиму (`enum Mode`) |
| `FrameProcessor` | Обробка зображень: фільтри, зум, яскравість, overlay HUD |
| `Display` | Відображення результату (`cv::imshow`) |

## Керування

| Клавіша / дія | Режим / ефект |
|---|---|
| `0` | Нормальний (без обробки) |
| `1` | Інверсія кольорів |
| `2` | Gaussian Blur |
| `3` | Canny (контури) |
| `4` | Sobel (градієнти) |
| `5` | Бінаризація |
| Scroll up/down | Збільшення / зменшення зуму |
| Trackbar **Brightness** | Яскравість кадру (0–200, нейтраль = 100) |
| `q` або `ESC` | Вийти |

## HUD (накладена інформація)

На кожному кадрі відображається:
- **FPS** — кількість кадрів за секунду
- **Frame** — лічильник кадрів поточної секунди
- **Zoom** — поточний коефіцієнт масштабування
- Рядок підказок знизу екрана
