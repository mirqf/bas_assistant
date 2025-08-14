from collections import deque
import os, openai, time, logging

os.environ["TOKENIZERS_PARALLELISM"] = "false"

client = openai.OpenAI(
    base_url = "https://openrouter.ai/api/v1",
    api_key = os.environ["OPENAI_API_KEY"]
)

logging.basicConfig(
    filename = "debug.txt",
    level = logging.DEBUG,
    format = "%(asctime)s [%(levelname)s] %(message)s",
)

class CAG:
    def __init__(self):
        # Путь к директории с базой знаний
        self.DATA_DIRECTORY = "./knowledge_base"
        # Максимальный размер контекстного окна
        self.PROMPT_WINDOW_LIMIT = 2e4
        # Максимальный размер кэша
        self.CACHE_SIZE_MAX = 1e4
        # Множитель для токенизатора
        self.TOKENIZER_MULTIPLYER = 1.0
        # Время жизни кэша в секундах
        self.CACHE_TIMEOUT = 900

        # Загрузка документов и формирование системного промпта
        self.system_prompt = '\n'.join(self._load_documents())
        # Текущий размер кэша
        self.global_cache_size = 0
        # Кэш запросов
        self.global_cache = deque()

    def _load_documents(self):
        # Загрузка документов из директории
        documents = list()
        context_win = 0

        for filename in os.listdir(self.DATA_DIRECTORY):
            if filename.endswith(".txt"):
                with open(os.path.join(self.DATA_DIRECTORY, filename), 'r', encoding = "utf-8") as file:
                    file_text = file.read()
                    context_win += len(file_text)
                
                    if context_win * self.TOKENIZER_MULTIPLYER > self.PROMPT_WINDOW_LIMIT:
                        raise RuntimeError("Превышен лимит контекстного окна: " + str(context_win))

                    documents.append(file_text)
        
        return documents
    
    def _cache_query(self, query: str, role: str):
        # Кэширование запроса
        query_size = len(query)
        while len(self.global_cache) > 0 and self.global_cache_size + query_size > self.CACHE_SIZE_MAX:
            self.global_cache_size -= len(self.global_cache.popleft())
        
        self.global_cache_size += query_size
        self.global_cache.append({"role": role, "text": query, "timestamp": time.time()})
    
    def _cache_access(self):
        # Проверка актуальности кэша
        if len(self.global_cache) == 0 or (self.global_cache[-1]["timestamp"] + self.CACHE_TIMEOUT < time.time()):
            self.global_cache_size = 0
            self.global_cache.clear()
            return "Context is empty"
        
        response = ""
        for item in self.global_cache:
            response += (item["role"] + ": " + item["text"] + '\n')
        
        return response


    def process_query(self, query: str):
        # Обработка запроса пользователя
        current_cach = self._cache_access()
        self._cache_query(query, "User")
        response = "Something went wrong on OpenRouter`s side ;("

        try:
            completion = client.chat.completions.create(
                extra_headers={},
                extra_body={},
                model="meta-llama/llama-3.3-70b-instruct:free",
                messages=[
                    {
                        "role": "system",
                        "content": [
                            {
                                "type": "text",
                                "text": "База знаний: " + self.system_prompt,
                            }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "История диалога: " + current_cach + "\nВопрос пользователя: " + query + "\n\nДЛЯ ОТВЕТА НА ВОПРОС ПОЛЬЗОВАТЕЛЯ ИСПОЛЬЗУЙ ТОЛЬКО ИНФОРМАЦИЮ ИЗ БАЗЫ ЗНАНИЙ. ЕСЛИ ТАМ НЕТ ОТВЕТА НА ВОПРОС, СКАЖИ, ЧТО НЕ МОЖЕШЬ ПОМОЧЬ. Отвечай на языке запроса пользователя"
                            }
                        ]
                    }
                ]
            )
            response = completion.choices[0].message.content
            self._cache_query(response , "Assistant")
        except Exception:
            pass

        return response