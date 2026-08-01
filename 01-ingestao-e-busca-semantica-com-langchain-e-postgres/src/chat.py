import logging
import warnings

# Silencia avisos/logs de libs (FastEmbed, LangChain, etc.) no console do chat.
warnings.filterwarnings("ignore")
logging.disable(logging.WARNING)

from search import answer_question


def main() -> None:
    print("Chat iniciado. Digite 'sair' para encerrar.\n")
    while True:
        try:
            question = input("PERGUNTA: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo!")
            break

        if question.lower() in {"sair", "exit", "quit"}:
            print("Até logo!")
            break
        if not question:
            continue

        try:
            print(f"RESPOSTA: {answer_question(question)}\n")
        except Exception as error:
            print(f"ERRO: {error}\n")


if __name__ == "__main__":
    main()
