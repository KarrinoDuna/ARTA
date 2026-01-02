import time
from pynput import mouse, keyboard
from pynput.keyboard import Key, KeyCode

# --- УНИКАЛЬНЫЕ КОДЫ ДЛЯ ВАШЕЙ СИСТЕМЫ ---
LEFT_MOUSE_BUTTON = (4, 2, 0)          # Левая кнопка мыши (ЛКМ)
RIGHT_MOUSE_BUTTON = (16, 8, 1)        # Правая кнопка мыши (ПКМ)
SIDE_BUTTON_CODE = (256, 128, 2)       # Дальняя боковая кнопка (автокликер)
SIDE_BUTTON_CODE_NEAR = (256, 128, 1)  # Ближняя боковая кнопка (SHIFT + ДВОЙНОЙ КЛИК)
# ------------------------------------------

clicking = False
current_movement_key = None  # Какая клавиша сейчас зажата: 'w' или 'ц'
mouse_controller = mouse.Controller()
keyboard_controller = keyboard.Controller()

# Словарь для раскладок: тильда -> клавиша для зажатия
LAYOUT_KEYS = {
    '`': 'w',     # Английская раскладка: ` -> W
    'ё': 'ц',     # Русская раскладка: ё -> Ц (W в русской раскладке)
}

# Клавиши, которые отменяют тильду и нажимаются вместо неё
CANCEL_KEYS_EN = ['s', 'e', 'q']      # Английская раскладка
CANCEL_KEYS_RU = ['ы', 'у', 'й']      # Русская раскладка (S, E, Q)

def on_click(x, y, button, pressed):
    global clicking
    
    # Получаем значение кнопки
    button_code = None
    if hasattr(button, 'value'):
        button_code = button.value

    # ДИАГНОСТИКА: Нажатие любой кнопки мыши
    if pressed:
        print(f"Нажата кнопка мыши. Код: {button_code}")
    else:
        print(f"Отпущена кнопка мыши. Код: {button_code}")

    # --- ЛОГИКА ДЛЯ ДАЛЬНЕЙ БОКОВОЙ КНОПКИ (автокликер) ---
    if button_code == SIDE_BUTTON_CODE and pressed:
        if not clicking:
            # ЗАЖАТЬ ЛЕВУЮ КНОПКУ МЫШИ (код (4, 2, 0))
            mouse_controller.press(mouse.Button.left)
            clicking = True
            print(">>> [LMB] ЗАЖАТА (Hold) - Активировано!")
        else:
            # ОТПУСТИТЬ ЛЕВУЮ КНОПКУ МЫШИ
            mouse_controller.release(mouse.Button.left)
            clicking = False
            print(">>> [LMB] ОТПУЩЕНА Ф (Release) - Деактивировано.")
    
    # --- ЛОГИКА ДЛЯ БЛИЖНЕЙ БОКОВОЙ КНОПКИ (SHIFT + ДВОЙНОЙ КЛИК) ---
    elif button_code == SIDE_BUTTON_CODE_NEAR and pressed:
        # Зажимаем SHIFT
        keyboard_controller.press(Key.shift)
        print(">>> [SHIFT] ЗАЖАТ")
        
        # Минимальная задержка для стабильности`w`
        time.sleep(0.01)
        
        # Делаем двойной клик ЛКМ
        print(">>> Выполнение SHIFT + ДВОЙНОЙ КЛИК ЛКМ")
        
        # Первый клик
        mouse_controller.press(mouse.Button.left)
        time.sleep(0.05)  # Задержка между нажатием и отпусканием
        mouse_controller.release(mouse.Button.left)
        
        time.sleep(0.05)  # Пауза между кликами
        
        # Второй клик
        mouse_controller.press(mouse.Button.left)
        time.sleep(0.05)  # Задержка между нажатием и отпусканием
        mouse_controller.release(mouse.Button.left)
        
        # Отпускаем SHIFT
        keyboard_controller.release(Key.shift)
        print(">>> [SHIFT] ОТПУЩЕН")
        print(">>> [ДВОЙНОЙ КЛИК] выполнен!")

def release_movement_key():
    global current_movement_key
    if current_movement_key:
        keyboard_controller.release(current_movement_key)
        print(f">>> [{current_movement_key.upper()}] ОТПУЩЕНА (отмена)")
        current_movement_key = None

def toggle_movement_key(tilde_char):
    global current_movement_key
    
    if current_movement_key is None:
        # Зажимаем нужную клавишу в зависимости от раскладки
        key_to_press = LAYOUT_KEYS.get(tilde_char, 'w')
        keyboard_controller.press(key_to_press)
        current_movement_key = key_to_press
        print(f">>> [{key_to_press.upper()}] ЗАЖАТА (Hold) - Активировано! (Раскладка: {'английская' if tilde_char == '`' else 'русская'})")
    else:
        # Отпускаем ту клавишу, которую нажали
        release_movement_key()

def on_press(key):
    global current_movement_key
    
    # ВЫВОДИМ ПОДРОБНУЮ ИНФОРМАЦИЮ О КЛАВИШЕ
    try:
        # Получаем разные атрибуты клавиши
        if hasattr(key, 'char') and key.char:
            key_char = key.char
            print(f"Нажата клавиша с символом: '{key_char}' (char)")
            
            # Проверяем на тильду (английская или русская)
            if key_char in ['ё', '`']:
                print(f"--- ТИЛЬДА ОБНАРУЖЕНА: '{key_char}' ---")
                toggle_movement_key(key_char)
                # Не блокируем клавишу, пусть обрабатывается дальше
                return
            
            # Проверяем на клавиши отмены S, E, Q (или их русские аналоги)
            if key_char.lower() in CANCEL_KEYS_EN or key_char.lower() in CANCEL_KEYS_RU:
                print(f"--- КЛАВИША ОТМЕНЫ: '{key_char}' ---")
                
                # Если тильда активна - отжимаем её
                if current_movement_key:
                    release_movement_key()
                
                # Саму клавишу S/E/Q программа не нажимает - она нажимается естественным образом
                # Просто пропускаем дальше
                return
                
        else:
            print(f"Нажата клавиша: {key}")
            
    except Exception as e:
        print(f"Ошибка при обработке клавиши: {e}")

def on_release(key):
    # ВЫВОДИМ ОТПУЩЕННУЮ КЛАВИШУ ДЛЯ ДИАГНОСТИКИ
    try:
        if hasattr(key, 'char') and key.char:
            print(f"Отпущена клавиша: '{key.char}'")
        else:
            print(f"Отпущена клавиша: {key}")
    except:
        print(f"Отпущена клавиша: {key}")

print("=== АВТОКЛИКЕР ЗАПУЩЕН ===")
print("=== РАСШИФРОВКА КОДОВ КНОПОК МЫШИ ===")
print(f"Левая кнопка мыши (ЛКМ): {LEFT_MOUSE_BUTTON}")
print(f"Правая кнопка мыши (ПКМ): {RIGHT_MOUSE_BUTTON}")
print(f"Боковая ближняя кнопка: {SIDE_BUTTON_CODE_NEAR}")
print(f"Боковая дальняя кнопка: {SIDE_BUTTON_CODE}")
print("======================================")
print("1. Нажмите БОКОВУЮ КНОПКУ (Код: 256, 128, 2) для зажатия/отпускания ЛКМ (автокликер).")
print("2. Нажмите БОКОВУЮ КНОПКУ (Код: 256, 128, 1) для нажатия SHIFT + ДВОЙНОЙ КЛИК ЛКМ.")
print("3. Нажмите КЛАВИШУ 'Ё' (русская) или '`' (английская) для зажатия/отпускания W/Ц.")
print("4. Нажмите S, E или Q (или их русские аналоги) для отмены тильды.")
print("---------------------------------------")
print("ФУНКЦИИ:")
print(f"  - Кнопка {SIDE_BUTTON_CODE} → тумблер ЛКМ (включить/выключить)")
print(f"  - Кнопка {SIDE_BUTTON_CODE_NEAR} → SHIFT + ДВОЙНОЙ КЛИК ЛКМ")
print("  - В английской раскладке: ` → зажимает W")
print("  - В русской раскладке: ё → зажимает Ц")
print("  - S/E/Q (или С/У/Й) → отменяют тильду")
print("---------------------------------------")
print("Для остановки программы закройте это окно или нажмите Ctrl+C в терминале.")

# Запускаем оба слушателя
with mouse.Listener(on_click=on_click) as mouse_listener, \
     keyboard.Listener(on_press=on_press, on_release=on_release) as keyboard_listener:
    
    try:
        mouse_listener.join()
        keyboard_listener.join()
    except KeyboardInterrupt:
        print("\n--- Программа остановлена пользователем ---")
        # Отпускаем кнопки при выходе
        if clicking:
            mouse_controller.release(mouse.Button.left)
            print(">>> [LMB] ОТПУЩЕНА (при выходе)")
        if current_movement_key:
            release_movement_key()      