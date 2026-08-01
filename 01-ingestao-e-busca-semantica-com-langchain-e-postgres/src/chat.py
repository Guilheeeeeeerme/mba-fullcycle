from search import answer_question


def main() -> None:
    print("Chat iniciado. Digite 'sair' para encerrar.")
    while True:
        try:
            question = input("\nFaça sua pergunta:\n\nPERGUNTA: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo!")
            break

        if question.lower() in {"sair", "exit", "quit"}:
            print("Até logo!")
            break
        if not question:
            continue

        try:
            print(f"RESPOSTA: {answer_question(question)}")
        except Exception as error:
            print(f"ERRO: {error}")


if __name__ == "__main__":
    main()
