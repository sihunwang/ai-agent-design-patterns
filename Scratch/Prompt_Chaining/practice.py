from utils import llm_call
from typing import List

def prompt_chain_workflow(initial_input: str, prompt_chain: List[str]) -> List[str]:
    response_chain = []
    response = initial_input

    for i, prompt in enumerate(prompt_chain, 1):
        print(f"\n========== {i} 단계 ==============\n")

        final_promt = f"""{promt}

응답 시 아래 내용을 