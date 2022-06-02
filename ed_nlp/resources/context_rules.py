
from medspacy.context import ConTextRule, ConTextComponent

context_rules = [ConTextRule(literal = "?", 
                    category="POSSIBLE_EXISTENCE", 
                    direction="BACKWARD", 
                    max_scope=1)]