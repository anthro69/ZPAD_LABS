# Лабораторна робота №7 — Computer Vision та багатопотоковість у C++

**Виконала:** Пінчук Катерина  
**Група:** ФБ-45  
**Дисципліна:** Засоби підготовки та аналізу даних  

## Мета

Поєднання класичного C++ із сучасним CV/ML: детекція облич за допомогою `cv::dnn` (ResNet-10 SSD), винесення важких обчислень у фоновий потік за допомогою `std::thread` та `std::mutex`.

---

## Збірка та запуск

### 1. Встановити залежності та завантажити модель

```bash
bash preinstall.sh
```

Скрипт встановлює `libopencv-dev`, `cmake`, `build-essential`, `libv4l-dev`, `wget` та завантажує два файли нейромережі:
- `deploy.prototxt`
- `res10_300x300_ssd_iter_140000.caffemodel`

### 2. Зібрати проєкт

```bash
mkdir -p build && cd build
cmake ..
make -j$(nproc)
cd ..
```

### 3. Запустити

```bash
./build/lab6
```

Або через `run.sh` якщо він є в проєкті:

```bash
./run.sh
```

> Файли моделі (`deploy.prototxt` і `.caffemodel`) мають знаходитись у кореневій папці проєкту, звідки запускається бінарник.

---

## Керування

| Клавіша | Дія |
|--------|-----|
| `F` | Режим детекції облич (Face) |
| `0` | Normal |
| `1` | Invert |
| `2` | Blur |
| `3` | Canny |
| `4` | Sobel |
| `5` | Binary |
| Scroll | Zoom |
| `q` / ESC | Вихід |

---

## Архітектура

### `FaceDetector` (новий клас, рівень 2)

Відповідає за асинхронну детекцію облич. Містить:

- `std::thread worker_` — фоновий потік, який постійно крутиться і запускає `net.forward()` щойно отримує новий кадр.
- `std::mutex mutex_` — захищає спільні дані (`inputFrame_` та `faces_`) від одночасного доступу двох потоків.
- `std::atomic<bool> running_` — прапорець безпечної зупинки потоку при виклику деструктора.

Логіка: main thread викликає `pushFrame()` (копія кадру під м'ютексом) і `getFaces()` (забирає останні координати під м'ютексом). Worker thread самостійно бере кадр, запускає інференс і зберігає результат. Завдяки цьому відео залишається плавним (30+ FPS), рамка оновлюється асинхронно.

### `FrameProcessor`

Відповідає за обробку кадру: zoom, яскравість, фільтри (Canny, Sobel, Binary, Blur, Invert). Метод `overlayFaces()` малює зелені прямокутники з confidence навколо знайдених облич. Метод `overlayStats()` виводить FPS, номер кадру, zoom та поточний режим.

### `KeyProcessor`

Обробляє натискання клавіш, зберігає поточний `Mode`. Підтримує режими: `NORMAL`, `INVERT`, `BLUR`, `CANNY`, `SOBEL`, `BINARY`, `FACE`.

### `CameraProvider`

Захоплення відео з камери через OpenCV (`cv::VideoCapture`).

### `Display`

Відображення кадру у вікні (`cv::imshow`), зберігає назву вікна для trackbar та mouse callback.

---
## Вимоги до системи

- OS: Linux (Ubuntu 20.04+ / Kali / Debian)
- CMake >= 3.10
- GCC >= 9 (підтримка C++17)
- OpenCV >= 4.0 (з модулем `dnn`)
- libv4l2 (для роботи з камерою)
- Підключена веб-камера

---

## Структура проєкту

```
lab7/
├── include/
│   ├── CameraProvider.hpp
│   ├── Display.hpp
│   ├── FaceDetector.hpp
│   ├── FrameProcessor.hpp
│   └── KeyProcessor.hpp
├── src/
│   ├── CameraProvider.cpp
│   ├── Display.cpp
│   ├── FaceDetector.cpp
│   ├── FrameProcessor.cpp
│   ├── KeyProcessor.cpp
│   └── main.cpp
├── build/                  # генерується при збірці
├── deploy.prototxt         # архітектура нейромережі
├── res10_300x300_ssd_iter_140000.caffemodel  # ваги нейромережі
├── CMakeLists.txt
├── preinstall.sh

```

## Модель

Використовується ResNet-10 SSD face detector від OpenCV:
- Архітектура: [deploy.prototxt](https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt)
- Ваги: [res10_300x300_ssd_iter_140000.caffemodel](https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel)

Вхід: blob 300×300, mean subtraction `(104, 177, 123)`. Виводяться обличчя з confidence > 50%.
