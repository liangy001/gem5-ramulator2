import os
from typing import (
    List,
    Optional,
    Sequence,
    Tuple,
)

import yaml

import m5
from m5.objects import (
    AddrRange,
    MemCtrl,
    Port,
    Ramulator2,
)
from m5.util.convert import toMemorySize

from ...utils.override import overrides
from ..boards.abstract_board import AbstractBoard
from .abstract_memory_system import AbstractMemorySystem


def config_r2(mem_type: str, num_chnls: int) -> Tuple[str, str]:
    """
    This function creates a config file that will be used to create a memory
    controller of type Ramulator2. It stores the config file in ``/tmp/`` directory.

    :param mem_type: The name for the type of the memory to be configured.

    :param num_chnls: The number of channels to configure for the memory

    :returns: A tuple containing the output file and the output directory.
    """

    # TODO: We need a better solution to this. This hard-coding is not
    # an acceptable solution.
    ramualtor_2_dir = os.path.join(
        os.getcwd(),
        "ext",
        "ramulator2",
        "ramulator2",
    )

    print(ramualtor_2_dir)

    # ramualtor_2_dir = Path("/home/yue/gem5/ext/ramulator2/ramulator2")

    ramualtor_2_mem_configs = os.path.join(ramualtor_2_dir, "configs")

    input_file = os.path.join(ramualtor_2_mem_configs, "example.yaml")
    print("input_file:", input_file)

    # Run checks to ensure the `ext/Ramulator2` directory is present, contains
    # the configs directory, and the configuration file we require.
    if not os.path.isdir(ramualtor_2_dir):
        raise Exception(
            "The `ext/Ramulator2` directory cannot be found.\n"
            "Please navigate to `ext` and run:\n"
            "git clone git@github.com:CMU-SAFARI/ramulator2.git"
        )
    elif not os.path.isdir(ramualtor_2_mem_configs):
        raise Exception(
            "The `ext/Ramulator2/configs` directory cannot be found."
        )
    elif not os.path.isfile(input_file):
        raise Exception(
            "The configuration file '" + input_file + "' cannot  be found."
        )

    # new_config_file = "/tmp/" + mem_type + "_chnls" + str(num_chnls) + ".yaml"

    # new_config = None
    # with open(input_file, 'r') as f:
    #     new_config = yaml.safe_load(f)
    # f.close()

    # new_config["MemorySystem"]["DRAM"]["org"]["channel"] = num_chnls

    # with open(new_config_file, 'w', encoding='utf-8') as f:
    #     yaml.dump(data=new_config, stream=f, allow_unicode=True)
    # f.close()
    # return new_config_file, m5.options.outdir
    return input_file, m5.options.outdir


class Ramulator2MemCtrl(Ramulator2):
    """
    A Ramulator2 Memory Controller.

    The class serves as a SimObject object wrapper, utiliszing the Ramulator2
    configuratons.
    """

    def __init__(self, mem_name: str, num_chnls: int) -> None:
        """
        :param mem_name: The name of the type  of memory to be configured.
        :param num_chnls: The number of channels.
        """
        super().__init__()
        ini_path, outdir = config_r2(mem_name, num_chnls)
        self.config_path = ini_path
        self.output_dir = outdir


class SingleChannel(AbstractMemorySystem):
    """
    A Single Channel Memory system.
    """

    def __init__(self, mem_type: str, size: Optional[str]):
        """
        :param mem_name: The name of the type  of memory to be configured.
        :param num_chnls: The number of channels.
        """
        super().__init__()
        self.mem_ctrl = Ramulator2MemCtrl(mem_type, 1)
        self._size = toMemorySize(size)
        if not size:
            raise NotImplementedError(
                "Ramulator2 memory controller requires a size parameter."
            )

    @overrides(AbstractMemorySystem)
    def incorporate_memory(self, board: AbstractBoard) -> None:
        pass

    @overrides(AbstractMemorySystem)
    def get_mem_ports(self) -> Tuple[Sequence[AddrRange], Port]:
        return [(self.mem_ctrl.range, self.mem_ctrl.port)]

    @overrides(AbstractMemorySystem)
    def get_memory_controllers(self) -> List[MemCtrl]:
        return [self.mem_ctrl]

    @overrides(AbstractMemorySystem)
    def get_size(self) -> int:
        return self._size

    @overrides(AbstractMemorySystem)
    def set_memory_range(self, ranges: List[AddrRange]) -> None:
        if len(ranges) != 1 or ranges[0].size() != self._size:
            raise Exception(
                "Single channel Ramualtor memory controller requires a single "
                "range which matches the memory's size."
            )
        self.mem_ctrl.range = ranges[0]


# def SingleChannelDDR3_1600(
#     size: Optional[str] = "2048MB",
# ) -> SingleChannel:
#     """
#     A single channel DDR3_1600.

#     :param size: The size of the memory system. Default value of 2048MB.
#     """
#     return SingleChannel("DDR3_8Gb_x8_1600", size)


def SingleChannelDDR4_2400(size: Optional[str] = "1024MB") -> SingleChannel:
    """
    A single channel DDR3_2400.

    :param size: The size of the memory system. Default value of 1024MB.
    """
    return SingleChannel("DDR4_4Gb_x8_2400", size)


# def SingleChannelLPDDR3_1600(size: Optional[str] = "256MB") -> SingleChannel:
#     """
#     A single channel LPDDR3_1600.

#     :param size: The size of the memory system. Default value of 256MB.
#     """
#     return SingleChannel("LPDDR3_8Gb_x32_1600", size)


# def SingleChannelHBM(size: Optional[str] = "64MB") -> SingleChannel:
#     """
#     A single channel HBM.

#     :param size: The size of the memory system. Default value of 64MB.
#     """
#     return SingleChannel("HBM1_4Gb_x128", size)
