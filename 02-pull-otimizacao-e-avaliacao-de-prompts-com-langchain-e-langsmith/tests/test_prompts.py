"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
V2_PATH = PROMPTS_DIR / "bug_to_user_story_v2.yml"


@pytest.fixture(scope="module")
def prompt_v2():
    """Carrega o prompt otimizado (v2) e retorna seu dicionário de dados."""
    data = load_prompts(V2_PATH)
    assert data, f"Não foi possível carregar {V2_PATH}"
    # O YAML tem uma única chave de topo, ex: "bug_to_user_story_v2"
    prompt_key = next(iter(data))
    return data[prompt_key]


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_v2):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_v2
        assert prompt_v2["system_prompt"].strip() != ""

    def test_prompt_has_role_definition(self, prompt_v2):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = prompt_v2["system_prompt"].lower()
        role_markers = ["você é um", "você é uma", "you are a", "you are an"]
        assert any(marker in system_prompt for marker in role_markers), (
            "O system_prompt não define uma persona/papel explícito "
            "(ex: 'Você é um Product Manager...')"
        )

    def test_prompt_mentions_format(self, prompt_v2):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_v2["system_prompt"].lower()
        format_markers = ["markdown", "como um", "eu quero", "para que", "user story"]
        assert any(marker in system_prompt for marker in format_markers), (
            "O system_prompt não menciona o formato Markdown nem o formato "
            "padrão de User Story (Como um... Eu quero... Para que...)"
        )

    def test_prompt_has_few_shot_examples(self, prompt_v2):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_v2["system_prompt"].lower()
        has_input_marker = "relato de bug" in system_prompt or "exemplo" in system_prompt
        has_output_marker = "resposta esperada" in system_prompt
        assert has_input_marker and has_output_marker, (
            "O system_prompt não contém exemplos claros de entrada/saída (Few-shot)"
        )

    def test_prompt_no_todos(self, prompt_v2):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        full_text = prompt_v2.get("system_prompt", "") + prompt_v2.get("user_prompt", "")
        assert "TODO" not in full_text
        assert "[TODO]" not in full_text

    def test_minimum_techniques(self, prompt_v2):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_v2.get("techniques_applied", [])
        assert len(techniques) >= 2, (
            f"Esperado no mínimo 2 técnicas em 'techniques_applied', "
            f"encontradas: {len(techniques)}"
        )
        # Checagem cruzada usando o validador central de utils.py
        is_valid, errors = validate_prompt_structure(prompt_v2)
        assert is_valid, f"validate_prompt_structure encontrou problemas: {errors}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])