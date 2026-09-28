# Ollama с уже скачанной моделью qwen2.5:7b.
# Ничего не нужно ставить на хост и загружать при первом запуске.
FROM ollama/ollama:latest

# Поднимаем сервер на время сборки образа, качаем модель и останавливаемся.
# Слой после этой команды содержит модель в /root/.ollama.
RUN ollama serve & \
    sleep 10 && \
    ollama pull qwen2.5:7b

ENV OLLAMA_HOST=0.0.0.0

EXPOSE 11434

# Стандартный CMD образа — `ollama serve`