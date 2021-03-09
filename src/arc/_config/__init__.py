from arc.convert import converter_mapping
from .config import Config


config: Config = Config(
    namespace_sep=":",
    arg_assignment="=",
    flag_denoter="--",
    loglevel=30,
    converters=converter_mapping,
)
