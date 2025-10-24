from pathlib import Path
from dynamicprompts.generators import RandomPromptGenerator
from dynamicprompts.wildcards.wildcard_manager import WildcardManager

wm = WildcardManager(Path("d:/dev/ai/lumi-wildcards/wildcards"))

generator = RandomPromptGenerator(wildcard_manager=wm)
prompt = """__std/xl/style/all__"""
generated_prompts = generator.generate(prompt, 100)
for p in generated_prompts:
    print(p)