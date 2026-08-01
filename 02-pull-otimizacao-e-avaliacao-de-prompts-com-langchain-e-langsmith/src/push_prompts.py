"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, load_project_env

load_project_env()


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = ["description", "system_prompt", "user_prompt", "version"]
    for field in required_fields:
        if not prompt_data.get(field):
            errors.append(f"Campo obrigatório faltando ou vazio: '{field}'")

    system_prompt = prompt_data.get("system_prompt", "") or ""
    if "TODO" in system_prompt:
        errors.append("system_prompt ainda contém pendências (TODO)")

    techniques = prompt_data.get("techniques_applied", []) or []
    if len(techniques) < 2:
        errors.append(
            f"São necessárias no mínimo 2 técnicas em 'techniques_applied' "
            f"(encontradas: {len(techniques)})"
        )

    return (len(errors) == 0, errors)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt (ex: "meu_usuario/bug_to_user_story_v2")
        prompt_data: Dados do prompt (dict lido do YAML)

    Returns:
        True se sucesso, False caso contrário
    """
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print(f"❌ Prompt '{prompt_name}' inválido, push cancelado:")
        for error in errors:
            print(f"   - {error}")
        return False

    template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt_data["system_prompt"]),
            ("human", prompt_data["user_prompt"]),
        ]
    )

    techniques = prompt_data.get("techniques_applied", [])
    description = prompt_data.get("description", "")
    if techniques:
        description = f"{description} | Técnicas: {', '.join(techniques)}"

    try:
        url = hub.push(
            prompt_name,
            template,
            api_key=os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY"),
            api_url=os.getenv("LANGSMITH_ENDPOINT") or os.getenv("LANGCHAIN_ENDPOINT"),
            new_repo_is_public=True,
            new_repo_description=description,
            tags=prompt_data.get("tags", []),
        )
        print(f"   ✓ Push realizado com sucesso")
        print(f"   URL: {url}")
        return True
    except Exception as e:
        print(f"   ❌ Erro ao fazer push do prompt '{prompt_name}': {e}")
        return False


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS PARA O LANGSMITH HUB")
    load_project_env(override=True)

    if not check_env_vars(["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")
    input_path = "prompts/bug_to_user_story_v2.yml"

    data = load_yaml(input_path)
    if not data:
        print(f"❌ Não foi possível carregar '{input_path}'")
        return 1

    # O YAML tem uma única chave de topo (ex: "bug_to_user_story_v2")
    prompt_key = next(iter(data))
    prompt_data = data[prompt_key]

    prompt_name = f"{username}/bug_to_user_story_v2"

    print(f"Publicando prompt '{prompt_name}'...")
    success = push_prompt_to_langsmith(prompt_name, prompt_data)

    if not success:
        print("\n❌ Push falhou. Corrija os erros acima e tente novamente.")
        return 1

    print(f"\n✅ Prompt publicado com sucesso!")
    print(f"   Confira no dashboard: https://smith.langchain.com/prompts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
