"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

from langchain import hub
from utils import (
    PROJECT_ROOT,
    check_env_vars,
    load_project_env,
    print_section_header,
    save_yaml,
)

load_project_env()

DEFAULT_PROMPT = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"


def _extract_template_text(message) -> str:
    """
    Extrai o texto de template de uma mensagem de um ChatPromptTemplate.
    """
    if hasattr(message, "prompt") and hasattr(message.prompt, "template"):
        return message.prompt.template
    if hasattr(message, "content"):
        return message.content
    return str(message)


def _extract_from_chat_prompt(prompt) -> Tuple[str, str]:
    system_prompt = ""
    user_prompt = ""

    for message in getattr(prompt, "messages", []):
        role = message.__class__.__name__.lower()
        text = _extract_template_text(message)

        if "system" in role:
            system_prompt = text
        elif "human" in role:
            user_prompt = text

    return system_prompt, user_prompt


def _extract_from_manifest(manifest: dict) -> Tuple[str, str]:
    """Extrai system/user templates do JSON retornado pelo CLI/API."""
    system_prompt = ""
    user_prompt = ""
    messages = (
        manifest.get("kwargs", {}).get("messages")
        or manifest.get("messages")
        or []
    )

    for message in messages:
        ids = message.get("id") or []
        class_name = str(ids[-1]).lower() if ids else ""
        template = (
            message.get("kwargs", {})
            .get("prompt", {})
            .get("kwargs", {})
            .get("template", "")
        )
        if "system" in class_name:
            system_prompt = template
        elif "human" in class_name:
            user_prompt = template

    return system_prompt, user_prompt


def _find_langsmith_cli() -> Optional[str]:
    """Prefere o CLI oficial (Go) em ~/.local/bin; evita o binário docker do venv."""
    candidates = [
        Path.home() / ".local" / "bin" / "langsmith",
        Path("/usr/local/bin/langsmith"),
    ]
    for path in candidates:
        if path.is_file() and os.access(path, os.X_OK):
            # Confirma que é o CLI novo (tem subcomando api / --version)
            try:
                result = subprocess.run(
                    [str(path), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0 and "version" in (result.stdout + result.stderr).lower():
                    return str(path)
            except (OSError, subprocess.SubprocessError):
                continue

    which = shutil.which("langsmith")
    if which and "venv" not in which:
        return which
    return None


def pull_via_sdk(prompt_name: str):
    api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
    api_url = os.getenv("LANGSMITH_ENDPOINT") or os.getenv("LANGCHAIN_ENDPOINT")
    return hub.pull(prompt_name, api_key=api_key, api_url=api_url)


def pull_via_cli(prompt_name: str) -> Tuple[str, str]:
    cli = _find_langsmith_cli()
    if not cli:
        raise RuntimeError(
            "CLI oficial do LangSmith não encontrado em ~/.local/bin/langsmith.\n"
            "Instale com: curl -fsSL https://cli.langsmith.com/install.sh | sh"
        )

    api_key = os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")
    endpoint = os.getenv("LANGSMITH_ENDPOINT") or os.getenv("LANGCHAIN_ENDPOINT") or ""
    env = os.environ.copy()
    if api_key:
        env["LANGSMITH_API_KEY"] = api_key
        env["LANGCHAIN_API_KEY"] = api_key
    if endpoint:
        env["LANGSMITH_ENDPOINT"] = endpoint

    cmd = [cli, "api", f"commits/{prompt_name}/latest"]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        cwd=str(PROJECT_ROOT),
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"CLI falhou ({result.returncode}): {result.stderr.strip() or result.stdout.strip()}"
        )

    payload = json.loads(result.stdout)
    manifest = payload.get("manifest") or payload
    return _extract_from_manifest(manifest)


def pull_prompts_from_langsmith():
    """
    Conecta ao LangSmith, faz pull do prompt de baixa qualidade
    e salva localmente em YAML. Tenta SDK e, se 403/erro, usa CLI oficial.
    """
    prompt_name = os.getenv("PULL_PROMPT_NAME", DEFAULT_PROMPT)
    output_path = OUTPUT_PATH

    print(f"Puxando prompt '{prompt_name}' do LangSmith Hub...")

    system_prompt = ""
    user_prompt = ""
    errors = []

    try:
        prompt = pull_via_sdk(prompt_name)
        system_prompt, user_prompt = _extract_from_chat_prompt(prompt)
        print("   ✓ Prompt puxado via SDK (hub.pull)")
    except Exception as sdk_error:
        errors.append(f"SDK: {sdk_error}")
        print(f"   ⚠️  SDK falhou: {sdk_error}")
        print("   Tentando fallback via LangSmith CLI...")
        try:
            system_prompt, user_prompt = pull_via_cli(prompt_name)
            print("   ✓ Prompt puxado via CLI")
        except Exception as cli_error:
            errors.append(f"CLI: {cli_error}")
            raise RuntimeError(
                "Falha no pull via SDK e CLI.\n" + "\n".join(errors)
            ) from cli_error

    if not system_prompt and not user_prompt:
        print("   ⚠️  Não foi possível separar system/user prompt automaticamente.")
        raise RuntimeError("Prompt vazio após pull")

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
    load_project_env(override=True)

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    key = os.getenv("LANGSMITH_API_KEY", "")
    print(f"API key carregada: sim (len={len(key)})")
    print(f".env: {PROJECT_ROOT / '.env'}")

    try:
        pull_prompts_from_langsmith()
    except Exception as e:
        print(f"\n❌ Falha ao puxar o prompt do LangSmith: {e}")
        print("\nVerifique:")
        print("  - LANGSMITH_API_KEY está configurada corretamente no .env")
        print("  - Você tem acesso ao workspace do LangSmith")
        print("  - CLI oficial: ~/.local/bin/langsmith (não o do venv)")
        print("  - Sua conexão com a internet está funcionando")
        return 1

    print("\n✅ Pull concluído com sucesso!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
