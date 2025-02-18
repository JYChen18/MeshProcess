import hydra
from func import *


@hydra.main(config_path="config", config_name="base", version_base=None)
def main(cfg):
    eval(f"func_{cfg.func_name}")(cfg)
    return


if __name__ == "__main__":
    main()
