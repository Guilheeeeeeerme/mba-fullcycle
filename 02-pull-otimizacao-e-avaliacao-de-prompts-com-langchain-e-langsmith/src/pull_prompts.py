"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()


def _extract_template_text(message) -> str:
    """
    Extrai o texto de template de uma mensagem de um ChatPromptTemplate.

    Mensagens de um ChatPromptTemplate (ex: SystemMessagePromptTemplate,
    HumanMessagePromptTemplate) guardam o texto dentro de `.prompt.template`.
    Este helper é defensivo para lidar com pequenas variações de formato
    entre versões do LangChain.
    """
    if hasattr(message, "prompt") and hasattr(message.prompt, "template"):
        return message.prompt.template
    if hasattr(message, "content"):
        return message.content
    return str(message)


def pull_prompts_from_langsmith():
    """
    Conecta ao LangSmith, faz pull do prompt de baixa qualidade
    'leonanluppi/bug_to_user_story_v1' e salva localmente em YAML.
    """
    prompt_name = "leonanluppi/bug_to_user_story_v1"
    output_path = "prompts/bug_to_user_story_v1.yml"

    print(f"Puxando prompt '{prompt_name}' do LangSmith Hub...")
    prompt = hub.pull(prompt_name)
    print("   ✓ Prompt puxado com sucesso")

    system_prompt = ""
    user_prompt = ""

    # ChatPromptTemplate.messages é uma lista de *MessagePromptTemplate
    for message in getattr(prompt, "messages", []):
        role = message.__class__.__name__.lower()
        text = _extract_template_text(message)

        if "system" in role:
            system_prompt = text
        elif "human" in role:
            user_prompt = text

    if not system_prompt and not user_prompt:
        # Fallback: prompt pode não ser um ChatPromptTemplate tradicional
        print("   ⚠️  Não foi possível separar system/user prompt automaticamente.")
        print("       Salvando representação bruta do prompt.")
        system_prompt = str(prompt)

    prompt_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt or "{bug_report}",
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    print(f"Salvando prompt em '{output_path}'...")
    success = save_yaml(prompt_data, output_path)

    if not success:
        raise RuntimeError(f"Falha ao salvar o prompt em '{output_path}'")

    print(f"   ✓ Prompt salvo com sucesso em '{output_path}'")
    return prompt_data


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    try:
        pull_prompts_from_langsmith()
    except Exception as e:
        print(f"\n❌ Falha ao puxar o prompt do LangSmith: {e}")
        print("\nVerifique:")
        print("  - LANGSMITH_API_KEY está configurada corretamente no .env")
        print("  - Você tem acesso ao workspace do LangSmith")
        print("  - Sua conexão com a internet está funcionando")
        return 1

    print("\n✅ Pull concluído com sucesso!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
