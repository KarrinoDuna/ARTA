import tkinter as tk
from tkinter import ttk, messagebox
import math
from typing import List, Tuple

class MultiArtilleryCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Артиллерийский калькулятор - Мультисистема")
        self.root.geometry("1100x800")
        
        self.artilleries = []  # Список артиллерий
        self.chain_points = []  # Точки цепочки наводчиков
        self.results = []  # Результаты для каждой артиллерии
        self.wind_direction = 0  # Направление ветра в градусах
        self.wind_force = 0  # Сила ветра (0-5)
        self.wind_drift = 5  # Снос на единицу силы ветра (метров)
        
        self.setup_ui()
        self.setup_treeview_editing()
    
    def setup_ui(self):
        # Создаем вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка 1: Артиллерии
        self.tab_artillery = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_artillery, text="1. Артиллерийские установки")
        self.setup_artillery_tab()
        
        # Вкладка 2: Цепочка наводчиков
        self.tab_chain = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_chain, text="2. Цепочка наводчиков")
        self.setup_chain_tab()
        
        # Вкладка 3: Роза ветров
        self.tab_wind = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_wind, text="3. Роза ветров")
        self.setup_wind_tab()
        
        # Вкладка 4: Результаты
        self.tab_results = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_results, text="4. Результаты стрельбы")
        self.setup_results_tab()
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе. Начните с ввода артиллерийских установок")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
    
    def setup_artillery_tab(self):
        """Настройка вкладки для ввода артиллерийских установок"""
        main_frame = ttk.Frame(self.tab_artillery, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Ввод артиллерийских установок", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Описание
        desc_text = """На этой вкладке введите данные по артиллерийским установкам, 
которые видит первый наводчик. Для каждой установки укажите:
- Азимут от наводчика к артиллерии (в градусах 0-360)
- Дистанцию от наводчика к артиллерии (в метрах)

Можно добавить до 10 артиллерийских установок."""
        
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.LEFT,
                              wraplength=800, font=("Arial", 10))
        desc_label.pack(pady=(0, 20))
        
        # Таблица артиллерий
        columns = ("№", "Артиллерия", "Азимут (°)", "Дистанция (м)")
        
        self.artillery_tree = ttk.Treeview(main_frame, columns=columns, 
                                          show='headings', height=8)
        
        # Заголовки
        self.artillery_tree.heading("#1", text="№")
        self.artillery_tree.heading("#2", text="Артиллерия")
        self.artillery_tree.heading("#3", text="Азимут (°)")
        self.artillery_tree.heading("#4", text="Дистанция (м)")
        
        # Ширина колонок
        self.artillery_tree.column("#1", width=50, anchor=tk.CENTER)
        self.artillery_tree.column("#2", width=150, anchor=tk.CENTER)
        self.artillery_tree.column("#3", width=150, anchor=tk.CENTER)
        self.artillery_tree.column("#4", width=150, anchor=tk.CENTER)
        
        self.artillery_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Полоса прокрутки для таблицы артиллерий
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, 
                                 command=self.artillery_tree.yview)
        self.artillery_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления артиллериями
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Добавить артиллерию", 
                  command=self.add_artillery).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить выбранную", 
                  command=self.delete_artillery).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить все", 
                  command=self.clear_artilleries).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Пример данных", 
                  command=self.load_artillery_example).pack(side=tk.LEFT, padx=5)
        
        # Счетчик артиллерий
        self.artillery_count = 0
        
        # Подсказка
        help_label = ttk.Label(main_frame, 
                              text="Для редактирования дважды щелкните по ячейке",
                              font=("Arial", 9), foreground="blue")
        help_label.pack(pady=(10, 0))
    
    def setup_chain_tab(self):
        """Настройка вкладки для цепочки наводчиков"""
        main_frame = ttk.Frame(self.tab_chain, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Цепочка наводчиков до цели", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Описание
        desc_text = """На этой вкладке введите цепочку наводчиков от первого наводчика до цели.
Для каждой точки в цепочке укажите:
- Азимут к следующей точке (в градусах 0-360)
- Дистанцию до следующей точки (в метрах)

Последняя точка в цепочке - это ЦЕЛЬ."""
        
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.LEFT,
                              wraplength=800, font=("Arial", 10))
        desc_label.pack(pady=(0, 20))
        
        # Таблица цепочки наводчиков
        columns = ("№", "Точка", "Азимут на следующую (°)", "Дистанция до следующей (м)")
        
        self.chain_tree = ttk.Treeview(main_frame, columns=columns, 
                                      show='headings', height=8)
        
        # Заголовки
        self.chain_tree.heading("#1", text="№")
        self.chain_tree.heading("#2", text="Точка")
        self.chain_tree.heading("#3", text="Азимут на следующую (°)")
        self.chain_tree.heading("#4", text="Дистанция до следующей (м)")
        
        # Ширина колонок
        self.chain_tree.column("#1", width=50, anchor=tk.CENTER)
        self.chain_tree.column("#2", width=150, anchor=tk.CENTER)
        self.chain_tree.column("#3", width=200, anchor=tk.CENTER)
        self.chain_tree.column("#4", width=200, anchor=tk.CENTER)
        
        self.chain_tree.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Полоса прокрутки для таблицы цепочки
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, 
                                 command=self.chain_tree.yview)
        self.chain_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления цепочкой
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Добавить точку", 
                  command=self.add_chain_point).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить выбранную", 
                  command=self.delete_chain_point).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить цепочку", 
                  command=self.clear_chain).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Пример цепочки", 
                  command=self.load_chain_example).pack(side=tk.LEFT, padx=5)
        
        # Подсказка
        help_label = ttk.Label(main_frame, 
                              text="Для редактирования дважды щелкните по ячейке",
                              font=("Arial", 9), foreground="blue")
        help_label.pack(pady=(10, 0))
        
        # Счетчик точек цепочки
        self.chain_count = 0
    
    def setup_wind_tab(self):
        """Настройка вкладки для розы ветров"""
        main_frame = ttk.Frame(self.tab_wind, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Роза ветров", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Описание
        desc_text = """На этой вкладке задайте параметры ветра для коррекции стрельбы:
- Направление ветра (куда дует ветер)
- Силу ветра (0-5)
- Коэффициент сноса (метров на единицу силы ветра)

Используйте мышку для вращения стрелки или введите градусы вручную."""
        
        desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.LEFT,
                              wraplength=800, font=("Arial", 10))
        desc_label.pack(pady=(0, 20))
        
        # Контейнер для розы ветров и параметров
        wind_container = ttk.Frame(main_frame)
        wind_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Левая часть - графическая роза ветров
        wind_rose_frame = ttk.LabelFrame(wind_container, text="Направление ветра", padding="10")
        wind_rose_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Создаем Canvas для розы ветров (уменьшенный размер)
        self.wind_canvas = tk.Canvas(wind_rose_frame, width=300, height=300, bg='white')
        self.wind_canvas.pack(pady=(0, 10))
        
        # Поле для ручного ввода градусов
        manual_input_frame = ttk.Frame(wind_rose_frame)
        manual_input_frame.pack(pady=10)
        
        ttk.Label(manual_input_frame, text="Градусы (0-360):", font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.wind_degrees_var = tk.StringVar(value="0")
        self.wind_degrees_entry = ttk.Entry(manual_input_frame, textvariable=self.wind_degrees_var, width=10)
        self.wind_degrees_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(manual_input_frame, text="Применить", 
                  command=self.apply_wind_degrees).pack(side=tk.LEFT)
        
        # Правая часть - параметры ветра
        params_frame = ttk.LabelFrame(wind_container, text="Параметры ветра", padding="10")
        params_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Сила ветра (0-5)
        ttk.Label(params_frame, text="Сила ветра (0-5):", font=("Arial", 10)).pack(pady=(10, 5))
        
        self.wind_force_var = tk.StringVar(value="0")
        wind_force_frame = ttk.Frame(params_frame)
        wind_force_frame.pack(pady=(0, 20))
        
        for i in range(6):
            rb = ttk.Radiobutton(wind_force_frame, text=str(i), variable=self.wind_force_var, 
                                value=str(i))
            rb.pack(side=tk.LEFT, padx=5)
        
        # Коэффициент сноса
        ttk.Label(params_frame, text="Коэффициент сноса (м на единицу силы):", 
                 font=("Arial", 10)).pack(pady=(10, 5))
        
        self.wind_drift_var = tk.StringVar(value="5")
        drift_entry = ttk.Entry(params_frame, textvariable=self.wind_drift_var, width=10)
        drift_entry.pack(pady=(0, 20))
        
        # Отображение текущего направления
        self.wind_direction_var = tk.StringVar(value="0° (N - Север)")
        ttk.Label(params_frame, text="Текущее направление:", 
                 font=("Arial", 10)).pack(pady=(10, 5))
        
        direction_label = ttk.Label(params_frame, textvariable=self.wind_direction_var,
                                   font=("Arial", 12, "bold"), foreground="blue")
        direction_label.pack(pady=(0, 20))
        
        # Кнопки
        button_frame = ttk.Frame(params_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Сбросить ветер", 
                  command=self.reset_wind).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Пример", 
                  command=self.wind_example).pack(side=tk.LEFT, padx=5)
        
        # Нарисуем начальную розу ветров
        self.draw_wind_rose()
        
        # Привязываем обработчики событий
        self.wind_canvas.bind("<B1-Motion>", self.on_wind_rose_drag)
        self.wind_canvas.bind("<Button-1>", self.on_wind_rose_click)
        
        # Кнопка расчета
        ttk.Button(main_frame, text="РАССЧИТАТЬ ВСЕ", 
                  command=self.calculate_all,
                  style="Accent.TButton").pack(pady=20)
        
        # Стиль для акцентной кнопки
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Arial", 10, "bold"))
    
    def setup_results_tab(self):
        """Настройка вкладки для результатов"""
        main_frame = ttk.Frame(self.tab_results, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(main_frame, 
                               text="Результаты расчетов для всех артиллерий", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Текстовое поле для детальных результатов
        self.results_text = tk.Text(main_frame, height=20, width=100, 
                                   font=("Courier", 10))
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Полоса прокрутки для текста
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, 
                                 command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки для результатов
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Копировать результаты", 
                  command=self.copy_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить результаты", 
                  command=self.clear_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Экспорт в файл", 
                  command=self.export_results).pack(side=tk.LEFT, padx=5)
    
    def setup_treeview_editing(self):
        """Настройка редактирования ячеек Treeview"""
        self.editing_entry = None
        
        def on_double_click(event, tree):
            # Определяем строку и колонку
            region = tree.identify_region(event.x, event.y)
            if region == "cell":
                item = tree.identify_row(event.y)
                column = tree.identify_column(event.x)
                
                if not item:
                    return
                
                # Получаем координаты ячейки
                bbox = tree.bbox(item, column)
                if not bbox:
                    return
                
                # Получаем текущее значение
                column_index = int(column[1:]) - 1
                values = list(tree.item(item, 'values'))
                
                # Проверяем, можно ли редактировать эту колонку
                # Колонки с индексом 0 и 1 не редактируются (№ и название)
                if column_index < 2:
                    return
                
                current_value = values[column_index]
                
                # Создаем поле для редактирования
                entry = ttk.Entry(tree, width=15)
                entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
                entry.insert(0, str(current_value))
                entry.select_range(0, tk.END)
                entry.focus()
                
                def save_edit(event=None):
                    new_value = entry.get()
                    values[column_index] = new_value
                    tree.item(item, values=tuple(values))
                    entry.destroy()
                    self.editing_entry = None
                    self.status_var.set("Данные сохранены")
                
                def cancel_edit(event=None):
                    entry.destroy()
                    self.editing_entry = None
                
                entry.bind('<Return>', save_edit)
                entry.bind('<Escape>', cancel_edit)
                entry.bind('<FocusOut>', lambda e: save_edit())
                
                self.editing_entry = entry
        
        # Привязываем обработчики двойного клика для обеих таблиц
        self.artillery_tree.bind('<Double-1>', 
                                lambda e: on_double_click(e, self.artillery_tree))
        self.chain_tree.bind('<Double-1>', 
                            lambda e: on_double_click(e, self.chain_tree))
        
        # Также добавляем возможность редактирования по клавише F2
        def start_edit_with_f2(event, tree):
            if event.keysym == 'F2':
                # Имитируем двойной клик
                on_double_click(event, tree)
        
        self.artillery_tree.bind('<Key>', 
                                lambda e: start_edit_with_f2(e, self.artillery_tree))
        self.chain_tree.bind('<Key>', 
                            lambda e: start_edit_with_f2(e, self.chain_tree))
    
    def draw_wind_rose(self):
        """Отрисовка розы ветров с простыми направлениями"""
        canvas = self.wind_canvas
        canvas.delete("all")  # Очищаем canvas
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            width, height = 300, 300
        
        center_x = width // 2
        center_y = height // 2
        radius = min(center_x, center_y) - 20
        
        # Рисуем внешний круг
        canvas.create_oval(center_x - radius, center_y - radius,
                          center_x + radius, center_y + radius,
                          outline="black", width=2)
        
        # Рисуем внутренний круг
        canvas.create_oval(center_x - radius//2, center_y - radius//2,
                          center_x + radius//2, center_y + radius//2,
                          outline="gray", width=1)
        
        # Простые направления через 45 градусов
        directions = {
            0: "N",
            45: "NE",
            90: "E",
            135: "SE",
            180: "S",
            225: "SW",
            270: "W",
            315: "NW"
        }
        
        for angle in range(0, 360, 45):
            # Угол в радианах для математических расчетов
            # В математике 0° = вправо, но нам нужно 0° = вверх (север)
            math_angle = math.radians(angle - 90)  # Поворачиваем на -90°, чтобы север был вверху
            
            # Линия направления
            x1 = center_x + radius * 0.8 * math.cos(math_angle)
            y1 = center_y + radius * 0.8 * math.sin(math_angle)
            x2 = center_x + radius * math.cos(math_angle)
            y2 = center_y + radius * math.sin(math_angle)
            
            canvas.create_line(x1, y1, x2, y2, fill="gray", width=1)
            
            # Подпись направления
            text_x = center_x + radius * 1.1 * math.cos(math_angle)
            text_y = center_y + radius * 1.1 * math.sin(math_angle)
            
            direction_text = directions.get(angle, "")
            canvas.create_text(text_x, text_y, text=direction_text, 
                             font=("Arial", 10, "bold"))
        
        # Рисуем основные направления (N, E, S, W) жирными линиями
        for angle in [0, 90, 180, 270]:
            math_angle = math.radians(angle - 90)
            x1 = center_x + radius * 0.7 * math.cos(math_angle)
            y1 = center_y + radius * 0.7 * math.sin(math_angle)
            x2 = center_x + radius * math.cos(math_angle)
            y2 = center_y + radius * math.sin(math_angle)
            
            canvas.create_line(x1, y1, x2, y2, fill="black", width=2)
        
        # Рисуем стрелку направления ветра
        self.draw_wind_arrow()
    
    def draw_wind_arrow(self):
        """Отрисовка стрелки направления ветра"""
        canvas = self.wind_canvas
        canvas.delete("arrow")  # Удаляем только стрелку
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            width, height = 300, 300
        
        center_x = width // 2
        center_y = height // 2
        radius = min(center_x, center_y) - 20
        
        # Угол в радианах (0° = север, 90° = восток)
        # В математике 0° = вправо, поэтому вычитаем 90°
        # Стрелка должна показывать, куда дует ветер, поэтому используем прямой угол
        math_angle = math.radians(self.wind_direction - 90)
        
        # Координаты кончика стрелки (стрелка указывает направление ветра)
        tip_x = center_x + radius * 0.8 * math.cos(math_angle)
        tip_y = center_y + radius * 0.8 * math.sin(math_angle)
        
        # Координаты основания стрелки
        base_angle = math_angle + math.pi  # Противоположное направление
        base_x = center_x + radius * 0.2 * math.cos(base_angle)
        base_y = center_y + radius * 0.2 * math.sin(base_angle)
        
        # Координаты для боковых точек стрелки
        side_angle1 = math_angle - math.radians(30)  # Изменяем знак для правильной стрелки
        side_angle2 = math_angle + math.radians(30)
        
        side1_x = center_x + radius * 0.15 * math.cos(side_angle1)
        side1_y = center_y + radius * 0.15 * math.sin(side_angle1)
        
        side2_x = center_x + radius * 0.15 * math.cos(side_angle2)
        side2_y = center_y + radius * 0.15 * math.sin(side_angle2)
        
        # Рисуем стрелку (треугольник)
        canvas.create_polygon(tip_x, tip_y, side1_x, side1_y, side2_x, side2_y,
                            fill="red", outline="black", width=2, tags="arrow")
        
        # Рисуем линию через центр
        canvas.create_line(base_x, base_y, tip_x, tip_y, 
                          fill="blue", width=3, tags="arrow")
    
    def on_wind_rose_click(self, event):
        """Обработка клика по розе ветров"""
        self.update_wind_direction_from_coords(event.x, event.y)
    
    def on_wind_rose_drag(self, event):
        """Обработка перетаскивания по розе ветров"""
        self.update_wind_direction_from_coords(event.x, event.y)
    
    def update_wind_direction_from_coords(self, x, y):
        """Обновление направления ветра из координат - теперь стрелка следует за мышкой"""
        canvas = self.wind_canvas
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            width, height = 300, 300
        
        center_x = width // 2
        center_y = height // 2
        
        # Вычисляем смещение от центра
        dx = x - center_x
        dy = y - center_y
        
        # Вычисляем математический угол (0° = вправо)
        # Учитываем, что ось Y в Canvas направлена вниз
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        # Преобразуем в компасный угол (0° = север, 90° = восток)
        # Для Canvas: при dx=0, dy<0 (мышь выше центра) = север = 0°
        compass_angle = (90 - angle_deg) % 360
        
        # Обновляем направление ветра
        self.wind_direction = compass_angle
        
        # Обновляем поле ввода
        self.wind_degrees_var.set(f"{compass_angle:.0f}")
        
        # Обновляем отображение
        self.draw_wind_arrow()
        
        # Обновляем текстовое представление
        self.update_wind_direction_text()
    
    def apply_wind_degrees(self):
        """Применение градусов из поля ввода"""
        try:
            degrees = float(self.wind_degrees_var.get())
            
            # Нормализуем градусы в диапазон 0-360
            degrees = degrees % 360
            if degrees < 0:
                degrees += 360
            
            # Обновляем направление ветра
            self.wind_direction = degrees
            
            # Обновляем отображение
            self.draw_wind_arrow()
            
            # Обновляем текстовое представление
            self.update_wind_direction_text()
            
            self.status_var.set(f"Направление ветра установлено на {degrees:.1f}°")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число градусов (0-360)")
    
    def update_wind_direction_text(self):
        """Обновление текстового представления направления ветра"""
        angle = self.wind_direction
        
        # Определяем направление
        directions = {
            (0, 22.5): "N (Север)",
            (22.5, 67.5): "NE (Северо-восток)",
            (67.5, 112.5): "E (Восток)",
            (112.5, 157.5): "SE (Юго-восток)",
            (157.5, 202.5): "S (Юг)",
            (202.5, 247.5): "SW (Юго-запад)",
            (247.5, 292.5): "W (Запад)",
            (292.5, 337.5): "NW (Северо-запад)",
            (337.5, 360): "N (Север)"
        }
        
        direction_text = ""
        for (low, high), text in directions.items():
            if low <= angle < high:
                direction_text = text
                break
        
        self.wind_direction_var.set(f"{angle:.1f}° ({direction_text})")
    
    def reset_wind(self):
        """Сброс параметров ветра"""
        self.wind_direction = 0
        self.wind_force_var.set("0")
        self.wind_drift_var.set("5")
        self.wind_degrees_var.set("0")
        self.draw_wind_arrow()
        self.update_wind_direction_text()
        self.status_var.set("Параметры ветра сброшены")
    
    def wind_example(self):
        """Пример параметров ветра"""
        self.wind_direction = 45  # NE
        self.wind_force_var.set("3")
        self.wind_drift_var.set("5")
        self.wind_degrees_var.set("45")
        self.draw_wind_arrow()
        self.update_wind_direction_text()
        self.status_var.set("Загружен пример: ветер 45° (NE), сила 3, коэффициент 5")
    
    def add_artillery(self):
        """Добавление новой артиллерийской установки"""
        if self.artillery_count >= 10:
            messagebox.showwarning("Ограничение", "Максимум 10 артиллерийских установок")
            return
        
        self.artillery_count += 1
        self.artillery_tree.insert('', 'end', values=(
            self.artillery_count,
            f"Артиллерия {self.artillery_count}",
            "0",
            "0"
        ))
        self.status_var.set(f"Добавлена артиллерийская установка №{self.artillery_count}")
    
    def delete_artillery(self):
        """Удаление выбранной артиллерии"""
        selected = self.artillery_tree.selection()
        if not selected:
            messagebox.showwarning("Выбор", "Выберите артиллерию для удаления")
            return
        
        for item in selected:
            self.artillery_tree.delete(item)
        
        # Обновляем номера
        items = self.artillery_tree.get_children()
        for i, item in enumerate(items, 1):
            values = list(self.artillery_tree.item(item)['values'])
            values[0] = i
            values[1] = f"Артиллерия {i}"
            self.artillery_tree.item(item, values=tuple(values))
        
        self.artillery_count = len(items)
        self.status_var.set(f"Удалена выбранная артиллерия. Осталось: {self.artillery_count}")
    
    def clear_artilleries(self):
        """Очистка всех артиллерий"""
        for item in self.artillery_tree.get_children():
            self.artillery_tree.delete(item)
        
        self.artillery_count = 0
        self.status_var.set("Все артиллерийские установки очищены")
    
    def load_artillery_example(self):
        """Загрузка примера артиллерий"""
        self.clear_artilleries()
        
        example_data = [
            (1, "Артиллерия 1", "45", "500"),
            (2, "Артиллерия 2", "90", "600"),
            (3, "Артиллерия 3", "135", "550"),
        ]
        
        for data in example_data:
            self.artillery_tree.insert('', 'end', values=data)
        
        self.artillery_count = 3
        self.status_var.set("Загружен пример: 3 артиллерийские установки")
    
    def add_chain_point(self):
        """Добавление новой точки в цепочку"""
        if self.chain_count >= 15:
            messagebox.showwarning("Ограничение", "Максимум 15 точек в цепочке")
            return
        
        self.chain_count += 1
        point_name = f"Точка {self.chain_count}"
        if self.chain_count == 1:
            point_name = "Первый наводчик"
        elif self.chain_count > 1:
            point_name = f"Наводчик {self.chain_count}"
        
        self.chain_tree.insert('', 'end', values=(
            self.chain_count,
            point_name,
            "0",
            "0"
        ))
        self.status_var.set(f"Добавлена точка в цепочку: {point_name}")
    
    def delete_chain_point(self):
        """Удаление выбранной точки цепочки"""
        selected = self.chain_tree.selection()
        if not selected:
            messagebox.showwarning("Выбор", "Выберите точку для удаления")
            return
        
        for item in selected:
            self.chain_tree.delete(item)
        
        # Обновляем номера
        items = self.chain_tree.get_children()
        self.chain_count = 0
        for item in items:
            self.chain_count += 1
            values = list(self.chain_tree.item(item)['values'])
            values[0] = self.chain_count
            if self.chain_count == 1:
                values[1] = "Первый наводчик"
            else:
                values[1] = f"Наводчик {self.chain_count}"
            self.chain_tree.item(item, values=tuple(values))
        
        self.status_var.set(f"Удалена выбранная точка. Осталось: {self.chain_count}")
    
    def clear_chain(self):
        """Очистка цепочки"""
        for item in self.chain_tree.get_children():
            self.chain_tree.delete(item)
        
        self.chain_count = 0
        self.status_var.set("Цепочка наводчиков очищена")
    
    def load_chain_example(self):
        """Загрузка примера цепочки"""
        self.clear_chain()
        
        example_data = [
            (1, "Первый наводчик", "60", "200"),
            (2, "Наводчик 2", "120", "150"),
            (3, "Наводчик 3", "180", "100"),
            (4, "ЦЕЛЬ", "", ""),
        ]
        
        for data in example_data:
            self.chain_tree.insert('', 'end', values=data)
        
        self.chain_count = 4
        self.status_var.set("Загружен пример: цепочка из 3 наводчиков и цели")
    
    def calculate_chain_to_target(self):
        """Расчет положения цели относительно первого наводчика"""
        chain_data = []
        
        # Собираем данные цепочки
        for item in self.chain_tree.get_children():
            values = self.chain_tree.item(item)['values']
            if len(values) >= 4:
                try:
                    azim_str = str(values[2]).strip()
                    dist_str = str(values[3]).strip()
                    
                    if azim_str and dist_str:
                        azim = float(azim_str)
                        dist = float(dist_str)
                        chain_data.append((azim, dist))
                    else:
                        # Если нет данных для этой точки, значит это последняя (цель)
                        break
                except ValueError:
                    break
        
        if not chain_data:
            raise ValueError("Нет данных в цепочке наводчиков!")
        
        # Начальная точка (первый наводчик) в (0, 0)
        current_x, current_y = 0, 0
        
        # Рассчитываем цепочку
        for azim, dist in chain_data:
            # Азимут в компасной системе (0° = север, 90° = восток)
            # Переводим в математическую систему (0° = вправо, 90° = вверх)
            math_azim = math.radians(90 - azim)
            
            # Рассчитываем приращение координат
            dx = dist * math.cos(math_azim)
            dy = dist * math.sin(math_azim)
            
            # Обновляем текущие координаты
            current_x += dx
            current_y += dy
        
        # Возвращаем координаты цели относительно первого наводчика
        return current_x, current_y
    
    def calculate_for_artillery(self, art_azim: float, art_dist: float, 
                               target_x: float, target_y: float) -> Tuple[float, float]:
        """Расчет азимута и дистанции от артиллерии до цели"""
        
        # Координаты артиллерии относительно первого наводчика
        # Наводчик видит артиллерию под азимутом art_azim (компасная система)
        # Это направление ОТ наводчика К артиллерии
        # Нам нужно направление ОТ артиллерии К наводчику = art_azim + 180°
        reverse_azim = (art_azim + 180) % 360
        
        # Переводим в математическую систему
        math_reverse_azim = math.radians(90 - reverse_azim)
        
        # Координаты артиллерии относительно наводчика
        art_x = art_dist * math.cos(math_reverse_azim)
        art_y = art_dist * math.sin(math_reverse_azim)
        
        # Вектор от артиллерии к цели
        dx = target_x - art_x
        dy = target_y - art_y
        
        # Дистанция
        distance = math.sqrt(dx**2 + dy**2)
        
        # Азимут в математической системе
        azimuth_rad = math.atan2(dy, dx)
        azimuth_deg = math.degrees(azimuth_rad)
        
        # Переводим в компасную систему
        compass_azimuth = (90 - azimuth_deg) % 360
        
        return compass_azimuth, distance, (art_x, art_y)
    
    def apply_wind_correction(self, target_x: float, target_y: float) -> Tuple[float, float]:
        """Применение коррекции на ветер"""
        try:
            wind_force = int(self.wind_force_var.get())
            wind_drift = float(self.wind_drift_var.get())
            
            if wind_force == 0:
                return target_x, target_y
            
            # Вычисляем смещение от ветра
            wind_offset = wind_force * wind_drift
            
            # Направление ветра в математической системе
            math_wind_dir = math.radians(90 - self.wind_direction)
            
            # Смещаем цель в направлении ветра
            target_x_corrected = target_x + wind_offset * math.cos(math_wind_dir)
            target_y_corrected = target_y + wind_offset * math.sin(math_wind_dir)
            
            return target_x_corrected, target_y_corrected
            
        except ValueError:
            return target_x, target_y
    
    def calculate_all(self):
        """Основной расчет для всех артиллерий"""
        try:
            # Проверяем наличие данных
            if self.artillery_count == 0:
                messagebox.showerror("Ошибка", "Нет данных об артиллерийских установках!")
                return
            
            if self.chain_count == 0:
                messagebox.showerror("Ошибка", "Нет данных о цепочке наводчиков!")
                return
            
            # Собираем данные артиллерий
            artillery_data = []
            for item in self.artillery_tree.get_children():
                values = self.artillery_tree.item(item)['values']
                if len(values) >= 4:
                    try:
                        azim_str = str(values[2]).strip()
                        dist_str = str(values[3]).strip()
                        
                        if azim_str and dist_str:
                            azim = float(azim_str)
                            dist = float(dist_str)
                            artillery_data.append({
                                'num': values[0],
                                'name': values[1],
                                'azim': azim,
                                'dist': dist
                            })
                    except ValueError as e:
                        messagebox.showerror("Ошибка", 
                                           f"Ошибка в данных артиллерии {values[1]}: {str(e)}")
                        return
            
            if not artillery_data:
                messagebox.showerror("Ошибка", "Нет корректных данных об артиллерийских установках!")
                return
            
            # Рассчитываем положение цели
            target_x, target_y = self.calculate_chain_to_target()
            
            # Применяем коррекцию на ветер
            wind_force = int(self.wind_force_var.get())
            wind_drift = float(self.wind_drift_var.get())
            wind_offset = wind_force * wind_drift
            
            target_x_original, target_y_original = target_x, target_y
            target_x, target_y = self.apply_wind_correction(target_x, target_y)
            
            # Рассчитываем для каждой артиллерии
            self.results = []
            results_text = "=" * 80 + "\n"
            results_text += "РАСЧЕТ СТРЕЛЬБЫ ДЛЯ АРТИЛЛЕРИЙСКИХ УСТАНОВОК\n"
            results_text += "=" * 80 + "\n\n"
            
            # СВОДКА ДЛЯ БЫСТРОГО ИСПОЛЬЗОВАНИЯ (вверху)
            results_text += "СВОДКА ДЛЯ БЫСТРОГО ИСПОЛЬЗОВАНИЯ:\n"
            results_text += "-" * 80 + "\n"
            
            summary_results = []
            for i, art in enumerate(artillery_data, 1):
                azimuth, distance, art_coords = self.calculate_for_artillery(
                    art['azim'], art['dist'], target_x, target_y
                )
                
                self.results.append({
                    'artillery': art['name'],
                    'azimuth': azimuth,
                    'distance': distance
                })
                
                summary_results.append(f"{art['name']}: Азимут {azimuth:.2f}°, Дистанция {distance:.1f} м")
            
            # Выводим сводку
            for result in summary_results:
                results_text += result + "\n"
            
            results_text += "\n" + "=" * 80 + "\n"
            results_text += "ДЕТАЛЬНЫЕ РАСЧЕТЫ:\n"
            results_text += "=" * 80 + "\n\n"
            
            # Информация о ветре
            results_text += f"ПАРАМЕТРЫ ВЕТРА:\n"
            results_text += f"  Направление: {self.wind_direction:.1f}°\n"
            results_text += f"  Сила ветра: {wind_force}\n"
            results_text += f"  Коэффициент сноса: {wind_drift} м/ед.силы\n"
            results_text += f"  Смещение от ветра: {wind_offset} м\n\n"
            
            results_text += f"Координаты цели относительно первого наводчика:\n"
            results_text += f"  Без учета ветра: X = {target_x_original:.1f} м, Y = {target_y_original:.1f} м\n"
            results_text += f"  С учетом ветра: X = {target_x:.1f} м, Y = {target_y:.1f} м\n"
            results_text += f"  Дистанция от первого наводчика до цели: {math.sqrt(target_x**2 + target_y**2):.1f} м\n\n"
            
            results_text += "-" * 80 + "\n"
            results_text += "РАСЧЕТ ДЛЯ КАЖДОЙ АРТИЛЛЕРИИ:\n"
            results_text += "-" * 80 + "\n\n"
            
            for i, art in enumerate(artillery_data, 1):
                azimuth, distance, art_coords = self.calculate_for_artillery(
                    art['azim'], art['dist'], target_x, target_y
                )
                
                results_text += f"{art['num']}. {art['name']}:\n"
                results_text += f"   Исходные данные от наводчика:\n"
                results_text += f"     Азимут на артиллерию: {art['azim']:.1f}°\n"
                results_text += f"     Дистанция до артиллерии: {art['dist']:.0f} м\n"
                results_text += f"   Координаты артиллерии относительно наводчика:\n"
                results_text += f"     X = {art_coords[0]:.1f} м, Y = {art_coords[1]:.1f} м\n"
                results_text += f"   Данные для стрельбы на цель:\n"
                results_text += f"     Азимут на цель: {azimuth:.2f}°\n"
                results_text += f"     Дистанция до цели: {distance:.1f} м\n"
                results_text += "-" * 60 + "\n\n"
            
            # Обновляем текстовое поле
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, results_text)
            
            # Переключаемся на вкладку результатов
            self.notebook.select(3)  # Индекс 3 - вкладка результатов
            
            # Обновляем статус
            self.status_var.set(f"Расчет завершен! Обработано {len(artillery_data)} артиллерийских установок")
            
        except ValueError as e:
            messagebox.showerror("Ошибка расчета", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при расчете: {str(e)}")
    
    def copy_results(self):
        """Копирование результатов в буфер обмена"""
        results = self.results_text.get(1.0, tk.END).strip()
        if results:
            self.root.clipboard_clear()
            self.root.clipboard_append(results)
            self.status_var.set("Результаты скопированы в буфер обмена")
        else:
            messagebox.showwarning("Копирование", "Нет результатов для копирования")
    
    def clear_results(self):
        """Очистка результатов"""
        self.results_text.delete(1.0, tk.END)
        self.results = []
        self.status_var.set("Результаты очищены")
    
    def export_results(self):
        """Экспорт результатов в файл"""
        results = self.results_text.get(1.0, tk.END).strip()
        if not results:
            messagebox.showwarning("Экспорт", "Нет результатов для экспорта")
            return
        
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(results)
                
                self.status_var.set(f"Результаты экспортированы в файл: {filename}")
                messagebox.showinfo("Экспорт", "Результаты успешно экспортированы!")
                
        except Exception as e:
            messagebox.showerror("Ошибка экспорта", f"Ошибка при экспорте: {str(e)}")


def main():
    root = tk.Tk()
    app = MultiArtilleryCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()