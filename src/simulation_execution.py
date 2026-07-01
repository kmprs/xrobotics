from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict
import h5py


ErronousElement = list | None


class SimulationExecution:
    """
    Represents a single teleoperation simulation run of robocasa. 

    :param hdf5_path: Path to the robocasa HDF5 demonstration file.
    :type hdf5_path: Path
    :param scenario_data: Path to the JSON file that describes the composite task, atomic sub-tasks,
    and their individual completion flags.
    :type scenario_data: Path
    """

    def __init__(
        self,
        scenario_data: Path,
    ) -> None:
        self.__erronous_element: ErronousElement = None
        self.__scenario_data_path: Path = Path(scenario_data)
        self.__simulation_data: Dict[str, Any] = self.__load_scenario_data()
        self.__hdf5_path: Path = Path(self.__simulation_data["hdf5_path"])
        self.__video_path: Path = self.__simulation_data["video_path"]
        self.__hdf5_metadata: Dict[str, Any] = self.__load_hdf5_metadata()

        self.__check()

    @property
    def simulation_data(self) -> Dict[str, Any]:
        return self.__simulation_data

    @property
    def video_path(self) -> Path:
        return self.__video_path

    @property
    def erronous_element(self) -> ErronousElement:
        return self.__erronous_element

    def was_successful(self) -> bool:
        return self.__erronous_element is None


    def __load_scenario_data(self) -> Dict[str, Any]:
        if not self.__scenario_data_path.exists():
            raise FileNotFoundError(
                f"Scenario data file not found: {self.__scenario_data_path}"
            )
        with self.__scenario_data_path.open("r", encoding="utf-8") as fh:
            data: Dict[str, Any] = json.load(fh)

        self.__validate_scenario_schema(data)
        return data


    @staticmethod
    def __validate_scenario_schema(data: Dict[str, Any]) -> None:
        # TODO: define a json scheme and validate against it
        required = {"composite_task", "completed", "hdf5_path", "video_path", "atomic_tasks"}
        missing = required - data.keys()
        if missing:
            raise ValueError(
                f"Scenario JSON is missing required keys: {missing}"
            )
        if not isinstance(data["atomic_tasks"], dict):
            raise TypeError(
                f"'atomic_tasks' must be a JSON object; "
                f"got {type(data['atomic_tasks']).__name__}."
            )

    def __load_hdf5_metadata(self) -> Dict[str, Any]:
        if not self.__hdf5_path.exists():
            raise FileNotFoundError(
                f"HDF5 demonstration file not found: {self.__hdf5_path}"
            )

        metadata: Dict[str, Any] = {"demos": {}}

        with h5py.File(self.__hdf5_path, "r") as hf:
            if "data" not in hf:
                raise KeyError(
                    f"HDF5 file '{self.__hdf5_path}' has no 'data' group. "
                    "Is this a valid robocasa demonstration file?"
                )
            data_group = hf["data"]
            if not isinstance(data_group, h5py.Group):
                raise TypeError(
                    f"Expected 'data' to be an HDF5 Group; "
                    f"got {type(data_group).__name__}."
                )

            raw_env_args = data_group.attrs.get("env_args", "{}")
            try:
                metadata["env_args"] = json.loads(raw_env_args)
            except (json.JSONDecodeError, TypeError):
                metadata["env_args"] = {}

            demo_keys = [k for k in data_group.keys() if k.startswith("demo_")]
            metadata["n_demos"] = len(demo_keys)

            for demo_key in demo_keys:
                demo = data_group[demo_key]
                if not isinstance(demo, h5py.Group):
                    raise TypeError(
                        f"Expected demo '{demo_key}' to be an HDF5 Group; "
                        f"got {type(demo).__name__}."
                    )
                metadata["demos"][demo_key] = {
                    "num_samples": int(demo.attrs.get("num_samples", 0)),
                    "model_file":  demo.attrs.get("model_file", None),
                    "rewards":     self.__read_dataset(demo, "rewards"),
                    "dones":       self.__read_dataset(demo, "dones"),
                }
        return metadata

    def __check(self) -> None:
        # Stage 1 – top-level composite task completion
        if not self.__parse_bool(self.__simulation_data.get("completed", False)):
            self.__erronous_element = self.__locate_erroneous_task()
            return
 
        # Stage 2 – individual atomic task completion
        failed_task = self.__locate_erroneous_task()
        if failed_task is not None:
            self.__erronous_element = failed_task
 
    def __locate_erroneous_task(self) -> ErronousElement:
        atomic_tasks: Dict[str, Any] = self.__simulation_data.get("atomic_tasks", {})
 
        for task_name, task_info in atomic_tasks.items():
            if not self.__parse_bool(task_info.get("completed", False)):
                reason: str = task_info.get("reason", "No reason provided.")
                return [task_name, reason]
        return None

    @staticmethod
    def __read_dataset(group: h5py.Group, key: str) -> list:
        if key not in group:
            return []
        item = group[key]
        if not isinstance(item, h5py.Dataset):
            return []
        return item[:].tolist()

    @staticmethod
    def __parse_bool(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() == "true"
        return bool(value)

