import tkinter as tk
from tkinter import scrolledtext
from service import CAG
import threading

class CAGAssistantGUI:
    def __init__(self, master):
        # Инициализация GUI
        self.master = master
        # Создание экземпляра сервиса CAG
        self.service = CAG()
        master.title("CAG Assistant Test GUI")

        # Отступы для всего окна
        master.config(padx=10, pady=10)

        # Поле ввода запроса пользователя
        self.user_prompt_label = tk.Label(master, text="User Prompt:")
        self.user_prompt_label.pack(pady=(0, 5))  # Отступ снизу
        self.user_prompt_text = scrolledtext.ScrolledText(master, height=10, width=80)  # Уменьшенная высота
        self.user_prompt_text.pack(pady=(0, 10))  # Отступ снизу

        # Поле вывода ответа
        self.response_label = tk.Label(master, text="Response:")
        self.response_label.pack(pady=(0, 5))  # Отступ снизу
        self.response_text = scrolledtext.ScrolledText(master, height=15, width=80, state=tk.DISABLED)
        self.response_text.pack(pady=(0, 10))  # Отступ снизу

        # Кнопка отправки запроса
        self.submit_button = tk.Button(master, text="Submit Prompt", command=self.submit_prompt_threaded)
        self.submit_button.pack(pady=(5, 0))  # Отступ сверху
        self.dots = 0

    def submit_prompt_threaded(self):
        # Создание и запуск потока для отправки запроса
        thread = threading.Thread(target=self.submit_prompt)
        thread.start()

    def submit_prompt(self):
        # Получение запроса пользователя и удаление пробелов
        user_prompt = self.user_prompt_text.get("1.0", tk.END).strip()
        # Проверка на пустой запрос
        if not user_prompt or len(user_prompt) < 3:
            return  # Не отправлять пустой запрос

        # Блокировка кнопки отправки
        self.submit_button.config(state=tk.DISABLED)
        # Вывод "Typing..." в поле ответа
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete("1.0", tk.END)
        self.response_text.insert(tk.END, "Typing")
        self.response_text.config(state=tk.DISABLED)
        # Запуск анимации "Typing..."
        self.animate_loading()

        # Очистка поля ввода
        self.user_prompt_text.delete("1.0", tk.END)

        # Получение ответа от сервиса
        response = self.service.process_query(user_prompt)

        # Обновление поля ответа
        self.master.after_cancel(self.animation_id)  # Остановка анимации
        self.response_text.config(state=tk.NORMAL)  # Разблокировка поля
        self.response_text.delete("1.0", tk.END)  # Очистка поля
        self.response_text.insert(tk.END, response)  # Вставка ответа
        self.response_text.config(state=tk.DISABLED)  # Блокировка поля
        # Разблокировка кнопки отправки
        self.submit_button.config(state=tk.NORMAL)

    def animate_loading(self):
        # Анимация "Typing..."
        self.dots = (self.dots + 1) % 4
        loading_text = "Typing" + "." * self.dots
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete("1.0", tk.END)
        self.response_text.insert(tk.END, loading_text)
        self.response_text.config(state=tk.DISABLED)
        self.animation_id = self.master.after(250, self.animate_loading)  # Повтор анимации

if __name__ == "__main__":
    print("Launched")
    root = tk.Tk()
    app = CAGAssistantGUI(root)
    root.mainloop()