# Лабораторна робота №2
**Студент:** Pinchuk Katya
**Група:** FB-45
**Курс:** Засоби підготовки та аналізу даних

## Опис

Лабораторна робота з підготовки та аналізу даних. Складається з двох частин:

- **Частина 1** — завантаження та аналіз VHI-індексу для адміністративних одиниць України (NOAA)
- **Частина 2** — аналіз датасету Individual Household Electric Power Consumption

## Вимоги до системи

- Python 3.10+
- pip

## Встановлення залежностей

Створити віртуальне середовище:
```
python -m venv venv
```

Активувати віртуальне середовище:

- Windows:
```
venv\Scripts\activate
```
- Linux/Mac:
```
source venv/bin/activate
```

Встановити залежності:
```
pip install -r requirements.txt
```

## Датасет (Частина 2)

Для другої частини необхідно вручну завантажити датасет **Individual Household Electric Power Consumption** з UCI Machine Learning Repository:

https://archive.ics.uci.edu/ml/datasets/Individual+household+electric+power+consumption

Завантажити файл `household_power_consumption.txt` та розмістити його в папці проєкту поряд з `.ipynb` файлом.

## Структура репозиторію
```
├── part1_vhi.ipynb
├── part2_power.ipynb
├── requirements.txt
├── README.md
└── data/
    └── household_power_consumption.txt
```

## Запуск
```
jupyter notebook
```
